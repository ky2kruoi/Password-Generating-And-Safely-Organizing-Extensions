import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def derive_key(master_key: str, salt: bytes):
    """Tạo khóa mã hóa 256-bit từ Khóa Chủ và Salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(master_key.encode())

def encrypt_data(master_key: str, plaintext: str):
    """Mã hóa mật khẩu dịch vụ"""
    # 1. Tạo Salt và IV ngẫu nhiên
    salt = os.urandom(16)
    iv = os.urandom(12) 
    
    # 2. Tạo khóa mã hóa từ Khóa Chủ
    key = derive_key(master_key, salt)
    aesgcm = AESGCM(key)
    
    # 3. Mã hóa
    ciphertext = aesgcm.encrypt(iv, plaintext.encode(), None)
    
    # Trả về các thành phần để lưu vào JSON (dưới dạng hex để dễ lưu trữ)
    return {
        "ciphertext": ciphertext.hex(),
        "iv": iv.hex(),
        "salt": salt.hex(), # Cần thêm salt riêng cho mỗi mục nhập
        "tag": ciphertext[-16:].hex() # AES-GCM tag nằm ở cuối ciphertext
    }

def decrypt_data(master_key: str, enc_dict: dict):
    """Giải mã mật khẩu dịch vụ"""
    try:
        salt = bytes.fromhex(enc_dict['salt'])
        iv = bytes.fromhex(enc_dict['iv'])
        ciphertext = bytes.fromhex(enc_dict['ciphertext'])
        
        key = derive_key(master_key, salt)
        aesgcm = AESGCM(key)
        
        decrypted_password = aesgcm.decrypt(iv, ciphertext, None)
        return decrypted_password.decode()
    except Exception:
        return None