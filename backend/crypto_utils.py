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
        iterations=100000, # Độ an toàn cao
    )
    return kdf.derive(master_key.encode())

def encrypt_data(master_key: str, plaintext: str):
    """Mã hóa mật khẩu với Salt và IV riêng biệt cho mỗi entry"""
    salt = os.urandom(16)
    iv = os.urandom(12) 
    
    key = derive_key(master_key, salt)
    aesgcm = AESGCM(key)
    
    # AESGCM.encrypt sẽ trả về ciphertext + tag (16 bytes cuối)
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext.encode(), None)
    
    return {
        "ciphertext": ciphertext_with_tag.hex(),
        "iv": iv.hex(),
        "salt": salt.hex()
    }

def decrypt_data(master_key: str, enc_dict: dict):
    """Giải mã mật khẩu"""
    try:
        salt = bytes.fromhex(enc_dict['salt'])
        iv = bytes.fromhex(enc_dict['iv'])
        ciphertext = bytes.fromhex(enc_dict['ciphertext'])
        
        key = derive_key(master_key, salt)
        aesgcm = AESGCM(key)
        
        # Thư viện tự động tách tag từ ciphertext để xác thực
        decrypted = aesgcm.decrypt(iv, ciphertext, None)
        return decrypted.decode()
    except Exception:
        return None