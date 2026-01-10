import secrets # Dùng để tạo số ngẫu nhiên an toàn cho mật khẩu
import string
import random # Dùng để xáo trộn danh sách

# Danh sách từ vựng để tạo Passphrase ngẫu nhiên
WORD_LIST = [
    "apple", "river", "sky", "blue", "run", "fast", "happy", "code", 
    "secure", "strong", "night", "sun", "moon", "star", "green", "cat", 
    "dog", "book", "coffee", "music", "light", "dark", "open", "close",
    "correct", "horse", "battery", "staple", "system", "login", "trust",
    "ocean", "mountain", "forest", "desert", "cloud", "rain", "wind",
    "dragon", "tiger", "earth", "mars", "space", "pixel", "data"
]

def generate_complex_password(length=16):
    """
    CHẾ ĐỘ 1: Tạo mật khẩu ký tự phức tạp. Bắt buộc có: Chữ Hoa + Chữ Thường + Số + Ký tự đặc biệt.
    """
    if length < 8:
        print("Cảnh báo: Độ dài quá ngắn (Nên >= 12).")

    # 1. Định nghĩa các nhóm ký tự
    letters_lower = string.ascii_lowercase
    letters_upper = string.ascii_uppercase
    digits = string.digits
    special_chars = string.punctuation

    # 2. Bắt buộc chọn ít nhất 1 ký tự từ mỗi nhóm để đảm bảo độ phức tạp
    password_chars = [
        secrets.choice(letters_lower),
        secrets.choice(letters_upper),
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]

    # 3. Điền nốt các ký tự còn thiếu
    alphabet = letters_lower + letters_upper + digits + special_chars
    remaining_length = length - len(password_chars)
    
    for _ in range(remaining_length):
        password_chars.append(secrets.choice(alphabet))

    # 4. Xáo trộn vị trí để không đoán được quy luật
    random.shuffle(password_chars)
    
    return ''.join(password_chars)

def generate_passphrase(num_words=5, separator="-"):
    """
    CHẾ ĐỘ 2: Tạo Passphrase (Chuẩn NIST). Dễ nhớ, gồm nhiều từ ngẫu nhiên.
    """
    passphrase_words = []
    for _ in range(num_words):
        word = secrets.choice(WORD_LIST)
        word = word.capitalize() # Viết hoa chữ cái đầu (đẹp và an toàn hơn)
        passphrase_words.append(word)
    
    return separator.join(passphrase_words)

# --- MENU CHƯƠNG TRÌNH ---
def main():
    while True:
        print("\n" + "="*40)
        print("   CÔNG CỤ TẠO MẬT KHẨU AN TOÀN")
        print("="*40)
        print("1. Tạo Mật khẩu Phức tạp (VD: H9@kL#m1...)")
        print("2. Tạo Passphrase Dễ nhớ (VD: Apple-River-Sky...)")
        print("3. Thoát")
        
        choice = input(">> Mời bạn chọn (1/2/3): ")

        if choice == '1':
            try:
                length_input = input("Nhập độ dài mong muốn (Không nên nhỏ hơn 8, mặc định là 16): ")
                length = int(length_input) if length_input else 16
                
                pwd = generate_complex_password(length)
                print(f"\n MẬT KHẨU CỦA BẠN: {pwd}")
            except ValueError:
                print("Lỗi: Vui lòng nhập số nguyên.")

        elif choice == '2':
            print("\n--- Tùy chọn Passphrase ---")
            print("a. Dùng dấu gạch ngang (Apple-River)")
            print("b. Dùng dấu cách (Apple River)")
            print("c. Viết gạch dưới (Apple_River)")
            
            sep_choice = input("Chọn kiểu ngăn cách (a/b/c): ").lower()
            separator = "-" # Mặc định
            if sep_choice == 'b': separator = " "
            if sep_choice == 'c': separator = "_"
            
            pwd = generate_passphrase(num_words=5, separator=separator)
            print(f"\n PASSPHRASE CỦA BẠN: {pwd}")

        elif choice == '3':
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

if __name__ == "__main__":
    main()