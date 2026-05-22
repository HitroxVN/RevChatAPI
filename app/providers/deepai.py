# -*- coding: utf-8 -*-
"""
DeepAI Chat Provider.
"""

import asyncio
import json
import hashlib
import random
import uuid
import httpx
from typing import AsyncGenerator, Tuple, Dict, Any, List
from app.providers.base import BaseProvider
from app.core.logging import logger

# Constants
DEEPAI_ENDPOINT = "https://api.deepai.org/hacking_is_a_serious_crime"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class DeepAIProvider(BaseProvider):
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, read=60.0),
            headers={
                "User-Agent": USER_AGENT,
                "Origin": "https://deepai.org",
                "Referer": "https://deepai.org/chat",
                "Accept": "*/*",
            }
        )

    def md5_reversed(self, s: str) -> str:
        """Calculates MD5 hash and reverses the resulting hex string."""
        h = hashlib.md5(s.encode('utf-8')).hexdigest()
        return h[::-1]

    def generate_api_key(self):
        """Generates the dynamic api-key required by DeepAI's protection mechanism."""
        salt = str(int(random.random() * 1e11))
        const_suffix = "hackers_become_a_little_stinkier_every_time_they_hack"
        
        # Signature derivation steps
        hash_1 = self.md5_reversed(USER_AGENT + salt + const_suffix)
        hash_2 = self.md5_reversed(USER_AGENT + hash_1)
        hash_3 = self.md5_reversed(USER_AGENT + hash_2)
        
        return f"tryit-{salt}-{hash_3}"

    async def generate_stream(self, message: str, model: str, session_id: str = None) -> Tuple[AsyncGenerator[str, None], str]:
        """Triển khai generate_stream cho DeepAI."""
        target_model = model or "standard"
        
        # Lấy lịch sử hội thoại từ session_id nếu cần (ở đây DeepAI yêu cầu chatHistory)
        history = [{"role": "user", "content": message}]
        
        async def stream_generator() -> AsyncGenerator[str, None]:
            api_key = self.generate_api_key()
            
            data = {
                "chat_style": "chat",
                "model": target_model,
                "session_uuid": str(uuid.uuid4()),
                "hacker_is_stinky": "very_stinky",
                "chatHistory": json.dumps(history),
            }

            headers = {
                "api-key": api_key,
            }

            try:
                async with self.client.stream("POST", DEEPAI_ENDPOINT, data=data, headers=headers) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"DeepAI Error: {response.status_code} - {error_text.decode()}")
                        yield f"Error: {response.status_code}"
                        return

                    async for chunk in response.aiter_text():
                        if chunk:
                            yield chunk
            except Exception as e:
                logger.error(f"Error during DeepAI stream: {e}")
                yield f"Error: {str(e)}"

        return stream_generator(), session_id or str(uuid.uuid4())
