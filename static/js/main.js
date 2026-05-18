import { checkLoginState, login, logout } from './modules/auth.js';
import { initIcons, showSection, loadTemplate } from './modules/ui.js';
import { loadKeys, openCreateModal, closeModal, submitModal } from './modules/keys.js';
import { loadAllAccounts, createNewAccount, deleteAccount, openAccountModal, closeAccountModal, saveAccountChanges, showEaseMateInstructions, copyEaseMateScript, verifyEaseMateID, selectProvider, backToProviders } from './modules/account.js';
import { loadModels, sendTestMessage } from './modules/test.js';

// Gắn các hàm vào đối tượng window để HTML có thể gọi
window.login = login;
window.logout = logout;
window.showSection = showSection;
window.openCreateModal = openCreateModal;
window.closeModal = closeModal;
window.submitModal = submitModal;
window.createNewAccount = createNewAccount;
window.deleteAccount = deleteAccount;
window.openAccountModal = openAccountModal;
window.closeAccountModal = closeAccountModal;
window.saveAccountChanges = saveAccountChanges;
window.showEaseMateInstructions = showEaseMateInstructions;
window.copyEaseMateScript = copyEaseMateScript;
window.verifyEaseMateID = verifyEaseMateID;
window.selectProvider = selectProvider;
window.backToProviders = backToProviders;
window.sendTestMessage = sendTestMessage;

// Lắng nghe sự kiện lỗi xác thực
window.addEventListener('auth-failed', () => {
    logout();
});

// Khởi tạo ứng dụng
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Nạp tất cả templates
        await Promise.all([
            loadTemplate('loginContainer', 'login'),
            loadTemplate('sidebarContainer', 'sidebar'),
            loadTemplate('keysSectionContainer', 'keys'),
            loadTemplate('accountSectionContainer', 'account'),
            loadTemplate('testSectionContainer', 'test'),
            loadTemplate('modalContainer', 'modal')
        ]);

        const isLoggedIn = checkLoginState();
        initIcons();

        if (isLoggedIn) {
            // Mặc định hiển thị phần API Keys
            showSection('keys');
            
            // Nạp dữ liệu nền
            await Promise.all([
                loadKeys(),
                loadModels(),
                loadAllAccounts()
            ]);
        }
    } catch (err) {
        console.error('Lỗi khởi tạo ứng dụng:', err);
    }
});
