"""Cấu hình logging."""
import logging
import time
from app.core.config import settings


def setup_logging():
    """Thiết lập logging cho ứng dụng."""
    log_level = settings.LOG_LEVEL
    if not settings.DEBUG:
        log_level = logging.CRITICAL + 1
    else:
        log_level = getattr(logging, log_level)
        
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


logger = setup_logging()


def log_request(session_id: str, model: str, messages_count: int) -> None:
    """Log yêu cầu đến."""
    logger.info(f"Yêu cầu đến - Session: {session_id}, Model: {model}, Số tin nhắn: {messages_count}")


def log_response(session_id: str, elapsed: float, input_tokens: int, output_tokens: int) -> None:
    """Log khi hoàn tất phản hồi."""
    logger.info(
        f"Yêu cầu hoàn tất - Session: {session_id}, "
        f"Thời gian: {elapsed:.2f}s, "
        f"Input tokens: {input_tokens}, "
        f"Output tokens: {output_tokens}"
    )


def log_error(session_id: str, error: str) -> None:
    """Log lỗi."""
    logger.error(f"Lỗi yêu cầu - Session: {session_id}, Lỗi: {error}")
