"""Các hàm bổ trợ cho các route API."""
from fastapi import HTTPException
from typing import List, Dict, Any, Union

VALID_ROLES = {"system", "user", "assistant"}

def validate_messages(messages: List[Dict[str, Any]]) -> None:
    """Xác thực role của các tin nhắn."""
    if not isinstance(messages, list):
        raise HTTPException(
            status_code=400,
            detail={
                'error': {
                    'message': f'Messages must be a list, got {type(messages).__name__}',
                    'type': 'invalid_request_error',
                    'code': 'invalid_request_error'
                }
            }
        )
        
    for i, msg in enumerate(messages):
        role = msg.get("role")
        if role not in VALID_ROLES:
            raise HTTPException(
                status_code=400,
                detail={
                    'error': {
                        'message': f'Invalid role at index {i}: {role}. Must be one of {VALID_ROLES}',
                        'type': 'invalid_request_error',
                        'code': 'invalid_request_error'
                    }
                }
            )

def extract_last_user_message(messages: List[Dict[str, Any]]) -> str:
    """Trích xuất tin nhắn cuối cùng của user từ danh sách messages."""
    for msg in reversed(messages):
        if msg.get('role') == 'user':
            content = msg.get('content')
            if not content:
                continue
                
            # Xử lý định dạng OpenAI/Claude (chuỗi hoặc danh sách các dict)
            if isinstance(content, list):
                text_parts = []
                for c in content:
                    if isinstance(c, dict):
                        # Claude sử dụng 'text', OpenAI có thể sử dụng 'text' hoặc 'image_url'
                        if c.get('type') == 'text':
                            text_parts.append(c.get('text', ''))
                        elif 'text' in c:
                            text_parts.append(c['text'])
                    else:
                        text_parts.append(str(c))
                last_message = ' '.join(filter(None, text_parts))
            elif isinstance(content, str):
                last_message = content
            else:
                last_message = str(content)
            
            if last_message.strip():
                return last_message
    
    raise HTTPException(
        status_code=400,
        detail={
            'error': {
                'message': 'No non-empty user message found',
                'type': 'invalid_request_error',
                'code': 'invalid_request_error'
            }
        }
    )
