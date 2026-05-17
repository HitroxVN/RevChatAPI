import { apiFetch } from './api.js';
import { showAlert, initIcons } from './ui.js';

let isEditing = false;

export async function loadKeys() {
    try {
        const loading = document.getElementById('loading');
        if (loading) loading.classList.remove('hidden');
        
        const response = await apiFetch('/keys');
        if (!response) return;

        const data = await response.json();
        const container = document.getElementById('keysContainer');
        const testKeySelect = document.getElementById('testApiKey');
        
        container.innerHTML = '';
        if (testKeySelect) {
            testKeySelect.innerHTML = '<option value="">Chọn một API key...</option>';
        }

        const keys = data.keys || [];
        document.getElementById('apiKeyCount').textContent = keys.length;
        document.getElementById('statKeys').textContent = keys.length;

        if (keys.length > 0) {
            keys.forEach(key => {
                if (testKeySelect) {
                    const option = document.createElement('option');
                    option.value = key.key;
                    option.textContent = `${key.name} (${key.key.substring(0, 12)}...)`;
                    testKeySelect.appendChild(option);
                }

                const keyRow = document.createElement('div');
                keyRow.className = 'p-6 hover:bg-white/5 flex items-center justify-between group transition-all border-b border-white/5 last:border-0';
                keyRow.innerHTML = `
                    <div class="flex-1">
                        <div class="flex items-center gap-4">
                            <span class="font-bold text-white text-lg tracking-tight">${key.name}</span>
                            <span class="px-3 py-1 bg-white/5 text-neutral-400 text-xs rounded-full font-mono select-all border border-white/5 backdrop-blur-sm">${key.key}</span>
                        </div>
                        <div class="text-sm text-neutral-500 mt-2 flex items-center gap-6 font-medium">
                            <span class="flex items-center gap-2">
                                <i data-lucide="info" class="w-4 h-4 text-neutral-600"></i>
                                ${key.description || 'Chưa thêm ghi chú'}
                            </span>
                            <span class="flex items-center gap-2">
                                <i data-lucide="calendar" class="w-4 h-4 text-neutral-600"></i>
                                ${new Date(key.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                            </span>
                        </div>
                    </div>
                    <div class="flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-all transform translate-x-4 group-hover:translate-x-0">
                        <button class="btn-copy p-3 text-neutral-400 hover:text-white hover:bg-white/10 rounded-xl transition-all" data-key="${key.key}" title="Sao chép Key">
                            <i data-lucide="copy" class="w-5 h-5"></i>
                        </button>
                        <button class="btn-edit p-3 text-neutral-400 hover:text-yellow-500 hover:bg-yellow-500/10 rounded-xl transition-all" 
                            data-key="${key.key}" data-name="${key.name}" data-desc="${key.description || ''}" title="Chỉnh sửa">
                            <i data-lucide="edit-3" class="w-5 h-5"></i>
                        </button>
                        <button class="btn-delete p-3 text-neutral-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all" data-key="${key.key}" title="Xóa">
                            <i data-lucide="trash-2" class="w-5 h-5"></i>
                        </button>
                    </div>
                `;
                container.appendChild(keyRow);
            });
            attachEventListeners();
        } else {
            container.innerHTML = '<div class="p-12 text-center text-neutral-500 italic text-sm">Chưa có API key nào. Hãy tạo một cái để bắt đầu.</div>';
        }
        initIcons();
    } catch (error) {
        showAlert('Lỗi khi tải dữ liệu: ' + error.message, 'error');
    }
}

function attachEventListeners() {
    document.querySelectorAll('.btn-copy').forEach(btn => {
        btn.onclick = () => copyKey(btn.dataset.key);
    });
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.onclick = () => openEditModal(btn.dataset.key, btn.dataset.name, btn.dataset.desc);
    });
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.onclick = () => deleteKey(btn.dataset.key);
    });
}

export function openCreateModal() {
    isEditing = false;
    document.getElementById('modalTitle').textContent = 'Tạo API Key Mới';
    document.getElementById('modalKeyId').value = '';
    document.getElementById('modalKeyName').value = '';
    document.getElementById('modalKeyDescription').value = '';
    document.getElementById('modalSubmitBtn').textContent = 'Tạo Key';
    document.getElementById('keyModal').classList.remove('hidden');
    initIcons();
}

export function openEditModal(key, name, description) {
    isEditing = true;
    document.getElementById('modalTitle').textContent = 'Chỉnh sửa API Key';
    document.getElementById('modalKeyId').value = key;
    document.getElementById('modalKeyName').value = name;
    document.getElementById('modalKeyDescription').value = description;
    document.getElementById('modalSubmitBtn').textContent = 'Lưu Thay đổi';
    document.getElementById('keyModal').classList.remove('hidden');
    initIcons();
}

export function closeModal() {
    document.getElementById('keyModal').classList.add('hidden');
}

export async function submitModal() {
    const key = document.getElementById('modalKeyId').value;
    const name = document.getElementById('modalKeyName').value.trim();
    const description = document.getElementById('modalKeyDescription').value.trim();

    if (!name) {
        showAlert('Vui lòng nhập tên key', 'error');
        return;
    }

    const endpoint = isEditing ? '/keys/update' : '/keys/create';
    const payload = isEditing ? { key, name, description } : { name, description };

    try {
        const response = await apiFetch(endpoint, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        if (!response) return;

        const data = await response.json();
        if (data.success) {
            showAlert(isEditing ? 'Đã cập nhật key' : 'Tạo key thành công', 'success');
            closeModal();
            loadKeys();
        } else {
            showAlert(data.message || 'Thao tác thất bại', 'error');
        }
    } catch (error) {
        showAlert('Lỗi kết nối', 'error');
    }
}

export async function deleteKey(key) {
    if (!confirm('Bạn có chắc chắn muốn xóa API key này không? Hành động này không thể hoàn tác.')) {
        return;
    }

    try {
        const response = await apiFetch('/keys/delete', {
            method: 'POST',
            body: JSON.stringify({ key })
        });
        if (!response) return;

        const data = await response.json();
        if (data.success) {
            showAlert('Đã xóa API key', 'success');
            loadKeys();
        } else {
            showAlert('Không thể xóa key', 'error');
        }
    } catch (error) {
        showAlert('Lỗi kết nối', 'error');
    }
}

export function copyKey(key) {
    navigator.clipboard.writeText(key).then(() => {
        showAlert('Đã sao chép API Key vào clipboard', 'success');
    });
}
