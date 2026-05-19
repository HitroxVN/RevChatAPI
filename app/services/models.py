"""
Service model để quản lý các model AI.
Xử lý cấu hình model, xác thực và truy xuất.
"""

import json
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple, AsyncGenerator
from pathlib import Path
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ModelConfig:
    """Đại diện cho cấu hình của một model đơn lẻ."""
    
    def __init__(
        self,
        model_id: str,
        name: str,
        provider: str,
        api_key_env: str,
        endpoint: Optional[str] = None,
        default: bool = False,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ):
        self.model_id = model_id
        self.name = name
        self.provider = provider
        self.api_key_env = api_key_env
        self.endpoint = endpoint
        self.default = default
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi cấu hình model thành dictionary."""
        return {
            "model_id": self.model_id,
            "name": self.name,
            "provider": self.provider,
            "api_key_env": self.api_key_env,
            "endpoint": self.endpoint,
            "default": self.default,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            **self.extra
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        """Tạo cấu hình model từ dictionary."""
        return cls(
            model_id=data.get("model_id", data.get("id", "")),
            name=data.get("name", ""),
            provider=data.get("provider", ""),
            api_key_env=data.get("api_key_env", data.get("api_key", "")),
            endpoint=data.get("endpoint"),
            default=data.get("default", False),
            max_tokens=data.get("max_tokens", 4096),
            temperature=data.get("temperature", 0.7),
            **{k: v for k, v in data.items() 
               if k not in ["model_id", "id", "name", "provider", 
                           "api_key_env", "api_key", "endpoint", 
                           "default", "max_tokens", "temperature"]}
        )


class ModelService:
    """Service để quản lý các model AI."""
    
    def __init__(self, config_path: Optional[str] = None):
        self._models: Dict[str, ModelConfig] = {}
        self._default_model_id: Optional[str] = None
        self.config_path = config_path or "config.json"
        self._load_models()

    def _load_models(self) -> None:
        """Tải các model từ file cấu hình."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            logger.warning(f"Không tìm thấy file cấu hình: {self.config_path}")
            return

        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            
            models_data = config.get("models", [])
            if not models_data:
                logger.warning("Không tìm thấy model nào trong file cấu hình")
                return

            for model_data in models_data:
                model = ModelConfig.from_dict(model_data)
                self._models[model.model_id] = model
                if model.default:
                    self._default_model_id = model.model_id
            
            logger.info(f"Đã tải {len(self._models)} model từ cấu hình")
            if self._default_model_id:
                logger.info(f"Model mặc định: {self._default_model_id}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON không hợp lệ trong file cấu hình: {e}")
        except Exception as e:
            logger.error(f"Lỗi khi tải các model: {e}")

    def get_models(self) -> List[Dict[str, Any]]:
        """Lấy tất cả các model hiện có."""
        return [model.to_dict() for model in self._models.values()]

    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """Lấy một model cụ thể theo ID."""
        return self._models.get(model_id)

    def get_default_model(self) -> Optional[ModelConfig]:
        """Lấy model mặc định."""
        if self._default_model_id:
            return self._models.get(self._default_model_id)
        # Trả về model đầu tiên nếu không có model mặc định nào được thiết lập
        for model in self._models.values():
            return model
        return None

    def model_exists(self, model_id: str) -> bool:
        """Kiểm tra xem một model có tồn tại không."""
        return model_id in self._models

    def add_model(self, model_config: Dict[str, Any]) -> Optional[ModelConfig]:
        """Thêm một model mới một cách động."""
        try:
            model = ModelConfig.from_dict(model_config)
            model_id = model.model_id
            
            if not model_id:
                logger.error("Model ID là bắt buộc")
                return None
            
            self._models[model_id] = model
            if model.default:
                self._default_model_id = model_id
            
            logger.info(f"Đã thêm model: {model_id}")
            return model
            
        except Exception as e:
            logger.error(f"Lỗi khi thêm model: {e}")
            return None

    def remove_model(self, model_id: str) -> bool:
        """Xóa một model theo ID."""
        if model_id in self._models:
            del self._models[model_id]
            if self._default_model_id == model_id:
                self._default_model_id = None
            logger.info(f"Đã xóa model: {model_id}")
            return True
        return False

    def get_providers(self) -> List[str]:
        """Lấy danh sách các provider duy nhất."""
        return list(set(model.provider for model in self._models.values()))

    def get_models_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Lấy tất cả các model cho một provider cụ thể."""
        return [
            model.to_dict() 
            for model in self._models.values() 
            if model.provider == provider
        ]

    def save_config(self) -> bool:
        """Lưu cấu hình model hiện tại vào file."""
        try:
            config = {
                "models": [model.to_dict() for model in self._models.values()]
            }
            
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Đã lưu cấu hình model vào {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi lưu cấu hình: {e}")
            return False

    def reload(self) -> None:
        """Tải lại các model từ file cấu hình."""
        self._models.clear()
        self._default_model_id = None
        self._load_models()


# Thể hiện (instance) singleton
_model_service_instance: Optional[ModelService] = None


def get_model_service(config_path: Optional[str] = None) -> ModelService:
    """Lấy hoặc tạo singleton cho service model."""
    global _model_service_instance
    if _model_service_instance is None:
        _model_service_instance = ModelService(config_path)
    return _model_service_instance


def init_model_service(config_path: Optional[str] = None) -> ModelService:
    """Khởi tạo service model (sử dụng khi ứng dụng khởi chạy)."""
    global _model_service_instance
    _model_service_instance = ModelService(config_path)
    return _model_service_instance


# Ánh xạ tên model thân thiện sang ID của EaseMate
EASEMATE_MODEL_MAPPING = {
    "llama-3.3": 1,
    "claude-3-haiku": 2,
    "gpt-4o-mini": 3,
    "deepseek-v3.2": 4,
    "deepseek-r1": 5,
    "gemini-2.0-flash": 6,
    "kimi-k2.5": 10,
    "qwen3-235b": 11,
    "gemini-3.0-flash": 17
}

CHATX_MODEL_MAPPING = {
    "deepseek-v3-flash": "deepseek_flash",
    "gpt-3.5-turbo": "gpt3"
}

def get_available_models() -> List[Dict[str, Any]]:
    """Lấy danh sách các model hiện có cho tính tương thích OpenAI."""
    service = get_model_service()
    models = service.get_models()
    
    now = int(time.time())
    available_list = []
    
    # Thêm model Saigon Incom (mặc định)
    available_list.append({
        "id": "test/saigon-incom",
        "object": "model",
        "created": now,
        "owned_by": "saigon-incom"
    })
    
    # Thêm các model ChatX với ID thân thiện
    for name in CHATX_MODEL_MAPPING.keys():
        available_list.append({
            "id": f"chatx/{name}",
            "object": "model",
            "created": now,
            "owned_by": "chatx"
        })
        
    # Thêm các model EaseMate với ID thân thiện
    for name in EASEMATE_MODEL_MAPPING.keys():
        available_list.append({
            "id": f"easemate/{name}",
            "object": "model",
            "created": now,
            "owned_by": "easemate"
        })
        
    # Nếu có model trong config.json, ưu tiên chúng
    if models:
        for m in models:
            available_list.append({
                "id": m["model_id"],
                "object": "model",
                "created": now,
                "owned_by": m["provider"]
            })
            
    return available_list


from app.providers.chatx import ChatXProvider
from app.providers.saigon import SaigonProvider
from app.providers.easemate.easemate import EaseMateProvider

# Khởi tạo các provider một lần để giữ trạng thái/connection pool của chúng
chatx_provider = ChatXProvider()
saigon_provider = SaigonProvider()
easemate_provider = EaseMateProvider()

async def dispatch_message(model: str, message: str, session_id: str = None) -> Tuple[AsyncGenerator[str, None], str]:
    """Điều phối tin nhắn đến backend service phù hợp dựa trên tên model."""
    model_lower = model.lower()
    
    # Xử lý mapping model trước khi gửi đi
    target_model = model
    
    if model == "test/saigon-incom":
        return await saigon_provider.generate_stream(message, model, session_id)
        
    elif "easemate" in model_lower:
        return await easemate_provider.generate_stream(message, model, session_id)
        
    elif "chatx" in model_lower:
        model_name = model.split("/")[-1] if "/" in model else model
        if model_name in CHATX_MODEL_MAPPING:
            target_model = f"chatx/{CHATX_MODEL_MAPPING[model_name]}"
        return await chatx_provider.generate_stream(message, target_model, session_id)
        
    # Fallback cho các trường hợp không có prefix
    elif any(k in model_lower for k in ["deepseek", "gpt", "claude"]):
        if model_lower in CHATX_MODEL_MAPPING:
            target_model = f"chatx/{CHATX_MODEL_MAPPING[model_lower]}"
        return await chatx_provider.generate_stream(message, target_model, session_id)
        
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model}' is not supported. Please use a valid model ID."
        )