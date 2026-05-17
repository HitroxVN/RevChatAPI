from abc import ABC, abstractmethod
from typing import AsyncGenerator, Tuple

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
