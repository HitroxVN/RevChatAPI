import json
import time
import os
import asyncio
import httpx
import secrets
from typing import Tuple, AsyncGenerator, Dict, Any, List
from app.providers.base import BaseProvider, MultiAccountProvider
from app.core.config import settings
from app.core.logging import logger

class EaseMateProvider(MultiAccountProvider):
    def __init__(self):
        super().__init__(provider_name="easemate")
        self.base_dir = os.path.dirname(__file__)
        self.sign_js_path = os.path.join(self.base_dir, "sign.js")
        self.node_path = settings.NODE_PATH
        
        self.device_uuid = None
        self.identity_id = None
        self.token = None
        self.current_session_id = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                }
            )
        return self._client

    async def _setup_account(self, acc: Dict[str, Any]) -> bool:
        """Thiết lập thông tin tài khoản EaseMate."""
        try:
            self.device_uuid = acc.get("device_uuid")
            self.identity_id = acc.get("identity_id")
            self.token = acc.get("token")
            self.current_session_id = None # Reset session for new account
            
            if not self.device_uuid or not self.identity_id:
                await self._ensure_identity()
            
            return True
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập tài khoản EaseMate: {e}")
            return False

    def _save_config(self):
        try:
            data = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            if "providers" not in data:
                data["providers"] = {}
                
            # Cập nhật phần easemate (Chỉ dùng cho guest account mới đăng ký)
            data["providers"]["easemate"] = [
                {
                    "device_uuid": self.device_uuid,
                    "identity_id": self.identity_id,
                    "token": self.token
                }
            ]
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Lỗi khi lưu cấu hình EaseMate vào config.json: {e}")

    async def _get_signature(self, payload: Dict[str, Any]) -> Tuple[str, str]:
        """Gọi sign.js qua node để lấy signature và timestamp."""
        timestamp_ns = str(time.time_ns())
        payload_str = json.dumps(payload, separators=(',', ':'))
        
        # Đảm bảo đã có device_uuid (identity_id có thể rỗng khi đăng ký)
        dev_uuid = self.device_uuid or secrets.token_hex(16)
        ident_id = self.identity_id or ""

        process = await asyncio.create_subprocess_exec(
            self.node_path, self.sign_js_path, payload_str, timestamp_ns, dev_uuid, ident_id,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.base_dir
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode()
            logger.error(f"Lỗi khi ký gói tin EaseMate: {error_msg}")
            raise Exception(f"Lỗi khi ký gói tin: {error_msg}")

        lines = stdout.decode().strip().split('\n')
        # Lấy dòng cuối cùng chứa JSON
        try:
            sig_data = json.loads(lines[-1])
            return sig_data['sign'], sig_data['timestamp']
        except Exception as e:
            logger.error(f"Lỗi parse signature từ sign.js: {e}. Output: {stdout.decode()}")
            raise Exception(f"Lỗi parse signature: {e}")

    async def _ensure_identity(self):
        """Đảm bảo thiết bị đã được đăng ký identity_id."""
        if self.device_uuid and self.identity_id:
            return

        self.device_uuid = secrets.token_hex(16)
        logger.info(f"[*] Đang đăng ký thiết bị EaseMate mới: {self.device_uuid}")
        
        payload = {}
        sign, timestamp = await self._get_signature(payload)
        
        headers = {
            "accept": "application/json, text/plain, */*",
            "client-name": "chatpdf",
            "client-type": "web",
            "content-type": "application/json;charset=UTF-8",
            "device-platform": "Windows,Chrome",
            "device-type": "web",
            "device-uuid": self.device_uuid,
            "identity-id": "",
            "lang": "en",
            "language": "en-US",
            "origin": "https://www.easemate.ai",
            "referer": "https://www.easemate.ai/",
            "sign": sign,
            "site": "www.easemate.ai",
            "timestamp": timestamp,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            response = await self.client.post(
                "https://api.easemate.ai/api2/task/identity_id",
                headers=headers,
                json=payload
            )
            
            res_json = response.json()
            if res_json.get("code") == 200 and "data" in res_json:
                self.identity_id = res_json["data"]["identity_id"]
                self._save_config()
                logger.info("Đăng ký identity_id EaseMate thành công!")
            else:
                logger.warning(f"Lỗi phản hồi đăng ký từ EaseMate: {res_json.get('message')}")
                self.identity_id = secrets.token_hex(32)
                self._save_config()
        except Exception as e:
            logger.error(f"Không thể kết nối API đăng ký EaseMate ({e})")
            self.identity_id = secrets.token_hex(32)
            self._save_config()

    async def _create_session(self, model_id: int) -> int:
        await self._ensure_identity()
        
        payload = {"model_id": model_id}
        sign, timestamp = await self._get_signature(payload)
        
        headers = {
            "accept": "application/json, text/plain, */*",
            "client-name": "chatpdf",
            "client-type": "web",
            "content-type": "application/json;charset=UTF-8",
            "device-platform": "Windows,Chrome",
            "device-type": "web",
            "device-uuid": self.device_uuid,
            "identity-id": self.identity_id,
            "lang": "en",
            "language": "en-US",
            "origin": "https://www.easemate.ai",
            "referer": "https://www.easemate.ai/",
            "sign": sign,
            "site": "www.easemate.ai",
            "timestamp": timestamp,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            response = await self.client.post(
                "https://api.easemate.ai/api2/task/create_pure_session",
                headers=headers,
                json=payload
            )
            
            res_json = response.json()
            if res_json.get("code") == 200 and "data" in res_json:
                return res_json["data"]["session_id"]
        except Exception as e:
            logger.error(f"Lỗi tạo session EaseMate: {e}")
            
        return 1000557976 # Fallback session ID

    async def verify_identity(self, device_uuid: str, identity_id: str, token: str = None) -> Tuple[bool, str]:
        """Kiểm tra tính hợp lệ của device_uuid và identity_id."""
        payload = {"model_id": 6}
        
        # Lưu ID cũ
        old_uuid = self.device_uuid
        old_ident = self.identity_id
        old_token = self.token
        
        try:
            self.device_uuid = device_uuid
            self.identity_id = identity_id
            self.token = token
            
            sign, timestamp = await self._get_signature(payload)
            
            headers = {
                "accept": "application/json, text/plain, */*",
                "client-name": "chatpdf",
                "client-type": "web",
                "content-type": "application/json;charset=UTF-8",
                "device-platform": "Windows,Chrome",
                "device-type": "web",
                "device-uuid": device_uuid,
                "identity-id": identity_id,
                "lang": "en",
                "language": "en-US",
                "origin": "https://www.easemate.ai",
                "referer": "https://www.easemate.ai/",
                "sign": sign,
                "site": "www.easemate.ai",
                "timestamp": timestamp,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            if token:
                headers["Authorization"] = f"Bearer {token}"

            response = await self.client.post(
                "https://api.easemate.ai/api2/task/create_pure_session",
                headers=headers,
                json=payload,
                timeout=10.0
            )
            
            res_json = response.json()
            code = res_json.get("code")
            message = res_json.get("message", "Unknown error")
            
            if code == 200:
                return True, "Khóa hợp lệ"
            
            error_msg = "Khóa không hợp lệ hoặc đã bị chặn (Yêu cầu đăng nhập)" if (code == 4007 or "login" in message.lower()) else f"Lỗi từ máy chủ ({code}): {message}"
            self._mark_account_failed({
                "device_uuid": device_uuid,
                "identity_id": identity_id,
                "token": token
            }, duration=86400)
            
            return False, error_msg
                
        except Exception as e:
            return False, f"Lỗi kết nối: {str(e)}"
        finally:
            # Khôi phục lại ID cũ
            self.device_uuid = old_uuid
            self.identity_id = old_ident
            self.token = old_token

    async def query_permission(self, device_uuid: str, identity_id: str, token: str = None) -> Dict[str, Any]:
        """Lấy thông tin hạn mức và lượt dùng còn lại của tài khoản."""
        payload = {}
        
        # Lưu ID cũ
        old_uuid = self.device_uuid
        old_ident = self.identity_id
        old_token = self.token

        try:
            self.device_uuid = device_uuid
            self.identity_id = identity_id
            self.token = token
            
            sign, timestamp = await self._get_signature(payload)
            
            headers = {
                "accept": "application/json, text/plain, */*",
                "client-name": "chatpdf",
                "client-type": "web",
                "content-type": "application/json;charset=UTF-8",
                "device-platform": "Windows,Chrome",
                "device-type": "web",
                "device-uuid": device_uuid,
                "identity-id": identity_id,
                "lang": "en",
                "language": "en-US",
                "origin": "https://www.easemate.ai",
                "referer": "https://www.easemate.ai/",
                "sign": sign,
                "site": "www.easemate.ai",
                "timestamp": timestamp,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            if token:
                headers["Authorization"] = f"Bearer {token}"

            response = await self.client.post(
                "https://api.easemate.ai/api2/task/query_permission",
                headers=headers,
                json=payload,
                timeout=10.0
            )
            
            res_json = response.json()
            if res_json.get("code") == 200 and "data" in res_json:
                return {
                    "success": True,
                    "data": res_json["data"]
                }
            return {
                "success": False,
                "message": res_json.get("message", "Không thể lấy thông tin hạn mức")
            }
        except Exception as e:
            logger.error(f"Lỗi truy vấn hạn mức EaseMate: {e}")
            return {
                "success": False,
                "message": f"Lỗi kết nối: {str(e)}"
            }
        finally:
            # Khôi phục lại ID cũ
            self.device_uuid = old_uuid
            self.identity_id = old_ident
            self.token = old_token

    def _get_current_session_id(self, default_id: str = None) -> str:
        return str(self.current_session_id) if self.current_session_id else (default_id or "new")

    async def _get_stream(self, message: str, model: str, session_id: str = None) -> AsyncGenerator[str, None]:
        # Phân tích model_id từ tên model
        model_id = 6 # Mặc định Gemini 2.0 Flash
        try:
            model_name = model.split("/")[-1] if "/" in model else model
            from app.services.models import EASEMATE_MODEL_MAPPING
            if model_name in EASEMATE_MODEL_MAPPING:
                model_id = EASEMATE_MODEL_MAPPING[model_name]
            elif model_name.isdigit():
                model_id = int(model_name)
        except Exception as e:
            logger.error(f"Lỗi khi phân tích model_id '{model}': {e}")

        # Luôn tạo session mới nếu session_id không hợp lệ hoặc không có session hiện tại
        if not self.current_session_id or (session_id and str(session_id) != str(self.current_session_id)):
            if session_id and str(session_id).isdigit():
                self.current_session_id = int(session_id)
            else:
                self.current_session_id = await self._create_session(model_id)
                logger.info(f"[*] Đã tạo session mới cho EaseMate: {self.current_session_id}")

        async for chunk in self._stream_chat(message, model_id, self.current_session_id):
            yield chunk

    async def _stream_chat(self, message: str, model_id: int, session_id: int) -> AsyncGenerator[str, None]:
        await self._ensure_identity()
        
        payload = {
            "model_id": model_id, 
            "session_id": session_id,
            "operation_info": {
                "operation": message,
                "id": 10000
            },
            "parameters": json.dumps({
                "webSearch": False, 
                "isThinking": True if model_id == 5 else False
            }, separators=(',', ':'))
        }
        
        sign, timestamp = await self._get_signature(payload)
        
        headers = {
            "accept": "text/event-stream",
            "accept-language": "en-US,en;q=0.9",
            "client-name": "chatpdf",
            "client-type": "web",
            "content-type": "application/json;charset=UTF-8",
            "device-platform": "Windows,Chrome",
            "device-type": "web",
            "device-uuid": self.device_uuid,
            "identity-id": self.identity_id,
            "lang": "en",
            "language": "en-US",
            "origin": "https://www.easemate.ai",
            "referer": "https://www.easemate.ai/",
            "sign": sign,
            "site": "www.easemate.ai",
            "timestamp": timestamp,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            async with self.client.stream(
                "POST", 
                "https://api.easemate.ai/api2/stream/exec_operation",
                headers=headers,
                json=payload,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"EaseMate API error {response.status_code}: {error_text.decode()}")

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    if not line.startswith("data:"):
                        # Nếu dòng không bắt đầu bằng data:, có thể là lỗi định dạng JSON trực tiếp
                        try:
                            error_json = json.loads(line)
                            if error_json.get('code') and error_json.get('code') != 200:
                                error_msg = error_json.get('message', 'Unknown API Error')
                                logger.error(f"EaseMate API Error (Non-SSE): {error_msg}")
                                raise Exception(f"EaseMate API error: {error_msg}")
                        except json.JSONDecodeError:
                            # Không phải JSON, bỏ qua
                            pass
                        continue

                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data_json = json.loads(data_str)
                        
                        # Kiểm tra code lỗi từ API (nếu có)
                        if data_json.get('code') and data_json.get('code') != 200:
                            error_msg = data_json.get('message', 'Lỗi không xác định từ EaseMate')
                            raise Exception(f"EaseMate API error: {error_msg}")

                        if 'data' in data_json:
                            inner_data = json.loads(data_json['data'])
                            
                            # Ưu tiên trả về answer, nếu là model thinking thì có thể trả về inference
                            inference = inner_data.get('inference', '')
                            if inference:
                                yield inference
                                
                            answer = inner_data.get('answer', '')
                            if not answer and 'content' in inner_data: # Thử key content nếu answer trống
                                answer = inner_data.get('content', '')
                                
                            if answer:
                                yield answer
                    except Exception as e:
                        if "EaseMate API error" in str(e):
                            raise e
                        logger.error(f"Lỗi parse chunk EaseMate: {e}, Data: {data_str}")
                        continue
        except Exception as e:
            logger.error(f"Lỗi stream EaseMate: {e}")
            raise e
