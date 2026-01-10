from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from backend import auth, crypto_utils, generator
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chia_khoa_bi_mat_cua_rieng_ban_2024'

# Cấu hình CORS và Cookie để chạy mượt trên Edge/Chrome
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
)

@app.route('/')
def index():
    if 'master_key' in session: return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    mk = request.form.get('master_key')
    data = auth.load_vault()
    try:
        auth.ph.verify(data['security_metadata']['master_key_hash'], mk)
        session['master_key'] = mk
        return redirect(url_for('dashboard'))
    except Exception: return "Sai mật khẩu! <a href='/'>Thử lại</a>"

@app.route('/dashboard')
def dashboard():
    if 'master_key' not in session: return redirect(url_for('index'))
    data = auth.load_vault()
    return render_template('dashboard.html', entries=data['entries'])

# API phục vụ Extension
@app.route('/api/generate')
def api_generate():
    mode = request.args.get('mode', 'complex')
    pass_str = generator.generate_passphrase(5, "-") if mode == 'passphrase' else generator.generate_complex_password(16)
    return jsonify({"password": pass_str})

@app.route('/login_api', methods=['POST'])
def login_api():
    mk = request.form.get('master_key')
    data = auth.load_vault()
    try:
        auth.ph.verify(data['security_metadata']['master_key_hash'], mk)
        session['master_key'] = mk
        session.modified = True 
        return jsonify({"status": "success"})
    except: return jsonify({"status": "fail"}), 401

@app.route('/dashboard_api')
def dashboard_api():
    if 'master_key' not in session: return jsonify({"error": "Unauthorized"}), 403
    data = auth.load_vault()
    return jsonify({"entries": data['entries']})

@app.route('/add_api', methods=['POST'])
def add_api():
    if 'master_key' not in session: return jsonify({"error": "Unauthorized"}), 403
    service, username, password = request.form.get('service'), request.form.get('username'), request.form.get('password')
    encrypted_payload = crypto_utils.encrypt_data(session['master_key'], password)
    data = auth.load_vault()
    data['entries'].append({"service_name": service, "username": username, "encrypted_data": encrypted_payload, "created_at": datetime.now().isoformat()})
    auth.save_vault(data)
    return jsonify({"status": "success"})

@app.route('/delete_api/<int:idx>', methods=['POST'])
def delete_api(idx):
    """API xóa mật khẩu dành riêng cho Extension"""
    if 'master_key' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = auth.load_vault()
    if 0 <= idx < len(data['entries']):
        # Xóa mục dựa trên chỉ số (index)
        removed = data['entries'].pop(idx)
        auth.save_vault(data) # Lưu lại file vault.json
        return jsonify({"status": "success", "message": f"Đã xóa {removed['service_name']}"})
    
    return jsonify({"status": "fail", "message": "Không tìm thấy mục cần xóa"}), 400

@app.route('/view/<int:idx>')
def view_pass(idx):
    if 'master_key' not in session: return jsonify({"error": "Unauthorized"}), 401
    data = auth.load_vault()
    password = crypto_utils.decrypt_data(session['master_key'], data['entries'][idx]['encrypted_data'])
    return jsonify({"password": password})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)