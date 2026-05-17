import { showAlert, initIcons } from './ui.js';

export async function loadModels() {
    try {
        const response = await fetch(`${window.location.origin}/v1/models`);
        const data = await response.json();
        const modelSelect = document.getElementById('testModel');
        
        if (data.data && data.data.length > 0) {
            modelSelect.innerHTML = '';
            data.data.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.id;
                modelSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Lỗi khi tải model:', error);
    }
}

export async function sendTestMessage() {
    const apiKey = document.getElementById('testApiKey').value;
    const model = document.getElementById('testModel').value;
    const message = document.getElementById('testMessage').value.trim();
    const responseDiv = document.getElementById('testResponse');
    const responseStatus = document.getElementById('responseStatus');
    const sendBtn = document.getElementById('sendBtn');

    if (!apiKey) {
        showAlert('Vui lòng chọn một API Key', 'error');
        return;
    }
    if (!message) {
        showAlert('Vui lòng nhập nội dung tin nhắn', 'error');
        return;
    }

    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Đang thực thi...</span>';
    responseDiv.textContent = 'Đang chờ phản hồi...';
    responseDiv.classList.add('text-neutral-500');
    responseStatus.classList.add('hidden');
    responseStatus.classList.remove('bg-green-500/20', 'text-green-500', 'bg-red-500/20', 'text-red-500');
    initIcons();

    try {
        const response = await fetch(`${window.location.origin}/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: model,
                messages: [{ role: 'user', content: message }]
            })
        });

        const data = await response.json();
        responseStatus.textContent = `TRẠNG THÁI: ${response.status} ${response.statusText}`;
        responseStatus.classList.remove('hidden', 'bg-neutral-800', 'text-neutral-400', 'bg-green-500/20', 'text-green-500', 'bg-red-500/20', 'text-red-500');
        
        if (response.ok) {
            responseStatus.classList.add('bg-green-500/20', 'text-green-500');
            responseDiv.textContent = JSON.stringify(data, null, 2);
            responseDiv.classList.remove('text-neutral-500', 'text-red-500');
            responseDiv.classList.add('text-green-400');
        } else {
            responseStatus.classList.add('bg-red-500/20', 'text-red-500');
            responseDiv.textContent = JSON.stringify(data, null, 2);
            responseDiv.classList.remove('text-neutral-500', 'text-green-400');
            responseDiv.classList.add('text-red-400');
        }
    } catch (error) {
        responseDiv.textContent = `Lỗi: ${error.message}`;
        responseDiv.classList.add('text-red-500');
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<span>Thực thi Request</span><i data-lucide="zap" class="w-6 h-6"></i>';
        initIcons();
    }
}
