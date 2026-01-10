import json
import auth
import crypto_utils
import generator
from datetime import datetime

def add_entry(master_key):
    """Chức năng CREATE: Thêm mật khẩu mới"""
    service = input("Tên dịch vụ (vd: Facebook, Gmail): ")
    username = input("Tên đăng nhập/Email: ")
    
    choice = input("Bạn muốn (1) Tự nhập hay (2) Tạo ngẫu nhiên? ")
    if choice == '2':
        password = generator.generate_complex_password(16)
        print(f"Mật khẩu đã tạo: {password}")
    else:
        password = input("Nhập mật khẩu của bạn: ")

    # Mã hóa dữ liệu trước khi lưu
    encrypted_payload = crypto_utils.encrypt_data(master_key, password)
    
    data = auth.load_vault()
    new_entry = {
        "service_name": service,
        "username": username,
        "encrypted_data": encrypted_payload,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data['entries'].append(new_entry)
    auth.save_vault(data) # Sử dụng hàm save_vault đã viết ở auth.py
    print(f"\n[THÀNH CÔNG] Đã lưu mật khẩu cho {service}!")

def view_entries(master_key):
    """Chức năng READ: Hiển thị và giải mã"""
    data = auth.load_vault()
    if not data['entries']:
        print("\nKho mật khẩu đang trống.")
        return None

    print("\n--- DANH SÁCH MẬT KHẨU ---")
    for i, entry in enumerate(data['entries']):
        print(f"{i+1}. Dịch vụ: {entry['service_name']} | Tài khoản: {entry['username']}")
    return data

def delete_entry(master_key):
    """Chức năng DELETE: Xóa mục nhập"""
    data = view_entries(master_key)
    if not data: return

    choice = input("\nNhập số thứ tự để XÓA (hoặc Enter để hủy): ")
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(data['entries']):
            removed = data['entries'].pop(idx)
            auth.save_vault(data)
            print(f"[THÀNH CÔNG] Đã xóa mục: {removed['service_name']}")

def update_entry(master_key):
    """Chức năng UPDATE: Cập nhật mật khẩu mới cho dịch vụ cũ"""
    data = view_entries(master_key)
    if not data: return

    choice = input("\nNhập số thứ tự để CẬP NHẬT mật khẩu: ")
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(data['entries']):
            new_password = input("Nhập mật khẩu mới: ")
            # Mã hóa lại với IV và Salt mới (crypto_utils tự xử lý)
            encrypted_payload = crypto_utils.encrypt_data(master_key, new_password)
            
            data['entries'][idx]['encrypted_data'] = encrypted_payload
            data['entries'][idx]['updated_at'] = datetime.now().isoformat()
            
            auth.save_vault(data)
            print(f"[THÀNH CÔNG] Đã cập nhật mật khẩu cho {data['entries'][idx]['service_name']}")

if __name__ == "__main__":
    master_key = auth.login()
    if master_key:
        while True:
            print("\n" + "="*30)
            print("DANH MỤC QUẢN LÝ MẬT KHẨU")
            print("1. Xem & Giải mã")
            print("2. Thêm mật khẩu mới")
            print("3. Cập nhật mật khẩu")
            print("4. Xóa mục nhập")
            print("5. Thoát")
            print("="*30)
            
            cmd = input("Chọn chức năng (1-5): ")
            if cmd == '1':
                data = view_entries(master_key)
                if data:
                    c = input("\nNhập số để GIẢI MÃ xem mật khẩu (Enter để bỏ qua): ")
                    if c.isdigit():
                        idx = int(c) - 1
                        if 0 <= idx < len(data['entries']):
                            target = data['entries'][idx]
                            pwd = crypto_utils.decrypt_data(master_key, target['encrypted_data'])
                            print(f"-> Mật khẩu: {pwd}")
            elif cmd == '2': add_entry(master_key)
            elif cmd == '3': update_entry(master_key)
            elif cmd == '4': delete_entry(master_key)
            elif cmd == '5': break