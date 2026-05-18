import { apiFetch } from './api.js';
import { showAlert, initIcons } from './ui.js';

let currentProvider = null;
let currentAccountId = null;
let allAccounts = {
    chatx: [],
    easemate: []
};

export function createNewAccount() {
    openAccountModal(currentProvider, null);
}

export function openAccountModal(provider, accountId = null) {
    currentProvider = provider;
    currentAccountId = accountId;
    
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

    // Clear inputs if adding new
    if (!accountId) {
        if (provider === 'chatx') {
            document.getElementById('chatxEmail').value = '';
            document.getElementById('chatxPassword').value = '';
            document.getElementById('chatxAutoClear').checked = false;
        } else {
            document.getElementById('easemateUuid').value = '';
            document.getElementById('easemateIdentity').value = '';
        }
    } else {
        // Fill inputs with existing data
        const account = allAccounts[provider].find(a => a.id === accountId);
        if (account) {
            if (provider === 'chatx') {
                document.getElementById('chatxEmail').value = account.email || '';
                document.getElementById('chatxPassword').value = ''; // Don't show password
                document.getElementById('chatxAutoClear').checked = account.auto_clear_history || false;
            } else {
                document.getElementById('easemateUuid').value = account.device_uuid || '';
                document.getElementById('easemateIdentity').value = account.identity_id || '';
            }
        }
    }
    
    if (provider === 'chatx') {
        title.textContent = accountId ? 'Sửa ChatX' : 'Thêm ChatX';
        subtitle.textContent = 'Quản lý tài khoản DeepSeek, Claude, GPT...';
        iconContainer.className = 'p-3 bg-yellow-500/10 rounded-2xl';
        icon.setAttribute('data-lucide', 'shield-check');
        chatxFields.classList.remove('hidden');
    } else {
        title.textContent = accountId ? 'Sửa EaseMate' : 'Thêm EaseMate';
        subtitle.textContent = 'Cấu hình Device UUID và Identity ID.';
        iconContainer.className = 'p-3 bg-blue-500/10 rounded-2xl';
        icon.setAttribute('data-lucide', 'cpu');
        easemateFields.classList.remove('hidden');
        verifyBtn.classList.remove('hidden');
    }

    modal.classList.remove('hidden');
    initIcons();
}

export async function loadAllAccounts() {
    try {
        const [chatxRes, easemateRes] = await Promise.all([
            apiFetch('/chatx/accounts'),
            apiFetch('/easemate/accounts')
        ]);
        
        if (chatxRes) {
            const data = await chatxRes.json();
            allAccounts.chatx = data.accounts || [];
        }
        
        if (easemateRes) {
            const data = await easemateRes.json();
            allAccounts.easemate = data.accounts || [];
        }
        
        renderAccountList();
    } catch (error) {
        console.error('Lỗi khi tải danh sách tài khoản:', error);
    }
}

export function selectProvider(provider) {
    currentProvider = provider;
    document.getElementById('providerView').classList.add('hidden');
    document.getElementById('accountListView').classList.remove('hidden');
    
    const title = document.getElementById('selectedProviderTitle');
    const subtitle = document.getElementById('selectedProviderSubtitle');
    
    if (provider === 'chatx') {
        title.textContent = 'ChatX Accounts';
        subtitle.textContent = 'Danh sách các tài khoản Email/Password của ChatX.';
    } else {
        title.textContent = 'EaseMate Accounts';
        subtitle.textContent = 'Danh sách các cặp Device UUID và Identity ID của EaseMate.';
    }
    
    renderAccountList();
}

export function backToProviders() {
    currentProvider = null;
    document.getElementById('providerView').classList.remove('hidden');
    document.getElementById('accountListView').classList.add('hidden');
    initIcons();
}

function renderAccountList() {
    const container = document.getElementById('accountList');
    if (!container) return;
    container.innerHTML = '';
    
    if (!currentProvider) return;

    // Chỉ render các tài khoản của provider đã chọn
    const accounts = allAccounts[currentProvider] || [];
    
    if (accounts.length === 0) {
        container.innerHTML = `
            <div class="col-span-full p-20 text-center text-neutral-500 bg-white/5 rounded-[32px] border border-dashed border-white/10">
                <i data-lucide="folder-open" class="w-12 h-12 mx-auto mb-4 opacity-20"></i>
                <p class="text-lg font-medium">Chưa có tài khoản nào được thêm cho Provider này.</p>
                <button onclick="createNewAccount()" class="mt-6 text-yellow-500 font-bold hover:underline">Thêm tài khoản ngay</button>
            </div>
        `;
    } else {
        accounts.forEach(acc => {
            const card = createAccountCard(currentProvider, acc);
            container.appendChild(card);
        });
    }
    
    initIcons();
}

