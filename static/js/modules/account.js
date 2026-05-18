import { apiFetch } from './api.js';
import { showAlert, initIcons } from './ui.js';

let currentProvider = null;

export function openAccountModal(provider) {
    currentProvider = provider;
    const modal = document.getElementById('accountModal');
    const title = document.getElementById('accountModalTitle');
    const subtitle = document.getElementById('accountModalSubtitle');
    const iconContainer = document.getElementById('accountModalIcon');
    const icon = document.getElementById('accountModalLucideIcon');
    
    const chatxFields = document.getElementById('chatxModalFields');
    const easemateFields = document.getElementById('easemateModalFields');
    const verifyBtn = document.getElementById('easemateVerifyBtn');
    
    // Reset views
    chatxFields.classList.add('hidden');
    easemateFields.classList.add('hidden');
    verifyBtn.classList.add('hidden');
    document.getElementById('easemateInstructions').classList.add('hidden');

    if (provider === 'chatx') {
        title.textContent = 'ChatX Provider';
        subtitle.textContent = 'Quản lý tài khoản DeepSeek, Claude, GPT...';
        iconContainer.className = 'p-3 bg-yellow-500/10 rounded-2xl';
        icon.setAttribute('data-lucide', 'shield-check');
        chatxFields.classList.remove('hidden');
    } else {
        title.textContent = 'EaseMate Provider';
        subtitle.textContent = 'Cấu hình Device UUID và Identity ID.';
        iconContainer.className = 'p-3 bg-blue-500/10 rounded-2xl';
        icon.setAttribute('data-lucide', 'cpu');
        easemateFields.classList.remove('hidden');
        verifyBtn.classList.remove('hidden');
    }

    modal.classList.remove('hidden');
    initIcons();
}

export async function verifyEaseMateID() {
    const device_uuid = document.getElementById('easemateUuid').value.trim();
    const identity_id = document.getElementById('easemateIdentity').value.trim();
    const btn = document.getElementById('easemateVerifyBtn');

    if (!device_uuid || !identity_id) {
        showAlert('Vui lòng nhập cả Device UUID và Identity ID', 'error');
        return;
    }

    btn.disabled = true;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i><span>Đang kiểm tra...</span>';
    initIcons();

    try {
        const response = await apiFetch('/easemate/account/verify', {
            method: 'POST',
            body: JSON.stringify({ device_uuid, identity_id })
        });
        
        if (!response) return;
        const data = await response.json();

        if (data.success) {
            showAlert('🎉 ' + data.message, 'success');
        } else {
            showAlert('❌ ' + data.message, 'error');
        }
    } catch (error) {
        showAlert('Lỗi kết nối máy chủ', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
        initIcons();
    }
}

export function closeAccountModal() {
    const modal = document.getElementById('accountModal');
    modal.classList.add('hidden');
    currentProvider = null;
}

export async function saveAccountChanges() {
    if (currentProvider === 'chatx') {
        await updateChatXAccount();
    } else if (currentProvider === 'easemate') {
        await updateEaseMateAccount();
    }
}

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

export async function loadEaseMateAccount() {
    try {
        const response = await apiFetch('/easemate/account');
        if (!response) return;

        const data = await response.json();
        if (data.success) {
            document.getElementById('easemateUuid').value = data.account.device_uuid || '';
            document.getElementById('easemateIdentity').value = data.account.identity_id || '';
        }
    } catch (error) {
        console.error('Lỗi khi tải tài khoản EaseMate:', error);
    }
}

export async function showEaseMateInstructions() {
    const container = document.getElementById('easemateInstructions');
    const codeBlock = document.getElementById('easemateScriptCode');
    
    if (!container.classList.contains('hidden')) {
        container.classList.add('hidden');
        return;
    }

    try {
        const response = await apiFetch('/easemate/script');
        if (!response) return;

        const data = await response.json();
        if (data.success) {
            codeBlock.textContent = data.script;
            container.classList.remove('hidden');
            initIcons();
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        showAlert('Không thể tải hướng dẫn', 'error');
    }
}

export async function copyEaseMateScript() {
    const code = document.getElementById('easemateScriptCode').textContent;
    try {
        await navigator.clipboard.writeText(code);
        showAlert('Đã sao chép script vào bộ nhớ tạm', 'success');
    } catch (err) {
        showAlert('Không thể sao chép tự động', 'error');
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

export async function updateEaseMateAccount() {
    const device_uuid = document.getElementById('easemateUuid').value.trim();
    const identity_id = document.getElementById('easemateIdentity').value.trim();
    const btn = document.getElementById('saveEaseMateBtn');

    if (!device_uuid || !identity_id) {
        showAlert('Vui lòng nhập cả Device UUID và Identity ID', 'error');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Đang lưu...</span>';
    initIcons();

    try {
        const response = await apiFetch('/easemate/account/update', {
            method: 'POST',
            body: JSON.stringify({ device_uuid, identity_id })
        });
        if (!response) return;

        const data = await response.json();
        if (data.success) {
            showAlert('Đã cập nhật tài khoản EaseMate', 'success');
        } else {
            showAlert(data.message || 'Cập nhật thất bại', 'error');
        }
    } catch (error) {
        showAlert('Lỗi kết nối', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="save" class="w-6 h-6"></i><span>Lưu Cấu hình</span>';
        initIcons();
    }
}
