"""Service streaming cho các response SSE."""
import json
import asyncio
import time
import uuid
from typing import AsyncGenerator

async def stream_response(
    response_generator: AsyncGenerator[str, None],
    completion_id: str,
    model: str,
    last_message: str
) -> AsyncGenerator[str, None]:
    """
    Stream response theo định dạng SSE, nhận vào một AsyncGenerator.
    
    Args:
        response_generator: Generator cung cấp các text chunk
        completion_id: ID của completion
        model: Tên model
        last_message: Tin nhắn cuối cùng của user
        
    Yields:
        Các chunk được định dạng SSE
    """
    # Chunk đầu tiên chứa role
    first_chunk = {
        'id': completion_id,
        'object': 'chat.completion.chunk',
        'created': int(time.time()),
        'model': model,
        'choices': [
            {
                'index': 0,
                'delta': {
                    'role': 'assistant',
                    'content': ''
                },
                'finish_reason': None
            }
        ]
    }
    yield f"data: {json.dumps(first_chunk)}\n\n"
    
    response_text = ""
    
    # Streaming thực tế: yield ngay khi nhận được các chunk
    async for chunk in response_generator:
        response_text += chunk
        chunk_data = {
            'id': completion_id,
            'object': 'chat.completion.chunk',
            'created': int(time.time()),
            'model': model,
            'choices': [
                {
                    'index': 0,
                    'delta': {
                        'content': chunk
                    },
                    'finish_reason': None
                }
            ]
        }
        yield f"data: {json.dumps(chunk_data)}\n\n"
    
    # Chunk cuối cùng chứa finish_reason
    final_chunk = {
        'id': completion_id,
        'object': 'chat.completion.chunk',
        'created': int(time.time()),
        'model': model,
        'choices': [
            {
                'index': 0,
                'delta': {},
                'finish_reason': 'stop'
            }
        ],
        'usage': {
            'prompt_tokens': len(last_message.split()),
            'completion_tokens': len(response_text.split()),
            'total_tokens': len(last_message.split()) + len(response_text.split())
        }
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"
