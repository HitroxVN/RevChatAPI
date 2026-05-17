"""Các model Pydantic cho request/response schema."""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any, Union


# Các model tương thích với OpenAI
class Message(BaseModel):
    """Tin nhắn trong hội thoại."""
    role: str
    content: Union[str, List[Dict[str, Any]]]


class ChatCompletionRequest(BaseModel):
    """Request chat completion của OpenAI."""
    model: str
    messages: List[Message]
    stream: bool = False
    session_id: Optional[str] = None


class ChatCompletionChoice(BaseModel):
    """Lựa chọn trong response chat completion."""
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    """Thông tin sử dụng token."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """Response chat completion của OpenAI."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


class Model(BaseModel):
    """Thông tin model."""
    id: str
    object: str = "model"
    created: int = 1677610602
    owned_by: str


class ModelsResponse(BaseModel):
    """Response cho endpoint danh sách model."""
    object: str = "list"
    data: List[Model]


class HealthResponse(BaseModel):
    """Response kiểm tra trạng thái (health check)."""
    status: str


class ChatCompletionChunkDelta(BaseModel):
    """Phần thay đổi (delta) trong streaming chunk."""
    content: Optional[str] = None
    role: Optional[str] = None


class ChatCompletionChunkChoice(BaseModel):
    """Lựa chọn trong streaming chunk."""
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    """Streaming chunk cho chat completion."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]


# Các model tương thích với Claude
class ClaudeContentBlock(BaseModel):
    """Khối nội dung trong response của Claude."""
    type: str = "text"
    text: str


class ClaudeMessage(BaseModel):
    """Tin nhắn theo định dạng Claude."""
    role: str
    content: Union[str, List[Dict[str, Any]]]


class ClaudeUsage(BaseModel):
    """Thông tin sử dụng cho Claude."""
    input_tokens: int
    output_tokens: int


class ClaudeMessageResponse(BaseModel):
    """Response tin nhắn của Claude."""
    id: str
    type: str = "message"
    role: str = "assistant"
    content: List[ClaudeContentBlock]
    model: str
    stop_reason: str = "end_turn"
    stop_sequence: Optional[str] = None
    usage: ClaudeUsage


class ErrorResponse(BaseModel):
    """Response lỗi."""
    error: Dict[str, Any]
