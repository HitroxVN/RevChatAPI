"""Các route kiểm tra trạng thái (health check)."""
from fastapi import APIRouter, Response
from app.schemas.chat import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    """Endpoint kiểm tra trạng thái."""
    return HealthResponse(status="healthy")


@router.get("/v1")
async def v1_root():
    """Endpoint gốc cho /v1."""
    return {"status": "ok"}


@router.head("/v1")
async def v1_head():
    """Endpoint HEAD cho /v1."""
    return Response(status_code=200)
