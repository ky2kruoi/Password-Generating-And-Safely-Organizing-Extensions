from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from backend import auth, crypto_utils, manager, generator
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'chia_khoa_bi_mat_cua_rieng_ban_2024'

# CẤU HÌNH BẢO MẬT
app.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=15),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

@app.before_request
def check_authentication():
    """Kiểm tra xác thực trước mọi yêu cầu"""
    # 1. Cho phép tải tài nguyên tĩnh (CSS/JS)
    if request.path.startswith('/static'):
        return

    # Danh sách các route không cần đăng nhập
    public_routes = ['login', 'setup']
    
    # 2. Nếu chưa khởi tạo file vault -> Bắt buộc vào setup
    if not auth.is_vault_initialized():
        if request.endpoint != 'setup':
            return redirect(url_for('setup'))
        return

    # 3. Nếu đã có vault nhưng chưa có khóa chủ trong session -> Bắt buộc vào login
    # Kiểm tra request.endpoint để tránh vòng lặp redirect
    if 'master_key' not in session:
        if request.endpoint not in public_routes and request.endpoint is not None:
            return redirect(url_for('login'))

# --- ĐIỀU HƯỚNG ---

@app.route('/')
def index():
    # before_request sẽ tự động xử lý việc đẩy về login hoặc dashboard
    return redirect(url_for('dashboard'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if auth.is_vault_initialized(): 
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        mk = request.form.get('master_key')
        if auth.init_vault(mk):
            session.clear() # Đảm bảo session sạch sau khi setup
            flash("Khởi tạo thành công! Vui lòng đăng nhập bằng Khóa Chủ.")
            return redirect(url_for('login'))
    return render_template('setup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Nếu đã login rồi thì không cho quay lại trang login
    if 'master_key' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        mk = request.form.get('master_key')
        if auth.verify_master_key(mk):
            session.clear() 
            session['master_key'] = mk # Lưu khóa chủ vào phiên làm việc
            session.permanent = False   # Xóa session khi đóng trình duyệt
            return redirect(url_for('dashboard'))
        else:
            flash("Khóa Chủ không chính xác! Vui lòng thử lại.")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Session đã được kiểm tra tại before_request
    entries = manager.get_all_entries()
    return render_template('dashboard.html', entries=entries)

@app.route('/logout')
def logout():
    session.clear() # Xóa sạch Master Key khỏi bộ nhớ
    flash("Bạn đã đăng xuất an toàn.")
    return redirect(url_for('login'))

# --- CÁC API KHÁC (Add, View, Generate...) ---
@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        service = request.form.get('service')
        username = request.form.get('username')
        password = request.form.get('password')
        if manager.add_password_entry(session['master_key'], service, username, password):
            flash(f"Đã thêm mật khẩu cho {service}")
            return redirect(url_for('dashboard'))
    return render_template('add.html')

@app.route('/view/<string:entry_id>')
def view_pass(entry_id):
    if 'master_key' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    password = manager.get_decrypted_password(session['master_key'], entry_id)
    return jsonify({"password": password}) if password else (jsonify({"error": "Fail"}), 400)

@app.route('/delete/<string:entry_id>')
def delete_entry(entry_id):
    if manager.delete_password_entry(entry_id):
        flash("Đã xóa mục thành công.")
    return redirect(url_for('dashboard'))

@app.route('/api/generate')
def api_generate():
    mode = request.args.get('mode', 'complex')
    pass_str = generator.generate_passphrase() if mode == 'passphrase' else generator.generate_complex_password()
    return jsonify({"password": pass_str})

if __name__ == '__main__':
    app.run(debug=True, port=5000)