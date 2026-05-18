from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any, List
from app.services.api_keys import api_key_manager
from app.services.models import chatx_provider, easemate_provider
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
            if "providers" in data and "chatx" in data["providers"]:
                chatx_config = data["providers"]["chatx"]
                account_data["email"] = chatx_config.get("email", "")
                account_data["password"] = chatx_config.get("password", "")
                account_data["auto_clear_history"] = chatx_config.get("auto_clear_history", False)
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
        
        if "providers" not in config_data:
            config_data["providers"] = {}
            
        if "chatx" not in config_data["providers"]:
            config_data["providers"]["chatx"] = {}
            
        config_data["providers"]["chatx"]["email"] = email
        if password:
            config_data["providers"]["chatx"]["password"] = password
        config_data["providers"]["chatx"]["auto_clear_history"] = auto_clear_history
        
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

@router.get("/easemate/account")
async def get_easemate_account():
    account_data = {"device_uuid": "", "identity_id": ""}
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "providers" in data and "easemate" in data["providers"]:
                easemate_config = data["providers"]["easemate"]
                account_data["device_uuid"] = easemate_config.get("device_uuid", "")
                account_data["identity_id"] = easemate_config.get("identity_id", "")
    except Exception:
        pass
    
    return {
        "success": True,
        "account": account_data
    }

@router.post("/easemate/account/update")
async def update_easemate_account(data: Dict[str, Any] = Body(...)):
    device_uuid = data.get("device_uuid")
    identity_id = data.get("identity_id")
    
    try:
        config_data = {}
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                try:
                    config_data = json.load(f)
                except:
                    pass
        
        if "providers" not in config_data:
            config_data["providers"] = {}
            
        if "easemate" not in config_data["providers"]:
            config_data["providers"]["easemate"] = {}
            
        config_data["providers"]["easemate"]["device_uuid"] = device_uuid
        config_data["providers"]["easemate"]["identity_id"] = identity_id
        
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
        # Cập nhật trạng thái của provider
        easemate_provider.device_uuid = device_uuid
        easemate_provider.identity_id = identity_id
            
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.post("/easemate/account/verify")
async def verify_easemate_account(data: Dict[str, Any] = Body(...)):
    device_uuid = data.get("device_uuid")
    identity_id = data.get("identity_id")
    
    if not device_uuid or not identity_id:
        return {"success": False, "message": "Vui lòng nhập đầy đủ Device UUID và Identity ID"}
    
    success, message = await easemate_provider.verify_identity(device_uuid, identity_id)
    return {"success": success, "message": message}

@router.get("/easemate/script")
async def get_easemate_script():
    try:
        # Đường dẫn tới file script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # app/api/v1/endpoints/admin.py -> app/providers/easemate/extract_browser_key.js
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), "providers", "easemate", "extract_browser_key.js")
        
        if os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"success": True, "script": content}
        return {"success": False, "message": f"Không tìm thấy file script tại {script_path}"}
    except Exception as e:
        return {"success": False, "message": str(e)}
