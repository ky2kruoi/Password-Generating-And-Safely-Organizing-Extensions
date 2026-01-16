# Password-Generating-And-Safely-Organizing-Extensions
🛡️ Secure PassManager - Personal Password Vault

Secure PassManager là một công cụ quản lý và tạo mật khẩu an toàn dành cho cá nhân, được phát triển bằng ngôn ngữ Python trên nền tảng Web Local (Flask). Dự án tập trung vào việc áp dụng các tiêu chuẩn mật mã học hiện đại để giải quyết vấn đề mật khẩu yếu và rủi ro lộ dữ liệu.




🚀 Tính năng chính

Quản lý Khóa Chủ (Master Key): Người dùng chỉ cần nhớ duy nhất một Khóa Chủ để truy cập toàn bộ kho mật khẩu.
Trình tạo mật khẩu mạnh: Tự động tạo mật khẩu với entropy cao, tùy chỉnh độ dài và loại ký tự.
Hỗ trợ Passphrase: Tạo cụm mật khẩu theo chuẩn NIST, ưu tiên độ dài để tăng cường bảo mật.
Mã hóa dữ liệu: Tuyệt đối không lưu mật khẩu ở dạng văn bản thuần túy (plaintext).
Bảo mật phiên làm việc: Tự động yêu cầu xác thực lại khi đóng trình duyệt hoặc hết thời gian chờ (15 phút).




🛠️ Kiến trúc Bảo mật 
Dự án được xây dựng dựa trên các thư viện mã hóa chuẩn công nghiệp:

Password Hashing: Sử dụng thuật toán Argon2 để băm Khóa Chủ, chống lại các cuộc tấn công Brute-force.
Encryption: Áp dụng AES-256-GCM để mã hóa mật khẩu dịch vụ, đảm bảo cả tính bảo mật và tính toàn vẹn của dữ liệu.
Key Derivation: Sử dụng PBKDF2-HMAC-SHA256 với 100.000 vòng lặp kết hợp Salt để tạo khóa mã hóa từ Khóa Chủ.
Storage: Dữ liệu được tổ chức trong tệp vault.json bao gồm phần Metadata bảo mật và các Entries đã được mã hóa.




📂 Cấu trúc dự án
Plaintext

.
├── app.py              # Luồng điều phối Web và quản lý Session
├── backend/            
│   ├── auth.py         # Xác thực người dùng và quản lý vault [cite: 156]
│   ├── crypto_utils.py # Module mã hóa AES-GCM và tạo khóa 
│   ├── manager.py      # Quản lý CRUD (Thêm, Xem, Xóa mật khẩu) [cite: 92]
│   └── generator.py    # Trình tạo mật khẩu an toàn [cite: 149]
├── static/             # CSS (style.css) và các tài nguyên giao diện
├── templates/          # Giao diện HTML (setup, login, dashboard, add)
├── .gitignore          # Ngăn chặn push file nhạy cảm (vault.json)
└── requirements.txt    # Danh sách các thư viện Python cần thiết




⚙️ Cài đặt & Sử dụng
Cài đặt thư viện:
pip install -r requirements.txt

Chạy ứng dụng:
python app.py

Truy cập http://127.0.0.1:5000 trên trình duyệt.

⚠️ Lưu ý Quan trọng

Bảo mật vật lý: Luôn đăng xuất khi không sử dụng để bảo vệ Master Key khỏi bộ nhớ tạm.
Rủi ro mất dữ liệu: Nếu quên Khóa Chủ, bạn sẽ không thể khôi phục các mật khẩu đã lưu.



