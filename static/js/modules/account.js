import { apiFetch } from './api.js';
import { showAlert, initIcons } from './ui.js';

export async function loadChatXAccount() {
    try {
        const response = await apiFetch('/chatx/account');
        if (!response) return;

        const data = await response.json();
        if (data.success) {
            document.getElementById('chatxEmail').value = data.account.email;
            document.getElementById('chatxPassword').value = data.account.password;
            document.getElementById('chatxAutoClear').checked = data.account.auto_clear_history;
        }
    } catch (error) {
        console.error('Lỗi khi tải tài khoản ChatX:', error);
    }
}

export async function updateChatXAccount() {
    const email = document.getElementById('chatxEmail').value.trim();
    const password = document.getElementById('chatxPassword').value.trim();
    const auto_clear_history = document.getElementById('chatxAutoClear').checked;
    const btn = document.getElementById('saveAccountBtn');

    if (!email || !password) {
        showAlert('Vui lòng nhập cả email và mật khẩu', 'error');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Đang lưu...</span>';
    initIcons();

    try {
        const response = await apiFetch('/chatx/account/update', {
            method: 'POST',
            body: JSON.stringify({ email, password, auto_clear_history })
        });
        if (!response) return;

        const data = await response.json();
        if (data.success) {
            showAlert('Đã cập nhật tài khoản ChatX', 'success');
        } else {
            showAlert(data.message || 'Cập nhật thất bại', 'error');
        }
    } catch (error) {
        showAlert('Lỗi kết nối', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="save" class="w-4 h-4"></i><span>Lưu Cấu hình</span>';
        initIcons();
    }
}
