import uuid
from datetime import datetime
from . import auth, crypto_utils

def get_all_entries():
    """Lấy danh sách mật khẩu (chưa giải mã) để hiển thị lên Web"""
    data = auth.load_vault()
    return data.get('entries', [])

def add_password_entry(master_key, service, username, password):
    """Thêm mật khẩu mới"""
    encrypted_payload = crypto_utils.encrypt_data(master_key, password)
    
    data = auth.load_vault()
    new_entry = {
        "id": str(uuid.uuid4()), # Dùng ID duy nhất thay vì Index
        "service_name": service,
        "username": username,
        "encrypted_data": encrypted_payload,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data['entries'].append(new_entry)
    return auth.save_vault(data)

def delete_password_entry(entry_id):
    """Xóa mật khẩu dựa trên ID"""
    data = auth.load_vault()
    initial_count = len(data['entries'])
    data['entries'] = [e for e in data['entries'] if e['id'] != entry_id]
    
    if len(data['entries']) < initial_count:
        return auth.save_vault(data)
    return False

def get_decrypted_password(master_key, entry_id):
    """Giải mã một mật khẩu cụ thể khi người dùng nhấn 'Xem'"""
    data = auth.load_vault()
    for entry in data['entries']:
        if entry['id'] == entry_id:
            return crypto_utils.decrypt_data(master_key, entry['encrypted_data'])
    return None