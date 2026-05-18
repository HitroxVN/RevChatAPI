export async function loadTemplate(containerId, templateName) {
    try {
        const response = await fetch(`/admin/assets/templates/${templateName}.html`);
        const html = await response.text();
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = html;
        }
    } catch (error) {
        console.error(`Lỗi khi nạp template ${templateName}:`, error);
    }
}

export function initIcons() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

export function showAlert(message, type) {
    if (document.getElementById('loginSection').style.display !== 'none') {
        const alert = document.getElementById('loginError');
        if (alert) {
            alert.textContent = message;
            alert.classList.remove('hidden');
            setTimeout(() => alert.classList.add('hidden'), 3000);
        }
    } else {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-8 right-8 p-4 rounded-lg shadow-2xl z-[200] flex items-center gap-3 border ${
            type === 'success' 
            ? 'bg-green-500/10 border-green-500/20 text-green-500' 
            : 'bg-red-500/10 border-red-500/20 text-red-500'
        }`;
        toast.innerHTML = `
            <i data-lucide="${type === 'success' ? 'check-circle' : 'alert-circle'}" class="w-5 h-5"></i>
            <span class="font-medium text-sm">${message}</span>
        `;
        document.body.appendChild(toast);
        initIcons();
        setTimeout(() => toast.remove(), 4000);
    }
}

export function showSection(sectionId) {
    const sections = ['keysSection', 'accountSection', 'testSection'];
    const sidebarItems = document.querySelectorAll('.sidebar-item');

    sections.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    });

    sidebarItems.forEach(item => item.classList.remove('active'));

    const activeSection = document.getElementById(`${sectionId}Section`);
    if (activeSection) activeSection.classList.remove('hidden');

    // Cập nhật trạng thái sidebar
    const indexMap = { 'keys': 0, 'account': 1, 'test': 2 };
    if (sidebarItems[indexMap[sectionId]]) {
        sidebarItems[indexMap[sectionId]].classList.add('active');
    }

    initIcons();
}
