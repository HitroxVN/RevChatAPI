"""Service lưu trữ và quản lý API key."""
import json
import os
import uuid
from typing import List, Dict, Optional
from datetime import datetime


class APIKeyManager:
    """Quản lý các API key được lưu trữ trong file JSON."""
    
    def __init__(self, storage_path: str = "config.json"):
        """Khởi tạo bộ quản lý API key."""
        self.storage_path = storage_path
        self._ensure_storage()
    
    def _ensure_storage(self) -> None:
        """Đảm bảo file lưu trữ tồn tại."""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)
    
    def _load_keys(self) -> List[Dict]:
        """Tải các API key từ bộ lưu trữ."""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get("api_keys", [])
            return data
    
    def _save_keys(self, keys: List[Dict]) -> None:
        """Lưu các API key vào bộ lưu trữ."""
        data = keys
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                try:
                    current_data = json.load(f)
                    if isinstance(current_data, dict):
                        current_data["api_keys"] = keys
                        data = current_data
                except:
                    pass
        
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_key(self, name: str, description: str = "") -> str:
        """
        Tạo một API key mới.
        
        Args:
            name: Tên cho API key
            description: Mô tả tùy chọn
            
        Returns:
            API key đã được tạo
        """
        keys = self._load_keys()
        
        api_key = f"sk-{uuid.uuid4().hex}"
        
        key_data = {
            "key": api_key,
            "name": name,
            "description": description,
            "created_at": datetime.utcnow().isoformat()
        }
        
        keys.append(key_data)
        self._save_keys(keys)
        
        return api_key
    
    def list_keys(self) -> List[Dict]:
        """Liệt kê tất cả các API key."""
        return self._load_keys()
    
    def get_key(self, api_key: str) -> Optional[Dict]:
        """
        Lấy thông tin chi tiết của API key theo giá trị key.
        
        Args:
            api_key: Giá trị API key cần tìm
            
        Returns:
            Dữ liệu key nếu tìm thấy, ngược lại là None
        """
        keys = self._load_keys()
        
        for key in keys:
            if key["key"] == api_key:
                return key
        
        return None
    
    def delete_key(self, api_key: str) -> bool:
        """
        Xóa một API key.
        
        Args:
            api_key: API key cần xóa
            
        Returns:
            True nếu đã xóa, False nếu không tìm thấy
        """
        keys = self._load_keys()
        
        original_length = len(keys)
        keys = [k for k in keys if k["key"] != api_key]
        
        if len(keys) < original_length:
            self._save_keys(keys)
            return True
        
        return False
    
    def update_key(self, api_key: str, name: str, description: str) -> bool:
        """
        Cập nhật thông tin chi tiết API key.
        
        Args:
            api_key: API key cần cập nhật
            name: Tên mới
            description: Mô tả mới
            
        Returns:
            True nếu đã cập nhật, False nếu không tìm thấy
        """
        keys = self._load_keys()
        
        for key in keys:
            if key["key"] == api_key:
                key["name"] = name
                key["description"] = description
                self._save_keys(keys)
                return True
        
        return False


# Thể hiện (instance) bộ quản lý API key toàn cục
api_key_manager = APIKeyManager()
