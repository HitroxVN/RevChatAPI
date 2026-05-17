from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any, List
from app.services.api_keys import api_key_manager
from app.services.models import chatx_provider
import json
import os

router = APIRouter()

@router.get("/keys")
async def get_keys():
    return {"keys": api_key_manager.list_keys()}

@router.post("/keys/create")
async def create_key(data: Dict[str, str] = Body(...)):
    name = data.get("name", "")
    desc = data.get("description", "")
    key = api_key_manager.create_key(name, desc)
    return {"success": True, "key": key}

@router.post("/keys/update")
async def update_key(data: Dict[str, str] = Body(...)):
    key = data.get("key")
    name = data.get("name", "")
    desc = data.get("description", "")
    if not key:
        return {"success": False, "message": "Key is required"}
    success = api_key_manager.update_key(key, name, desc)
    return {"success": success}

@router.post("/keys/delete")
async def delete_key(data: Dict[str, str] = Body(...)):
    key = data.get("key")
    if not key:
        return {"success": False, "message": "Key is required"}
    success = api_key_manager.delete_key(key)
    return {"success": success}

@router.get("/chatx/account")
async def get_chatx_account():
    account_data = {"email": "", "password": "", "auto_clear_history": False}
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "chatx" in data:
                account_data["email"] = data["chatx"].get("email", "")
                account_data["password"] = data["chatx"].get("password", "")
                account_data["auto_clear_history"] = data["chatx"].get("auto_clear_history", False)
    except Exception:
        pass
    
    return {
        "success": True,
        "account": account_data
    }

@router.post("/chatx/account/update")
async def update_chatx_account(data: Dict[str, Any] = Body(...)):
    email = data.get("email")
    password = data.get("password")
    auto_clear_history = data.get("auto_clear_history", False)
    
    try:
        config_data = {}
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                try:
                    config_data = json.load(f)
                except:
                    pass
        
        if "chatx" not in config_data:
            config_data["chatx"] = {}
            
        config_data["chatx"]["email"] = email
        if password:
            config_data["chatx"]["password"] = password
        config_data["chatx"]["auto_clear_history"] = auto_clear_history
        
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
    # Cập nhật trạng thái của provider
        chatx_provider.email = email
        if password:
            chatx_provider.password = password
        chatx_provider.auto_clear_history = auto_clear_history
            
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}
