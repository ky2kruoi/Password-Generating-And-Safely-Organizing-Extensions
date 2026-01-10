const FLASK_URL = 'http://127.0.0.1:5000';

// 1. KIỂM TRA TRẠNG THÁI
async function checkStatus() {
    try {
        const res = await fetch(`${FLASK_URL}/api/status`, { credentials: 'include' });
        const data = await res.json();
        if (!data.initialized) showSection('setup-section');
        else if (!data.logged_in) showSection('login-section');
        else { showSection('vault-section'); showVault(); }
    } catch (e) { document.getElementById('error-msg').innerText = "Lỗi: Hãy chạy app.py!"; }
}

function showSection(id) {
    ['setup-section', 'login-section', 'vault-section'].forEach(s => {
        document.getElementById(s).style.display = (s === id) ? 'block' : 'none';
    });
}

// 2. KHỞI TẠO (SETUP)
document.getElementById('setup-btn').onclick = async () => {
    const mk = document.getElementById('setup-key').value;
    const mkc = document.getElementById('setup-confirm').value;
    if (mk !== mkc) return alert("Khóa Chủ không khớp!");
    
    const fd = new URLSearchParams(); fd.append('master_key', mk);
    const res = await fetch(`${FLASK_URL}/setup`, { method: 'POST', body: fd });
    if (res.ok) { 
        alert("Khởi tạo thành công!"); 
        document.getElementById('setup-key').value = '';
        document.getElementById('setup-confirm').value = '';
        checkStatus(); 
    }
};

// 3. ĐĂNG NHẬP & ĐĂNG XUẤT (CÓ XÓA INPUT)
document.getElementById('login-btn').onclick = async () => {
    const mkInput = document.getElementById('master-key-input');
    const fd = new URLSearchParams(); fd.append('master_key', mkInput.value);
    const res = await fetch(`${FLASK_URL}/api/login`, { method: 'POST', body: fd, credentials: 'include' });
    if (res.ok) { mkInput.value = ''; checkStatus(); } else alert("Sai Khóa Chủ!");
};

document.getElementById('logout-btn').onclick = async () => {
    await fetch(`${FLASK_URL}/logout`, { credentials: 'include' });
    document.getElementById('master-key-input').value = ''; // XÓA SẠCH Ô ĐIỀN KHÓA CHỦ
    checkStatus();
};

// 4. HIỂN THỊ VAULT (SỬ DỤNG ID UUID)
async function showVault() {
    const list = document.getElementById('password-list');
    const res = await fetch(`${FLASK_URL}/api/vault`, { credentials: 'include' });
    const entries = await res.json();
    list.innerHTML = entries.length ? '' : '<p style="text-align:center;font-size:12px;">Kho trống.</p>';

    entries.forEach(entry => {
        const item = document.createElement('div');
        item.className = 'entry-item';
        item.innerHTML = `<div><strong>${entry.service_name}</strong><br><small>${entry.username}</small></div>`;
        
        const actions = document.createElement('div');
        actions.className = 'entry-actions';

        const vBtn = document.createElement('button'); vBtn.className = 'btn-sm'; vBtn.innerText = 'Xem';
        vBtn.onclick = () => viewPass(entry.id);

        const dBtn = document.createElement('button'); dBtn.className = 'btn-delete-small'; dBtn.innerText = 'Xóa';
        dBtn.onclick = () => deletePass(entry.id, entry.service_name);

        actions.append(vBtn, dBtn);
        item.append(actions);
        list.appendChild(item);
    });
}

// 5. CÁC HÀM XỬ LÝ KHÁC (Tạo, Lưu, View, Delete)
async function viewPass(id) {
    try {
        const res = await fetch(`${FLASK_URL}/view/${id}`, { credentials: 'include' });
        const data = await res.json();
        
        if (data.password) {
            // Tự động sao chép mật khẩu vào bộ nhớ tạm (Clipboard)
            navigator.clipboard.writeText(data.password).then(() => {
                alert("Mật khẩu: " + data.password + "\n\n(Hệ thống đã tự động sao chép vào bộ nhớ tạm!)");
            }).catch(err => {
                // Trường hợp trình duyệt chặn quyền truy cập clipboard
                alert("Mật khẩu: " + data.password);
            });
        } else {
            alert("Lỗi: Không thể lấy mật khẩu!");
        }
    } catch (err) {
        alert("Lỗi kết nối server!");
    }
}

async function deletePass(id, name) {
    if (confirm(`Xóa mật khẩu ${name}?`)) {
        await fetch(`${FLASK_URL}/delete/${id}`, { credentials: 'include' });
        showVault();
    }
}

document.getElementById('ext-gen-btn').onclick = async () => {
    const mode = document.getElementById('ext-password-type').value;
    const res = await fetch(`${FLASK_URL}/api/generate?mode=${mode}`);
    const data = await res.json();
    document.getElementById('ext-password-field').value = data.password;
};

document.getElementById('ext-save-btn').onclick = async () => {
    const s = document.getElementById('ext-service').value, u = document.getElementById('ext-username').value, p = document.getElementById('ext-password-field').value;
    if (!s || !p) return alert("Nhập đủ thông tin!");
    const fd = new URLSearchParams(); fd.append('service', s); fd.append('username', u); fd.append('password', p);
    const res = await fetch(`${FLASK_URL}/api/add`, { method: 'POST', body: fd, credentials: 'include' });
    if (res.ok) { 
        alert("Đã lưu!"); 
        document.getElementById('ext-service').value = ''; 
        document.getElementById('ext-password-field').value = ''; 
        switchTab('list'); 
    }
};

function switchTab(name) {
    document.getElementById('list-content').style.display = (name === 'list' ? 'block' : 'none');
    document.getElementById('gen-content').style.display = (name === 'gen' ? 'block' : 'none');
    document.getElementById('tab-list').classList.toggle('active', name === 'list');
    document.getElementById('tab-gen').classList.toggle('active', name === 'gen');
    if (name === 'list') showVault();
}
document.getElementById('tab-list').onclick = () => switchTab('list');
document.getElementById('tab-gen').onclick = () => switchTab('gen');

checkStatus();