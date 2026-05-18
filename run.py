import sys
import asyncio
import uvicorn
import subprocess
from app.main import app
from app.core.config import settings

def check_node_existence():
    """Kiểm tra xem Node.js đã được cài đặt chưa. Nếu không có thì thoát."""
    try:
        # Thử chạy lệnh node -v
        subprocess.run([settings.NODE_PATH, "-v"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ LỖI: Không tìm thấy Node.js tại đường dẫn: '{settings.NODE_PATH}'")
        print("❌ Vui lòng cài đặt Node.js hoặc cấu hình đúng NODE_PATH trong file .env")
        return False

if __name__ == "__main__":
    # Kiểm tra Node.js trước khi chạy. Nếu không có thì dừng ứng dụng.
    if not check_node_existence():
        sys.exit(1)

    # Khắc phục lỗi phân quyền socket trên Windows (WinError 10013)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    print(f"Đang khởi chạy server tại http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
