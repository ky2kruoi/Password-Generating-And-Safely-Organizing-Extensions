import json
import os
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Cấu hình đường dẫn file vault.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_FILE = os.path.join(BASE_DIR, "vault.json")

ph = PasswordHasher()

def is_vault_initialized():
    """Kiểm tra xem hệ thống đã có người dùng chưa"""
    if not os.path.exists(VAULT_FILE):
        return False
    data = load_vault()
    return data is not None and "security_metadata" in data

def load_vault():
    """Đọc dữ liệu từ file JSON"""
    if not os.path.exists(VAULT_FILE):
        return {"security_metadata": {}, "entries": []}
    try:
        with open(VAULT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"security_metadata": {}, "entries": []}

def save_vault(data):
    """Lưu dữ liệu vào file JSON"""
    try:
        with open(VAULT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except IOError:
        return False

def init_vault(master_key):
    """Trường hợp 1: Thiết lập Khóa chủ cho người dùng mới"""
    hashed_password = ph.hash(master_key)
    vault_data = {
        "security_metadata": {
            "master_key_hash": hashed_password,
            "algorithm": "argon2",
            "encryption_algorithm": "AES-256-GCM"
        },
        "entries": [] 
    }
    return save_vault(vault_data)

def verify_master_key(master_key):
    """Trường hợp 2: Kiểm tra Khóa chủ cho người dùng cũ"""
    data = load_vault()
    hashed = data.get("security_metadata", {}).get("master_key_hash")
    if not hashed:
        return False
    try:
        return ph.verify(hashed, master_key)
    except VerifyMismatchError:
        return False