"""Cấu hình các thiết lập cho ứng dụng."""
import os
from typing import List
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()


class Settings:
    """Các thiết lập của ứng dụng."""
    
    # Thiết lập API
    API_TITLE: str = os.getenv("API_TITLE", "RevChatAPI")
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "easemate/gemini-2.0-flash")
    
    # Thiết lập Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5000"))
    
    # Thiết lập CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "*"
    ).split(",") if os.getenv("CORS_ORIGINS") else ["*"]
    
    # Thiết lập API Key
    REQUIRE_AUTH: bool = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    
    # Thiết lập Admin Key (để truy cập giao diện Admin)
    ADMIN_KEY: str = os.getenv("ADMIN_KEY", "")
    
    # Thiết lập Timeout
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "60"))
    
    # Giới hạn lưu lượng (Rate Limiting)
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "30/minute")
    
    # Nhật ký ứng dụng (Logging)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    NODE_PATH: str = os.getenv("NODE_PATH", "node")
    
    # Thiết lập Session
    SESSION_TTL: int = int(os.getenv("SESSION_TTL", "3600"))  # 1 giờ
    
    # Chế độ Debug
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
