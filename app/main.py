"""Ứng dụng FastAPI chính."""
import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

class NoCacheStaticFiles(StaticFiles):
    """Ghi đè StaticFiles."""
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

from app.core.config import settings
from app.core.logging import logger
from app.api.v1.endpoints import chat as openai, providers as claude, health, admin
from app.services.api_keys import api_key_manager

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware xác thực API key."""
    
    async def dispatch(self, request: Request, call_next):
        """Xử lý request với kiểm tra xác thực và thêm header bảo mật."""
        # Thêm các header bảo mật cơ bản
        response = None
        
        path = request.url.path
        
        # 1. Các endpoint công khai (Không cần xác thực)
        PUBLIC_PATHS = {"/health", "/v1", "/v1/models", "/anthropic", "/anthropic/v1"}
        if not settings.REQUIRE_AUTH or path in PUBLIC_PATHS:
            response = await call_next(request)
        
        # 2. Các file tĩnh của giao diện Admin 
        elif request.method == "GET" and (path.startswith("/admin") or path == "/admin"):
            response = await call_next(request)
            
        # 3. Admin API (/api/admin/...)
        elif path.startswith("/api/admin"):
            # Cho phép endpoint login không cần xác thực header
            if path == "/api/admin/login":
                response = await call_next(request)
            else:
                response = await self._authenticate_admin(request, call_next)

        # 4. Standard API (/v1/...) hoặc Anthropic API (/anthropic/v1/...)
        elif path.startswith("/v1") or path.startswith("/anthropic/v1"):
            response = await self._authenticate_api(request, call_next)
        
        else:
            response = await call_next(request)

        # Thêm các Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        if path.startswith("/admin") or path.startswith("/api/admin"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response

    async def _authenticate_admin(self, request: Request, call_next):
        """Xử lý xác thực Admin API."""
        auth_header = request.headers.get("Authorization")
        if auth_header != f"Bearer {settings.ADMIN_KEY}":
            logger.warning(f"Yêu cầu Admin không được xác thực từ {request.client.host}")
            return self._unauthorized_response()
        return await call_next(request)

    async def _authenticate_api(self, request: Request, call_next):
        """Xử lý xác thực Standard API."""
        auth_header = request.headers.get("Authorization")
        x_api_key = request.headers.get("x-api-key")
        
        api_key = None
        if auth_header and auth_header.startswith("Bearer "):
            api_key = auth_header.replace("Bearer ", "")
        elif x_api_key:
            api_key = x_api_key
            
        if not api_key:
            logger.warning(f"Thiếu header xác thực từ {request.client.host}")
            return self._unauthorized_response()
            
        if not api_key_manager.get_key(api_key):
            logger.warning(f"API key không hợp lệ từ {request.client.host}")
            return self._unauthorized_response()
            
        return await call_next(request)

    def _unauthorized_response(self) -> Response:
        """Trả về response lỗi xác thực chuẩn hóa."""
        return Response(
            content=json.dumps({"error": "Unauthorized"}),
            status_code=401,
            media_type="application/json"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý vòng đời (lifespan) ứng dụng."""
    # Khởi chạy (Startup)
    logger.info(f"Đang khởi chạy {settings.API_TITLE} v{settings.API_VERSION}...")
    logger.info(f"Yêu cầu xác thực: {settings.REQUIRE_AUTH}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")
    yield
    # Tắt ứng dụng (Shutdown)
    logger.info("Đang tắt ứng dụng...")


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Thêm CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm auth middleware
if settings.REQUIRE_AUTH:
    app.add_middleware(AuthMiddleware)

# Bao gồm các router
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(openai.router)
app.include_router(claude.router)
app.include_router(health.router)

# Gắn kết các file tĩnh cho giao diện Admin (SPA)
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

# Mount thư mục assets riêng để truy cập nhanh các file JS/CSS
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/admin/assets", StaticFiles(directory=assets_dir), name="admin_assets")

@app.get("/admin/{path:path}")
async def admin_ui(path: str):
    """Cung cấp giao diện Admin (SPA support)."""
    if not os.path.exists(frontend_dist):
        return Response(content="Frontend chưa được build. Vui lòng chạy 'npm run build' trong thư mục frontend.", status_code=503)

    # 1. Thử tìm file vật lý trong thư mục dist (cho favicon.ico, vite.svg, v.v.)
    file_path = os.path.join(frontend_dist, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # 2. Nếu không thấy file, hoặc là đường dẫn router (SPA), trả về index.html
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return Response(content="Không tìm thấy file index.html", status_code=404)

@app.get("/admin")
async def admin_root():
    return await admin_ui("")
