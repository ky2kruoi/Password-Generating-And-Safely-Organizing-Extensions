const FLASK_URL = 'http://127.0.0.1:5000';

// ==========================================
// 1. QUẢN LÝ ĐĂNG NHẬP
// ==========================================
document.getElementById('login-btn').addEventListener('click', async () => {
    const mk = document.getElementById('master-key-input').value;
    const errorMsg = document.getElementById('error-msg');
    errorMsg.innerText = "Đang xác thực...";

    try {
        const response = await fetch(`${FLASK_URL}/login_api`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `master_key=${encodeURIComponent(mk)}`,
            credentials: 'include' 
        });

        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('login-section').style.display = 'none';
            document.getElementById('vault-section').style.display = 'block';
            showVault(); 
        } else {
            errorMsg.innerText = "Sai Khóa Chủ!";
        }
    } catch (err) {
        errorMsg.innerText = "Lỗi kết nối: Hãy chạy app.py!";
    }
});

// ==========================================
// 2. QUẢN LÝ TAB
// ==========================================
function switchTab(name) {
    document.getElementById('tab-list').classList.toggle('active', name === 'list');
    document.getElementById('tab-gen').classList.toggle('active', name === 'gen');
    document.getElementById('list-content').style.display = name === 'list' ? 'block' : 'none';
    document.getElementById('gen-content').style.display = name === 'gen' ? 'block' : 'none';
    if (name === 'list') showVault();
}

document.getElementById('tab-list').addEventListener('click', () => switchTab('list'));
document.getElementById('tab-gen').addEventListener('click', () => switchTab('gen'));

// ==========================================
// 3. HIỂN THỊ DANH SÁCH & XEM
// ==========================================
async function showVault() {
    const listContainer = document.getElementById('password-list');
    try {
        const response = await fetch(`${FLASK_URL}/dashboard_api`, { credentials: 'include' });
        if (response.status === 403) return;

        const data = await response.json();
        listContainer.innerHTML = '';

        if (data.entries.length === 0) {
            listContainer.innerHTML = '<p style="text-align:center; color:#666; font-size:12px;">Kho đang trống.</p>';
            return;
        }

        data.entries.forEach((entry, index) => {
            const item = document.createElement('div');
            item.className = 'entry-item';
            
            item.innerHTML = `
                <div style="text-align:left; flex-grow:1;">
                    <strong>${entry.service_name}</strong><br>
                    <small>${entry.username}</small>
                </div>
            `;

            const actionDiv = document.createElement('div');
            actionDiv.style.display = 'flex';
            actionDiv.style.gap = '5px';

            const viewBtn = document.createElement('button');
            viewBtn.className = 'btn';
            viewBtn.style.width = 'auto';
            viewBtn.style.padding = '5px 10px';
            viewBtn.innerText = 'Xem';
            viewBtn.addEventListener('click', () => viewPass(index));

            const delBtn = document.createElement('button');
            delBtn.className = 'btn btn-danger';
            delBtn.style.width = 'auto';
            delBtn.style.padding = '5px 10px';
            delBtn.innerText = 'Xóa';
            delBtn.addEventListener('click', () => deletePass(index, entry.service_name));

            actionDiv.appendChild(viewBtn);
            actionDiv.appendChild(delBtn);
            item.appendChild(actionDiv);
            listContainer.appendChild(item);
        });
    } catch (err) {
        listContainer.innerHTML = '<p class="error">Lỗi tải dữ liệu!</p>';
    }
}

async function viewPass(idx) {
    try {
        const response = await fetch(`${FLASK_URL}/view/${idx}`, { credentials: 'include' });
        const data = await response.json();
        if (data.password) {
            alert(`Mật khẩu cho mục này là: ${data.password}`);
        }
    } catch (err) { alert("Lỗi kết nối!"); }
}

// ==========================================
// 4. XÓA MẬT KHẨU
// ==========================================
async function deletePass(idx, serviceName) {
    if (!confirm(`Bạn có chắc muốn xóa mật khẩu của ${serviceName}?`)) return;

    try {
        const response = await fetch(`${FLASK_URL}/delete_api/${idx}`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await response.json();

        if (data.status === 'success') {
            showVault(); 
        } else {
            alert("Lỗi: " + data.message);
        }
    } catch (err) { alert("Lỗi khi kết nối để xóa!"); }
}

// ==========================================
// 5. TẠO & LƯU MẬT KHẨU MỚI
// ==========================================
document.getElementById('ext-gen-btn').addEventListener('click', async () => {
    const mode = document.getElementById('ext-password-type').value;
    const passField = document.getElementById('ext-password-field');
    try {
        const response = await fetch(`${FLASK_URL}/api/generate?mode=${mode}`, { credentials: 'include' });
        const data = await response.json();
        if (data.password) {
            passField.value = data.password;
        }
    } catch (err) { alert("Lỗi tạo mật khẩu!"); }
});

document.getElementById('ext-save-btn').addEventListener('click', async () => {
    const s = document.getElementById('ext-service').value;
    const u = document.getElementById('ext-username').value;
    const p = document.getElementById('ext-password-field').value;
    const status = document.getElementById('save-status');

    if (!s || !p) {
        alert("Thiếu thông tin dịch vụ hoặc mật khẩu!");
        return;
    }

    try {
        const formData = new URLSearchParams();
        formData.append('service', s);
        formData.append('username', u);
        formData.append('password', p);

        const response = await fetch(`${FLASK_URL}/add_api`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        const data = await response.json();

        if (data.status === 'success') {
            status.innerText = "✅ Lưu thành công!";
            document.getElementById('ext-service').value = "";
            document.getElementById('ext-username').value = "";
            document.getElementById('ext-password-field').value = "";
            setTimeout(() => { status.innerText = ""; switchTab('list'); }, 1500);
        }
    } catch (err) { alert("Lỗi khi lưu!"); }
});

// ==========================================
// 6. ĐĂNG XUẤT
// ==========================================
document.getElementById('logout-btn').addEventListener('click', async () => {
    await fetch(`${FLASK_URL}/logout`, { credentials: 'include' });
    location.reload();
});