import json
import time
import os
import asyncio
import httpx
import secrets
from typing import Tuple, AsyncGenerator, Dict, Any
from app.providers.base import BaseProvider
from app.core.config import settings
from app.core.logging import logger

class EaseMateProvider(BaseProvider):
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.config_path = "config.json"
        self.sign_js_path = os.path.join(self.base_dir, "sign.js")
        self.node_path = settings.NODE_PATH
        
        self.device_uuid = None
        self.identity_id = None
        self._client = None
        self._load_config()

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

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    easemate_config = data.get("providers", {}).get("easemate", {})
                    self.device_uuid = easemate_config.get("device_uuid")
                    self.identity_id = easemate_config.get("identity_id")
            except Exception as e:
                logger.error(f"Lỗi khi tải cấu hình EaseMate từ config.json: {e}")

    def _save_config(self):
        try:
            data = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            if "providers" not in data:
                data["providers"] = {}
                
            # Cập nhật phần easemate
            data["providers"]["easemate"] = {
                "device_uuid": self.device_uuid,
                "identity_id": self.identity_id
            }
            
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

    async def verify_identity(self, device_uuid: str, identity_id: str) -> Tuple[bool, str]:
        """Kiểm tra tính hợp lệ của device_uuid và identity_id."""
        payload = {"model_id": 6}
        
        # Tạo signature tạm thời với cặp ID cần kiểm tra
        old_uuid = self.device_uuid
        old_ident = self.identity_id
        
        try:
            self.device_uuid = device_uuid
            self.identity_id = identity_id
            
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
            elif code == 4007 or "login" in message.lower():
                return False, "Khóa không hợp lệ hoặc đã bị chặn (Yêu cầu đăng nhập)"
            else:
                return False, f"Lỗi từ máy chủ ({code}): {message}"
                
        except Exception as e:
            return False, f"Lỗi kết nối: {str(e)}"
        finally:
            # Khôi phục lại ID cũ
            self.device_uuid = old_uuid
            self.identity_id = old_ident

    async def generate_stream(self, message: str, model: str, session_id: str = None) -> Tuple[AsyncGenerator[str, None], str]:
        # Phân tích model_id từ tên model (ví dụ: easemate/gemini-2.5-flash hoặc easemate/5)
        model_id = 6 # Mặc định Gemini 2.0 Flash
        
        try:
            if "/" in model:
                model_name = model.split("/")[-1]
                
                # Kiểm tra trong mapping trước
                from app.services.models import EASEMATE_MODEL_MAPPING
                if model_name in EASEMATE_MODEL_MAPPING:
                    model_id = EASEMATE_MODEL_MAPPING[model_name]
                elif model_name.isdigit():
                    model_id = int(model_name)
        except Exception as e:
            logger.error(f"Lỗi khi phân tích model_id '{model}': {e}")
            
        # Nếu session_id không hợp lệ, tạo mới
        if not session_id or not str(session_id).isdigit():
            session_id_int = await self._create_session(model_id)
        else:
            session_id_int = int(session_id)

        generator = self._stream_chat(message, model_id, session_id_int)
        return generator, str(session_id_int)

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
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data_json = json.loads(data_str)
                            if 'data' in data_json:
                                inner_data = json.loads(data_json['data'])
                                
                                # Ưu tiên trả về answer, nếu là model thinking thì có thể trả về inference
                                inference = inner_data.get('inference', '')
                                if inference:
                                    yield inference
                                    
                                answer = inner_data.get('answer', '')
                                if answer:
                                    yield answer
                        except:
                            continue
        except Exception as e:
            logger.error(f"Lỗi stream EaseMate: {e}")
            raise e
