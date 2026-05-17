"""Service quản lý session."""
from typing import Dict, Optional
from app.core.config import settings


class SessionManager:
    """Bộ quản lý session thread-safe sử dụng bộ nhớ trong (in-memory storage)."""
    
    def __init__(self):
        """Khởi tạo bộ quản lý session."""
        self._sessions: Dict[str, str] = {}
    
    def get_session_id(self, external_session_id: Optional[str]) -> Optional[str]:
        """
        Lấy ID session nội bộ từ ID session bên ngoài.
        
        Args:
            external_session_id: ID session bên ngoài từ request
            
        Returns:
            ID session nội bộ hoặc None nếu không tìm thấy
        """
        if external_session_id and external_session_id in self._sessions:
            return self._sessions[external_session_id]
        return None
    
    def set_session_id(self, external_session_id: str, internal_session_id: str) -> None:
        """
        Lưu trữ ánh xạ giữa ID session bên ngoài và nội bộ.
        
        Args:
            external_session_id: ID session bên ngoài từ request
            internal_session_id: ID session nội bộ từ backend
        """
        self._sessions[external_session_id] = internal_session_id
    
    def clear_session(self, external_session_id: str) -> None:
        """
        Xóa một session khỏi bộ quản lý.
        
        Args:
            external_session_id: ID session bên ngoài cần xóa
        """
        if external_session_id in self._sessions:
            del self._sessions[external_session_id]


# Thể hiện (instance) bộ quản lý session toàn cục
session_manager = SessionManager()
