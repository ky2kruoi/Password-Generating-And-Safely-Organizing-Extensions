from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_cors import CORS
from backend import auth, crypto_utils, manager, generator
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'chia_khoa_bi_mat_cua_rieng_ban_2024'

# Cấu hình CORS cho phép Extension gửi Cookie xác thực
CORS(app, supports_credentials=True)

app.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=15),
    SESSION_COOKIE_SAMESITE='None', 
    SESSION_COOKIE_SECURE=True,     
    SESSION_COOKIE_HTTPONLY=True
)

@app.before_request
def check_authentication():
    """Kiểm tra quyền truy cập cho từng request"""
    # 1. Cho phép các trang công khai và file tĩnh
    public_endpoints = ['get_status', 'login_api', 'setup', 'login', 'static']
    if request.endpoint in public_endpoints or request.path.startswith('/static'):
        return

    # 2. Nếu chưa khởi tạo vault -> Bắt buộc vào setup
    if not auth.is_vault_initialized():
        if request.path.startswith('/api'):
            return jsonify({"error": "init_required"}), 403
        return redirect(url_for('setup'))

    # 3. Nếu chưa đăng nhập -> Chặn truy cập
    if 'master_key' not in session:
        # Nếu là request từ API/Extension
        if request.path.startswith('/api') or request.path.startswith('/view') or request.path.startswith('/delete'):
            return jsonify({"error": "unauthorized"}), 401
        # Nếu là request từ trình duyệt web
        return redirect(url_for('login'))

# --- CÁC API JSON CHO EXTENSION ---

@app.route('/api/status')
def get_status():
    return jsonify({"initialized": auth.is_vault_initialized(), "logged_in": 'master_key' in session})

@app.route('/api/login', methods=['POST'])
def login_api():
    """API đăng nhập dành riêng cho Extension"""
    mk = request.form.get('master_key')
    if auth.verify_master_key(mk):
        session.clear()
        session['master_key'] = mk
        return jsonify({"status": "success"})
    return jsonify({"status": "fail"}), 401

@app.route('/api/vault')
def get_vault_api():
    return jsonify(manager.get_all_entries())

@app.route('/api/add', methods=['POST'])
def add_api():
    if 'master_key' not in session: return jsonify({"error": "unauthorized"}), 401
    service, user, pwd = request.form.get('service'), request.form.get('username'), request.form.get('password')
    if manager.add_password_entry(session['master_key'], service, user, pwd):
        return jsonify({"status": "success"})
    return jsonify({"status": "fail"}), 400

# --- ROUTES CHO WEB LOCAL ---

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập cho giao diện Web"""
    if 'master_key' in session: 
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        mk = request.form.get('master_key')
        if auth.verify_master_key(mk):
            session.clear()
            session['master_key'] = mk
            return redirect(url_for('dashboard'))
        flash("Khóa Chủ không chính xác!")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', entries=manager.get_all_entries())

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if auth.is_vault_initialized(): 
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        mk = request.form.get('master_key')
        auth.init_vault(mk)
        # Hỗ trợ cả Web (redirect) và Extension (JSON)
        if request.path.startswith('/api') or request.headers.get('X-Requested-With'):
            return jsonify({"status": "success"})
        return redirect(url_for('login'))
    return render_template('setup.html')

# --- THAO TÁC DỮ LIỆU ---

@app.route('/view/<string:entry_id>')
def view_pass(entry_id):
    if 'master_key' not in session: return jsonify({"error": "unauthorized"}), 401
    password = manager.get_decrypted_password(session['master_key'], entry_id)
    return jsonify({"password": password}) if password else (jsonify({"error": "fail"}), 400)

@app.route('/add')
def add_page():
    """Hiển thị giao diện thêm mật khẩu trên Web"""
    if 'master_key' not in session:
        return redirect(url_for('login'))
    return render_template('add_entry.html') 

@app.route('/delete/<string:entry_id>')
def delete_entry(entry_id):
    if 'master_key' not in session: return jsonify({"error": "unauthorized"}), 401
    if manager.delete_password_entry(entry_id):
        return jsonify({"status": "success"})
    return jsonify({"status": "fail"}), 400

@app.route('/logout')
def logout():
    session.clear()
    # Nếu gọi từ Extension
    if request.headers.get('X-Requested-With') or request.path.startswith('/api'):
        return jsonify({"status": "success"})
    return redirect(url_for('login'))

@app.route('/api/generate')
def api_generate():
    mode = request.args.get('mode', 'complex')
    pwd = generator.generate_passphrase() if mode == 'passphrase' else generator.generate_complex_password()
    return jsonify({"password": pwd})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
