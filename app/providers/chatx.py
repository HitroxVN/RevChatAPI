"""Service ChatX để xử lý các lệnh gọi API backend tới chatx.ai bằng httpx."""
import httpx
import re
import json
import os
import time
import uuid
from typing import Tuple, AsyncGenerator, List, Dict, Any
from app.core.config import settings
from app.core.logging import logger
import asyncio
from app.providers.base import MultiAccountProvider

class ChatXProvider(MultiAccountProvider):
    def __init__(self):
        super().__init__(provider_name="chatx")
        self.base_url = "https://chatx.ai"
        self.csrf_token = None
        self.user_id = None
        self.chats_id = None
        self.auto_clear_history = False
        self.email = None
        self.password = None

    @property
    def client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{self.base_url}/deepseek"
                }
            )
        return self._client

    async def _setup_account(self, acc: Dict[str, Any]) -> bool:
        """Thiết lập thông tin tài khoản ChatX."""
        try:
            self.email = acc.get("email")
            self.password = acc.get("password")
            self.auto_clear_history = acc.get("auto_clear_history", False)
            
            # Reset client cookies for each account to avoid cross-contamination
            self.client.cookies.clear()
            if "cookies" in acc:
                for k, v in acc["cookies"].items():
                    self.client.cookies.set(k, v, domain="chatx.ai")
            
            # Reset tokens to force re-authentication for this account
            self.csrf_token = None
            self.user_id = None
            self.chats_id = None
            
            return True
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập tài khoản ChatX {self.email}: {e}")
            return False

    def _save_chatx_token(self):
        """Lưu cookies ChatX ngược lại vào config.json."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "providers" not in data:
                    data["providers"] = {}
                
                if "chatx" not in data["providers"]:
                    data["providers"]["chatx"] = []
                
                chatx_config = data["providers"]["chatx"]
                cookies_dict = {c.name: c.value for c in self.client.cookies.jar}
                
                if isinstance(chatx_config, list):
                    found = False
                    for acc in chatx_config:
                        if acc.get("email") == self.email:
                            acc["cookies"] = cookies_dict
                            acc["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                            found = True
                            break
                    
                    if not found and self.email:
                        # Thêm mới nếu chưa có
                        chatx_config.append({
                            "id": str(uuid.uuid4()),
                            "email": self.email,
                            "cookies": cookies_dict,
                            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S")
                        })
                elif isinstance(chatx_config, dict):
                    data["providers"]["chatx"]["cookies"] = cookies_dict
                    data["providers"]["chatx"]["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Lỗi khi lưu token ChatX: {e}")

    async def get_initial_token(self) -> bool:
        try:
            response = await self.client.get(f"{self.base_url}/deepseek", timeout=10.0)
            
            match = re.search(r'name="_token"\s+value="([^"]+)"', response.text)
            if not match:
                match = re.search(r'csrf-token"\s+content="([^"]+)"', response.text)
            if not match:
                match = re.search(r'<input type="hidden" name="_token" value="([^"]+)">', response.text)
            
            if match:
                self.csrf_token = match.group(1)
                self.client.headers.update({"X-CSRF-TOKEN": self.csrf_token})
            
            user_id_match = re.search(r"user_id['\"]?\s*[:=]\s*['\"]?(\d+)['\"]?", response.text)
            if user_id_match:
                self.user_id = user_id_match.group(1)
            else:
                self.user_id = self.client.cookies.get("chatx_guest_token")
            
            return self.csrf_token is not None
        except Exception as e:
            logger.error(f"Lỗi khi lấy token: {e}")
            return False

    async def login(self) -> bool:
        if not self.email or not self.password:
            return False

        if not self.csrf_token:
            await self.get_initial_token()
            
        logger.info(f"[*] Đang đăng nhập vào ChatX với email {self.email}...")
        payload = {
            "_token": self.csrf_token,
            "email": self.email,
            "password": self.password,
            "rememberme": "1"
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        try:
            response = await self.client.post(f"{self.base_url}/apilogin", data=payload, headers=headers, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" or "success" in data.get("message", "").lower():
                    await self.get_initial_token() 
                    self._save_chatx_token() 
                    return True
                else:
                    logger.warning(f"[-] Đăng nhập ChatX thất bại: {data.get('message')}")
        except Exception as e:
            logger.error(f"Lỗi đăng nhập: {e}")
        return False

    async def start_new_chat(self) -> bool:
        if not self.csrf_token or not self.user_id:
            await self.get_initial_token()

        payload = {
            "_token": self.csrf_token,
            "user_id": self.user_id,
            "is_manual": "1"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        try:
            response = await self.client.post(f"{self.base_url}/newchat", data=payload, headers=headers, timeout=10.0)
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.chats_id = data.get("chats_id") or data.get("id")
                except:
                    pass
                
                if not self.chats_id:
                    match = re.search(r"openconversions\(['\"](\d+)['\"]\)", response.text)
                    if not match:
                        match = re.search(r'chats_id="(\d+)"', response.text)
                    if match:
                        self.chats_id = match.group(1)
                
                return self.chats_id is not None
        except Exception as e:
            logger.error(f"Lỗi khi bắt đầu chat: {e}")
        return False

    async def clear_history(self):
        if not self.csrf_token or not self.user_id:
            await self.get_initial_token()
            
        payload = {
            "_token": self.csrf_token,
            "user_id": self.user_id
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        try:
            await self.client.post(f"{self.base_url}/clearconversion", data=payload, headers=headers, timeout=10.0)
            self.chats_id = None
        except:
            pass

    def _get_current_session_id(self, default_id: str = None) -> str:
        return f"chatx_{self.email}" if self.email else (default_id or "chatx_session")

    async def _get_stream(self, message: str, model: str, session_id: str = None) -> AsyncGenerator[str, None]:
        """Generator nội bộ trả về các response chunk một cách bất đồng bộ."""
        if "/" in model:
            model = model.split("/")[-1]
            
        if "claude" in model.lower() and model not in ["claude3", "claude2"]:
            model = "deepseek_flash"
            
        async with self._auth_lock:
            if not self.csrf_token or not self.user_id:
                await self.get_initial_token()
            
            self.chats_id = None
            
            if self.auto_clear_history:
                await self.clear_history()
            
            if not await self.start_new_chat():
                logger.info("[*] Không thể bắt đầu chat, đang thử đăng nhập...")
                if await self.login():
                    if not await self.start_new_chat():
                        raise Exception("Không thể bắt đầu session chat sau khi đăng nhập")
                else:
                    raise Exception("Xác thực ChatX thất bại")

        payload = {
            "_token": self.csrf_token,
            "user_id": self.user_id,
            "chats_id": self.chats_id,
            "prompt": message,
            "current_model": model,
            "is_web": "0",
            "is_youtube": "0"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        
        try:
            response = await self.client.post(f"{self.base_url}/sendchat", data=payload, headers=headers, timeout=30.0)
            if response.status_code != 200:
                raise Exception(f"ChatX /sendchat thất bại với trạng thái {response.status_code}. Response: {response.text}")
            
            data = response.json()
            if not data.get("response"):
                raise Exception(f"ChatX trả về lỗi: {data.get('message', 'Lỗi không xác định')}")

            conv_id = data.get("conversions_id")
            ass_conv_id = data.get("ass_conversions_id")
            
            if not conv_id or not ass_conv_id:
                raise Exception("Không thể khởi tạo hội thoại")
            
            stream_params = {
                "user_id": self.user_id,
                "chats_id": self.chats_id,
                "current_model": model,
                "conversions_id": conv_id,
                "ass_conversions_id": ass_conv_id,
                "is_web": "0",
                "is_youtube": "0"
            }
            
            # Sử dụng httpx stream
            raw_unparsed = []
            has_yielded = False
            
            async with self.client.stream("GET", f"{self.base_url}/chats_stream", params=stream_params, timeout=60.0) as stream_resp:
                stream_resp.raise_for_status()
                
                async for line in stream_resp.aiter_lines():
                    if line:
                        if line.startswith("data: "):
                            content = line[6:]
                            if content == "[DONE]":
                                break
                            try:
                                if content.strip() in ["end", "[DONE]", "done"]:
                                    continue
                                    
                                chunk_data = json.loads(content)
                                if chunk_data.get("type") == "response.output_text.delta":
                                    text_chunk = chunk_data.get("delta", "")
                                    # Lọc các thẻ DSML tool call sớm
                                    text_chunk = re.sub(r'<｜｜DSML｜｜.*?>', '', text_chunk, flags=re.DOTALL)
                                    if text_chunk:
                                        has_yielded = True
                                        yield text_chunk
                                elif chunk_data.get("type") == "response.end":
                                    break
                                else:
                                    raw_unparsed.append(content)
                            except json.JSONDecodeError:
                                raw_unparsed.append(content)
                            except Exception as e:
                                logger.error(f"[*] Lỗi khi parse stream chunk: {e}")
                                
            if not has_yielded:
                if raw_unparsed:
                    err_msg = " | ".join(raw_unparsed[:5])
                    raise Exception(f"ChatX trả về một response trống. Dữ liệu stream thô: {err_msg}")
                else:
                    raise Exception("Không có phản hồi từ ChatX (Stream trống hoặc kết nối bị đóng).")
                    
        except Exception as e:
            raise e