function createAccountCard(provider, account) {
    const div = document.createElement('div');
    const isChatX = provider === 'chatx';
    const colorClass = isChatX ? 'yellow' : 'blue';
    const icon = isChatX ? 'shield-check' : 'cpu';
    const title = isChatX ? 'ChatX Account' : 'EaseMate Account';
    const desc = isChatX ? account.email : (account.device_uuid ? account.device_uuid.substring(0, 8) + '...' : 'New Account');

    div.className = `card p-8 shadow-2xl cursor-pointer hover:bg-white/5 transition-all group border border-transparent hover:border-${colorClass}-500/20 relative`;
    div.onclick = () => openAccountModal(provider, account.id);
    
    div.innerHTML = `
        <div class="flex items-center justify-between mb-4">
            <div class="p-3 bg-${colorClass}-500/10 rounded-2xl group-hover:scale-110 transition-transform">
                <i data-lucide="${icon}" class="w-8 h-8 text-${colorClass}-500"></i>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="event.stopPropagation(); deleteAccount('${provider}', '${account.id}')" class="p-2 text-neutral-500 hover:text-red-500 transition-colors">
                    <i data-lucide="trash-2" class="w-5 h-5"></i>
                </button>
                <div class="text-neutral-500 group-hover:text-${colorClass}-500 transition-colors">
                    <i data-lucide="edit-3" class="w-6 h-6"></i>
                </div>
            </div>
        </div>
        <h3 class="text-2xl font-bold text-white tracking-tight">${title}</h3>
        <p class="text-sm text-neutral-400 mt-2 truncate max-w-full">${desc}</p>
    `;
    
    return div;
}

export async function deleteAccount(provider, id) {
    if (!confirm('Bạn có chắc chắn muốn xóa tài khoản này?')) return;
    
    try {
        const response = await apiFetch(`/${provider}/account/delete`, {
            method: 'POST',
            body: JSON.stringify({ id })
        });
        
        if (response) {
            const data = await response.json();
            if (data.success) {
                showAlert('Đã xóa tài khoản', 'success');
                await loadAllAccounts();
            } else {
                showAlert('Không thể xóa tài khoản', 'error');
            }
        }
    } catch (error) {
        showAlert('Lỗi kết nối', 'error');
    }
}

export function closeAccountModal() {
    const modal = document.getElementById('accountModal');
    if (modal) modal.classList.add('hidden');
    // currentProvider = null; // Bỏ dòng này để giữ ngữ cảnh provider hiện tại
}

export async function saveAccountChanges() {
    if (currentProvider === 'chatx') {
        await saveChatXAccount();
    } else if (currentProvider === 'easemate') {
        await saveEaseMateAccount();
    }
}

async function saveChatXAccount() {
    const email = document.getElementById('chatxEmail').value.trim();
    const password = document.getElementById('chatxPassword').value.trim();
    const auto_clear_history = document.getElementById('chatxAutoClear').checked;
    const btn = document.getElementById('accountSaveBtn');

    if (!email || (!currentAccountId && !password)) {
        showAlert('Vui lòng nhập đầy đủ thông tin', 'error');
        return;
    }

    btn.disabled = true;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-6 h-6 animate-spin"></i><span>Đang lưu...</span>';
    initIcons();

    try {
        const response = await apiFetch('/chatx/account/save', {
            method: 'POST',
            body: JSON.stringify({ id: currentAccountId, email, password, auto_clear_history })
        });
        
        if (response) {
            const data = await response.json();
            if (data.success) {
                showAlert('Đã lưu tài khoản ChatX', 'success');
                closeAccountModal();
                await loadAllAccounts();
            } else {
                showAlert('Lưu thất bại', 'error');
            }
        }
    } catch (error) {
        showAlert('Lỗi kết nối', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
        initIcons();
    }
}

async function saveEaseMateAccount() {
    const device_uuid = document.getElementById('easemateUuid').value.trim();
    const identity_id = document.getElementById('easemateIdentity').value.trim();
    const btn = document.getElementById('accountSaveBtn');

    if (!device_uuid || !identity_id) {
        showAlert('Vui lòng nhập đầy đủ thông tin', 'error');
        return;
    }

    btn.disabled = true;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-6 h-6 animate-spin"></i><span>Đang lưu...</span>';
    initIcons();

    try {
        const response = await apiFetch('/easemate/account/save', {
            method: 'POST',
            body: JSON.stringify({ id: currentAccountId, device_uuid, identity_id })
        });
        
        if (response) {
            const data = await response.json();
            if (data.success) {
                showAlert('Đã lưu tài khoản EaseMate', 'success');
                closeAccountModal();
                await loadAllAccounts();
            } else {
                showAlert('Lưu thất bại', 'error');
            }
        }
    } catch (error) {
        showAlert('Lỗi kết nối', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
        initIcons();
    }
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

export async function showEaseMateInstructions() {
    const container = document.getElementById('easemateInstructions');
    const codeBlock = document.getElementById('easemateScriptCode');
    
    if (!container || container.classList.contains('hidden') === false) {
        if (container) container.classList.add('hidden');
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
    const codeBlock = document.getElementById('easemateScriptCode');
    if (!codeBlock) return;
    const code = codeBlock.textContent;
    try {
        await navigator.clipboard.writeText(code);
        showAlert('Đã sao chép script vào bộ nhớ tạm', 'success');
    } catch (err) {
        showAlert('Không thể sao chép tự động', 'error');
    }
}

