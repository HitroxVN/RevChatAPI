"""Service chatbot để xử lý các lệnh gọi API backend tới Saigon Incom bằng httpx."""
import httpx
import uuid
import time
import sys
from typing import Tuple, AsyncGenerator
from app.core.config import settings
from app.providers.base import BaseProvider

# Cấu hình lại stdout để hỗ trợ UTF-8 cho các ký tự tiếng Việt trong terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class SaigonProvider(BaseProvider):
    def __init__(self):
        self._client = None
        
    def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(float(settings.REQUEST_TIMEOUT), connect=10.0))
        return self._client

    async def generate_stream(self, message: str, model: str, session_id: str = None) -> Tuple[AsyncGenerator[str, None], str]:
        if session_id is None:
            timestamp = int(time.time() * 1000)
            random_suffix = uuid.uuid4().hex[:7]
            session_id = f"session_{timestamp}_{random_suffix}"
            
        generator = self._stream_chatbot_message(message, session_id)
        return generator, session_id

    async def _stream_chatbot_message(self, message: str, session_id: str = None) -> AsyncGenerator[str, None]:
        """Gửi tin nhắn và trả về phản hồi (tạm thời là giả lập streaming)."""
        url = "https://n8n.incom.vn/webhook/cbcab7f4-d281-4618-9dc1-61774c35b2f4/chat"
        
        if session_id is None:
            timestamp = int(time.time() * 1000)
            random_suffix = uuid.uuid4().hex[:7]
            session_id = f"session_{timestamp}_{random_suffix}"
        
        payload = {
            "chatInput": message,
            "sessionId": session_id
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Origin": "https://saigon.incom.vn",
            "Referer": "https://saigon.incom.vn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        try:
            client = self.get_client()
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            output = data.get("output", "Không tìm thấy nội dung phản hồi.")
            
            # Chúng tôi không có streaming thực tế từ Saigon Incom, vì vậy chúng tôi chỉ trả về toàn bộ khối hoặc chia nhỏ nó một cách nhân tạo
            chunk_size = 10
            for i in range(0, len(output), chunk_size):
                yield output[i:i+chunk_size]
                
        except Exception as e:
            # Raise exception thay vì yield string để API trả về đúng status code
            raise e
