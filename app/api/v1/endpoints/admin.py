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

@router.get("/chatx/accounts")
async def get_chatx_accounts():
    accounts = []
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "providers" in data and "chatx" in data["providers"]:
                chatx_config = data["providers"]["chatx"]
                if isinstance(chatx_config, list):
                    accounts = chatx_config
                elif isinstance(chatx_config, dict):
                    # Migration: convert single object to list
                    account = {
                        "id": "default",
                        "email": chatx_config.get("email", ""),
                        "password": chatx_config.get("password", ""),
                        "auto_clear_history": chatx_config.get("auto_clear_history", False)
                    }
                    accounts = [account]
    except Exception:
        pass
    
    return {
        "success": True,
        "accounts": accounts
    }

@router.post("/chatx/account/save")
async def save_chatx_account(data: Dict[str, Any] = Body(...)):
    account_id = data.get("id")
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
            
        if "chatx" not in config_data["providers"] or not isinstance(config_data["providers"]["chatx"], list):
            # Migrate or initialize
            if "chatx" in config_data["providers"] and isinstance(config_data["providers"]["chatx"], dict):
                old = config_data["providers"]["chatx"]
                config_data["providers"]["chatx"] = [{
                    "id": "default",
                    "email": old.get("email", ""),
                    "password": old.get("password", ""),
                    "auto_clear_history": old.get("auto_clear_history", False)
                }]
            else:
                config_data["providers"]["chatx"] = []
            
        accounts = config_data["providers"]["chatx"]
        
        if account_id:
            # Update existing
            found = False
            for acc in accounts:
                if acc.get("id") == account_id:
                    acc["email"] = email
                    if password:
                        acc["password"] = password
                    acc["auto_clear_history"] = auto_clear_history
                    found = True
                    break
            if not found:
                return {"success": False, "message": "Account not found"}
        else:
            # Create new
            import uuid
            new_acc = {
                "id": str(uuid.uuid4()),
                "email": email,
                "password": password,
                "auto_clear_history": auto_clear_history
            }
            accounts.append(new_acc)
        
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
        # Update provider state (using the first active account as default for now)
        if accounts:
            first = accounts[0]
            chatx_provider.email = first.get("email")
            if first.get("password"):
                chatx_provider.password = first.get("password")
            chatx_provider.auto_clear_history = first.get("auto_clear_history", False)
            
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.post("/chatx/account/delete")
async def delete_chatx_account(data: Dict[str, Any] = Body(...)):
    account_id = data.get("id")
    if not account_id:
        return {"success": False, "message": "ID is required"}
        
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if "providers" in config_data and "chatx" in config_data["providers"]:
                accounts = config_data["providers"]["chatx"]
                if isinstance(accounts, list):
                    config_data["providers"]["chatx"] = [acc for acc in accounts if acc.get("id") != account_id]
                    
                    with open("config.json", 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=2, ensure_ascii=False)
                    return {"success": True}
        return {"success": False, "message": "Account not found"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/easemate/accounts")
async def get_easemate_accounts():
    accounts = []
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "providers" in data and "easemate" in data["providers"]:
                easemate_config = data["providers"]["easemate"]
                if isinstance(easemate_config, list):
                    accounts = easemate_config
                elif isinstance(easemate_config, dict):
                    account = {
                        "id": "default",
                        "device_uuid": easemate_config.get("device_uuid", ""),
                        "identity_id": easemate_config.get("identity_id", "")
                    }
                    accounts = [account]
    except Exception:
        pass
    
    return {
        "success": True,
        "accounts": accounts
    }

@router.post("/easemate/account/save")
async def save_easemate_account(data: Dict[str, Any] = Body(...)):
    account_id = data.get("id")
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
            
        if "easemate" not in config_data["providers"] or not isinstance(config_data["providers"]["easemate"], list):
            if "easemate" in config_data["providers"] and isinstance(config_data["providers"]["easemate"], dict):
                old = config_data["providers"]["easemate"]
                config_data["providers"]["easemate"] = [{
                    "id": "default",
                    "device_uuid": old.get("device_uuid", ""),
                    "identity_id": old.get("identity_id", "")
                }]
            else:
                config_data["providers"]["easemate"] = []
            
        accounts = config_data["providers"]["easemate"]
        
        if account_id:
            found = False
            for acc in accounts:
                if acc.get("id") == account_id:
                    acc["device_uuid"] = device_uuid
                    acc["identity_id"] = identity_id
                    found = True
                    break
            if not found:
                return {"success": False, "message": "Account not found"}
        else:
            import uuid
            new_acc = {
                "id": str(uuid.uuid4()),
                "device_uuid": device_uuid,
                "identity_id": identity_id
            }
            accounts.append(new_acc)
        
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
        if accounts:
            first = accounts[0]
            easemate_provider.device_uuid = first.get("device_uuid")
            easemate_provider.identity_id = first.get("identity_id")
            
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.post("/easemate/account/delete")
async def delete_easemate_account(data: Dict[str, Any] = Body(...)):
    account_id = data.get("id")
    if not account_id:
        return {"success": False, "message": "ID is required"}
        
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if "providers" in config_data and "easemate" in config_data["providers"]:
                accounts = config_data["providers"]["easemate"]
                if isinstance(accounts, list):
                    config_data["providers"]["easemate"] = [acc for acc in accounts if acc.get("id") != account_id]
                    
                    with open("config.json", 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=2, ensure_ascii=False)
                    return {"success": True}
        return {"success": False, "message": "Account not found"}
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
