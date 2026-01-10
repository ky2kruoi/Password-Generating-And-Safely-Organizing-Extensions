import json
import os
import getpass  # Giúp ẩn mật khẩu khi nhập
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


# Lấy đường dẫn của chính file auth.py này
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Ghép đường dẫn đó với tên file json
VAULT_FILE = os.path.join(SCRIPT_DIR, "vault.json")

# Khởi tạo bộ băm mật khẩu Argon2
# Argon2 tự động xử lý Salt, không cần tạo salt thủ công
ph = PasswordHasher()

def load_vault():
    """Đọc dữ liệu từ file vault.json"""
    if not os.path.exists(VAULT_FILE):
        return None
    try:
        with open(VAULT_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print("Lỗi đọc file dữ liệu!")
        return None

def save_vault(data):
    """Ghi dữ liệu Vault (đã cập nhật) vào file vault.json"""
    try:
        with open(VAULT_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except IOError:
        print("Lỗi: Không thể lưu file dữ liệu.")
        return False

def register():
    """Chức năng ĐĂNG KÝ (Chạy lần đầu tiên)"""
    print("--- THIẾT LẬP KHÓA CHỦ (MASTER KEY) ---")
    print("Đây là lần đầu bạn sử dụng. Hãy tạo mật khẩu chủ.")
    print("Lưu ý: Nếu quên mật khẩu này, bạn sẽ mất toàn bộ dữ liệu!")
    
    while True:
        # Giúp ẩn ký tự khi gõ
        password = getpass.getpass("Nhập Khóa Chủ mới: ")
        confirm = getpass.getpass("Nhập lại Khóa Chủ: ")
        
        if password == confirm and len(password) > 0:
            break
        print("Mật khẩu không khớp hoặc để trống. Vui lòng thử lại.")

    # --- BĂM MẬT KHẨU ---
    # Tự động tạo Salt ngẫu nhiên và băm mật khẩu
    hashed_password = ph.hash(password)
    
    # Tạo cấu trúc dữ liệu ban đầu
    vault_data = {
        "security_metadata": {
            "master_key_hash": hashed_password,
            "algorithm": "argon2",
            "encryption_algorithm": "AES-256-GCM"
        },
        "entries": [] # Danh sách mật khẩu trống
    }
    
    # Lưu vào file JSON
    with open(VAULT_FILE, 'w') as f:
        json.dump(vault_data, f, indent=4)
    
    print("\n[THÀNH CÔNG] Đã tạo Khóa Chủ và file vault.json!")
    return password # Trả về mật khẩu gốc để dùng cho việc tạo khóa mã hóa sau này

def login():
    """Chức năng ĐĂNG NHẬP (Các lần sau)"""
    print("--- ĐĂNG NHẬP ---")
    
    # 1. Tải dữ liệu hash từ file
    data = load_vault()
    if not data:
        return register() # Nếu chưa có file thì chuyển sang đăng ký
        
    saved_hash = data['security_metadata']['master_key_hash']
    
    # 2. Yêu cầu nhập khóa để kiểm tra
    input_password = getpass.getpass("Nhập Khóa Chủ của bạn: ")
    
    # 3. Kiểm tra khóa (Verify)
    try:
        # Hàm verify sẽ so sánh khóa nhập vào với hash đã lưu
        # Nếu sai, nó sẽ báo lỗi VerifyMismatchError
        ph.verify(saved_hash, input_password)
        
        print("\n[THÀNH CÔNG] Xác thực thành công!")
        # Nếu thuật toán Argon2 cần cập nhật tham số (rehash), thư viện sẽ báo true
        if ph.check_needs_rehash(saved_hash):
            print("Cập nhật lại hash bảo mật hơn...")
            # Code cập nhật lại hash (chưa hoàn thành ở đây)
            
        return input_password # Trả về mật khẩu gốc để dùng tiếp
        
    except VerifyMismatchError:
        print("\n[THẤT BẠI] Sai Khóa Chủ! Truy cập bị từ chối.")
        return None

# --- CHẠY THỬ NGHIỆM ---
if __name__ == "__main__":
    # Kiểm tra xem file đã tồn tại chưa để quyết định Register hay Login
    if not os.path.exists(VAULT_FILE):
        key = register()
    else:
        key = login()