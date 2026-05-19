from abc import ABC, abstractmethod
import json
import os
import asyncio
import time
from typing import AsyncGenerator, Tuple, List, Dict, Any
from app.core.logging import logger

class BaseProvider(ABC):
    """Lớp cơ sở trừu tượng cho tất cả các chatbot provider."""
    
    @abstractmethod
    async def generate_stream(self, message: str, model: str, session_id: str = None) -> Tuple[AsyncGenerator[str, None], str]:
        """
        Tạo một stream các phản hồi từ provider.
        
        Args:
            message: Tin nhắn đầu vào của user.
            model: Tên model mục tiêu.
            session_id: ID session tùy chọn để duy trì hội thoại.
            
        Returns:
            Một tuple gồm (AsyncGenerator trả về các text chunk, session_id mới).
        """
        pass

class MultiAccountProvider(BaseProvider):
    """Lớp cơ sở cho các provider hỗ trợ nhiều tài khoản và failover."""
    
    # Cấu trúc: {provider_name: {account_id: expiry_timestamp}}
    _global_failed_accounts: Dict[str, Dict[str, float]] = {}
    
    def __init__(self, provider_name: str, config_path: str = "config.json"):
        self.provider_name = provider_name
        self.config_path = config_path
        self._client = None
        self._auth_lock = asyncio.Lock()
        
        # Khởi tạo registry cho provider nếu chưa có
        if provider_name not in self._global_failed_accounts:
            self._global_failed_accounts[provider_name] = {}

    def _get_account_id(self, acc: Dict[str, Any]) -> str:
        """Lấy id của tài khoản."""
        return acc.get("email") or acc.get("identity_id") or \
               acc.get("device_uuid") or acc.get("id") or "unknown"

    def _mark_account_failed(self, account_data: Dict[str, Any], duration: int = 86400):
        """Đánh dấu tài khoản bị lỗi trong một khoảng thời gian (mặc định 24h)."""
        acc_id = self._get_account_id(account_data)
        if acc_id != "unknown":
            expiry = time.time() + duration
            self._global_failed_accounts[self.provider_name][acc_id] = expiry
            logger.warning(f"[!] Tài khoản {self.provider_name} ({acc_id}) bị đánh dấu lỗi. Sẽ bỏ qua trong {duration}s.")

    def _is_account_failed(self, account_data: Dict[str, Any]) -> bool:
        """Kiểm tra xem tài khoản có đang trong danh sách lỗi không."""
        acc_id = self._get_account_id(account_data)
        if acc_id == "unknown":
            return False
            
        failed_map = self._global_failed_accounts.get(self.provider_name, {})
        if acc_id in failed_map:
            if time.time() < failed_map[acc_id]:
                return True
            else:
                del failed_map[acc_id]
        return False

    def _load_accounts(self) -> List[Dict[str, Any]]:
        """Tải tất cả tài khoản và lọc bỏ những tài khoản đang bị lỗi."""
        accounts = []
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    provider_config = data.get("providers", {}).get(self.provider_name, [])
                    
                    if isinstance(provider_config, list):
                        accounts = provider_config
                    elif isinstance(provider_config, dict):
                        accounts = [provider_config]
            except Exception as e:
                logger.error(f"Lỗi khi tải danh sách tài khoản {self.provider_name}: {e}")
        
        valid_accounts = [acc for acc in accounts if not self._is_account_failed(acc)]
        
        if accounts and not valid_accounts:
            logger.warning(f"Tất cả tài khoản {self.provider_name} đều đang bị lỗi. Thử dùng lại để tránh gián đoạn.")
            self._global_failed_accounts[self.provider_name] = {}
            return accounts
            
        return valid_accounts

    @abstractmethod
    async def _setup_account(self, account_data: Dict[str, Any]) -> bool:
        """Thiết lập thông tin tài khoản cụ thể. Trả về True nếu thành công."""
        pass

    @abstractmethod
    async def _get_stream(self, message: str, model: str, session_id: str = None) -> AsyncGenerator[str, None]:
        """Thực hiện gọi API thực tế và trả về stream content."""
        pass

    async def generate_stream(self, message: str, model: str, session_id: str = None) -> Tuple[AsyncGenerator[str, None], str]:
        """Triển khai generate_stream với logic failover qua nhiều tài khoản."""
        accounts = self._load_accounts()
        
        if not accounts:
            logger.warning(f"Không tìm thấy tài khoản hợp lệ nào cho provider {self.provider_name}. Thử chạy với cấu hình mặc định.")
            return self._get_stream(message, model, session_id), session_id or "default"

        last_error = None
        for i, acc in enumerate(accounts):
            try:
                if not await self._setup_account(acc):
                    logger.warning(f"Tài khoản {self.provider_name} #{i+1} thiết lập thất bại, bỏ qua.")
                    self._mark_account_failed(acc, duration=3600) # Setup fail khóa 1h
                    continue

                logger.info(f"[*] Thử dùng tài khoản {self.provider_name} #{i+1}/{len(accounts)}")
                
                has_content = False
                
                current_acc = acc
                
                async def stream_wrapper():
                    nonlocal has_content
                    try:
                        async for chunk in self._get_stream(message, model, session_id):
                            has_content = True
                            yield chunk
                    except Exception as e:
                        logger.error(f"Lỗi trong khi stream với tài khoản {self.provider_name}: {e}")
                        if not has_content:
                            raise e
                        return

                wrapper_gen = stream_wrapper()
                try:
                    # Kiểm tra xem có chunk đầu tiên không
                    first_chunk = await wrapper_gen.__anext__()
                    has_content = True
                    
                    async def final_generator():
                        yield first_chunk
                        async for chunk in wrapper_gen:
                            yield chunk
                    
                    return final_generator(), self._get_current_session_id(session_id)
                except StopAsyncIteration:
                    self._mark_account_failed(acc)
                    raise Exception("API trả về response trống")
                except Exception as e:
                    logger.warning(f"Tài khoản {self.provider_name} #{i+1} thất bại khi khởi tạo stream: {e}. Đang thử tài khoản tiếp theo...")
                    self._mark_account_failed(acc)
                    last_error = e
                    continue

            except Exception as e:
                last_error = e
                continue

        error_msg = str(last_error) or f"Tất cả tài khoản {self.provider_name} đều thất bại"
        raise Exception(error_msg)

    def _get_current_session_id(self, default_id: str = None) -> str:
        """Trả về session ID hiện tại của provider. Có thể ghi đè bởi lớp con."""
        return default_id or "session"
