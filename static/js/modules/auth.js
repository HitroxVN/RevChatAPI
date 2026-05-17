import { showAlert, initIcons } from './ui.js';
import { API_BASE } from './api.js';

export async function login() {
    const adminKeyInput = document.getElementById('adminKey');
    const loginBtn = document.querySelector('#loginSection button');
    const adminKey = adminKeyInput.value.trim();
    
    if (!adminKey) {
        showAlert('Vui lòng nhập admin key', 'error');
        return;
    }

    // Hiển thị trạng thái đang kiểm tra
    const originalBtnContent = loginBtn.innerHTML;
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i><span>Đang xác thực...</span>';
    initIcons();

    try {
        const response = await fetch(`${API_BASE}/keys`, {
            headers: { 'Authorization': `Bearer ${adminKey}` }
        });

        if (response.ok) {
            localStorage.setItem('adminKey', adminKey);
            window.location.reload();
        } else if (response.status === 401) {
            showAlert('Admin key không chính xác', 'error');
        } else {
            showAlert('Lỗi hệ thống khi xác thực', 'error');
        }
    } catch (error) {
        showAlert('Không thể kết nối đến server', 'error');
    } finally {
        loginBtn.disabled = false;
        loginBtn.innerHTML = originalBtnContent;
        initIcons();
    }
}

export function logout() {
    localStorage.removeItem('adminKey');
    window.location.reload();
}

export function checkLoginState() {
    const adminKey = localStorage.getItem('adminKey');
    const loginSection = document.getElementById('loginSection');
    const dashboardSection = document.getElementById('dashboardSection');
    
    if (adminKey) {
        if (loginSection) loginSection.style.display = 'none';
        if (dashboardSection) {
            dashboardSection.classList.remove('hidden');
            dashboardSection.classList.add('flex');
        }
        return true;
    } else {
        if (loginSection) loginSection.style.display = 'flex';
        if (dashboardSection) {
            dashboardSection.classList.add('hidden');
            dashboardSection.classList.remove('flex');
        }
        return false;
    }
}
