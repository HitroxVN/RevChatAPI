import sys
import asyncio
import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    # Khắc phục lỗi phân quyền socket trên Windows (WinError 10013)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    print(f"Đang khởi chạy server tại http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
