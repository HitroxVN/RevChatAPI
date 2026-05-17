"""Route API tương thích với Claude."""
import json
import time
import uuid
import asyncio
import httpx
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Body, Response

from app.schemas.chat import ClaudeMessageResponse, ClaudeContentBlock, ClaudeUsage
from app.services.models import dispatch_message, get_available_models
from app.services.sessions import session_manager
from app.utils.helpers import validate_messages, extract_last_user_message
from app.core.config import settings
from app.core.logging import log_request, log_response, log_error


router = APIRouter()
@router.get("/anthropic")
@router.head("/anthropic")
async def anthropic_root():
    """Endpoint gốc cho /anthropic."""
    return Response(status_code=200)


@router.get("/anthropic/v1")
@router.head("/anthropic/v1")
async def anthropic_v1_root():
    """Endpoint gốc cho /anthropic/v1."""
    return {"status": "ok"}


@router.get("/anthropic/v1/models")
async def list_claude_models():
    """Liệt kê các model hiện có theo định dạng Anthropic."""
    models = get_available_models()
    claude_models = []
    for m in models:
        claude_models.append({
            "type": "model",
            "id": m.get("id"),
            "display_name": m.get("id"),
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(m.get("created", time.time())))
        })
    
    return {
        "type": "list",
        "data": claude_models,
        "first_id": claude_models[0]["id"] if claude_models else None,
        "last_id": claude_models[-1]["id"] if claude_models else None,
        "has_more": False
    }


@router.post("/anthropic/v1/messages")
@router.post("/v1/messages")
async def claude_messages(request: Dict[str, Any] = Body(...)):
    """Endpoint tin nhắn tương thích Claude."""
    start = time.time()
    session_id = request.get('session_id', 'unknown')
    model = request.get('model', settings.DEFAULT_MODEL)
    
    try:
        # Trích xuất các tin nhắn và system prompt từ định dạng Claude
        messages = request.get('messages', [])
        system_prompt = request.get('system')
        
        # Xác thực role của các tin nhắn
        validate_messages(messages)
        
        # Log yêu cầu
        log_request(session_id, model, len(messages))
        
        # Lấy tin nhắn cuối cùng của user
        last_message = extract_last_user_message(messages)
        
        # Thêm system prompt vào đầu nếu được cung cấp
        if system_prompt:
            last_message = f"System Instruction: {system_prompt}\n\nUser Message: {last_message}"
        
        # Tạo hoặc lấy session ID
        internal_session_id = session_manager.get_session_id(session_id)
        
        # Điều phối tin nhắn đến service phù hợp
        response_generator, new_session_id = await dispatch_message(
            model, 
            last_message, 
            internal_session_id
        )
        
        # Lưu trữ session ID nếu được cung cấp
        if session_id:
            session_manager.set_session_id(session_id, new_session_id)
            
        # Response không streaming cho Claude (sử dụng generator)
        response_text = ""
        async for chunk in response_generator:
            response_text += chunk
        
        # Trả về định dạng response tương thích Claude
        claude_response = ClaudeMessageResponse(
            id=f"msg_{uuid.uuid4().hex[:24]}",
            type="message",
            role="assistant",
            content=[
                ClaudeContentBlock(
                    type="text",
                    text=response_text
                )
            ],
            model=request.get('model', settings.DEFAULT_MODEL),
            stop_reason="end_turn",
            stop_sequence=None,
            usage=ClaudeUsage(
                input_tokens=len(last_message.split()),
                output_tokens=len(response_text.split())
            )
        )
        
        # Log phản hồi
        elapsed = time.time() - start
        log_response(session_id, elapsed, len(last_message.split()), len(response_text.split()))
        
        return Response(
            content=json.dumps(claude_response.model_dump(), ensure_ascii=False),
            media_type="application/json",
            headers={
                "Content-Type": "application/json; charset=utf-8"
            }
        )
        
    except HTTPException as e:
        log_error(session_id, f"HTTPException: {e.status_code} - {e.detail}")
        raise
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response is not None else 500
        error_msg = str(e)
        try:
            # Thử lấy thêm thông tin chi tiết từ nội dung response
            error_msg = f"{e}. Response: {e.response.text}"
        except:
            pass
            
        log_error(session_id, error_msg)
        error_response = {
            'error': {
                'message': error_msg,
                'type': 'api_error',
                'code': 'api_error'
            }
        }
        return Response(
            content=json.dumps(error_response),
            status_code=status_code,
            media_type="application/json"
        )
    except Exception as e:
        log_error(session_id, str(e))
        error_response = {
            'error': {
                'message': str(e),
                'type': 'api_error',
                'code': 'api_error'
            }
        }
        return Response(
            content=json.dumps(error_response),
            status_code=500,
            media_type="application/json"
        )

