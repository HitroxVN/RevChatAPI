"""Route API tương thích với OpenAI."""
import json
import time
import uuid
import asyncio
import requests
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Body, Response
from fastapi.responses import StreamingResponse

from app.schemas.chat import (
    ChatCompletionResponse,
    ChatCompletionChoice,
    Usage,
    Message,
    ModelsResponse
)
from app.services.models import get_available_models, dispatch_message
from app.services.sessions import session_manager
from app.services.streaming import stream_response
from app.utils.helpers import validate_messages, extract_last_user_message
from app.core.config import settings
from app.core.logging import log_request, log_response, log_error


router = APIRouter()


@router.get("/v1/models", response_model=ModelsResponse)
async def list_models():
    """Liệt kê các model hiện có."""
    return ModelsResponse(data=get_available_models())


@router.post("/v1/chat/completions")
async def chat_completions(request: Dict[str, Any] = Body(...)):
    """Endpoint cho chat completions tương thích OpenAI."""
    start = time.time()
    session_id = request.get('session_id', 'unknown')
    model = request.get('model', settings.DEFAULT_MODEL)
    
    try:
        # Kiểm tra xem có yêu cầu streaming không
        stream = request.get('stream', False)
        
        # Trích xuất các tin nhắn
        messages = request.get('messages', [])
        if not messages:
            raise HTTPException(
                status_code=400,
                detail={
                    'error': {
                        'message': 'No messages provided',
                        'type': 'invalid_request_error',
                        'code': 'invalid_request_error'
                    }
                }
            )
        
        # Log yêu cầu
        log_request(session_id, model, len(messages))
        
        # Xác thực role của các tin nhắn
        validate_messages(messages)
        
        # Lấy tin nhắn cuối cùng của user
        last_message = extract_last_user_message(messages)
        
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
        
        # Tạo response tương thích OpenAI
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        created = int(time.time())
        
        # Trả về response streaming nếu được yêu cầu
        if stream:
            return StreamingResponse(
                stream_response(response_generator, completion_id, model, last_message),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )
        
        # Response không streaming
        response_text = ""
        async for chunk in response_generator:
            response_text += chunk
            
        response_data = ChatCompletionResponse(
            id=completion_id,
            object="chat.completion",
            created=created,
            model=model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=response_text
                    ),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=len(last_message.split()),
                completion_tokens=len(response_text.split()),
                total_tokens=len(last_message.split()) + len(response_text.split())
            )
        )
        
        # Log phản hồi
        elapsed = time.time() - start
        log_response(session_id, elapsed, len(last_message.split()), len(response_text.split()))
        
        return response_data
        
    except HTTPException:
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
