import { checkLoginState, login, logout } from './modules/auth.js';
import { initIcons, showSection, loadTemplate } from './modules/ui.js';
import { loadKeys, openCreateModal, closeModal, submitModal } from './modules/keys.js';
import { loadChatXAccount, updateChatXAccount, loadEaseMateAccount, updateEaseMateAccount, openAccountModal, closeAccountModal, saveAccountChanges, showEaseMateInstructions, copyEaseMateScript, verifyEaseMateID } from './modules/account.js';
import { loadModels, sendTestMessage } from './modules/test.js';

// Gắn các hàm vào đối tượng window để HTML có thể gọi
window.login = login;
window.logout = logout;
window.showSection = showSection;
window.openCreateModal = openCreateModal;
window.closeModal = closeModal;
window.submitModal = submitModal;
window.updateChatXAccount = updateChatXAccount;
window.updateEaseMateAccount = updateEaseMateAccount;
window.openAccountModal = openAccountModal;
window.closeAccountModal = closeAccountModal;
window.saveAccountChanges = saveAccountChanges;
window.showEaseMateInstructions = showEaseMateInstructions;
window.copyEaseMateScript = copyEaseMateScript;
window.verifyEaseMateID = verifyEaseMateID;
window.sendTestMessage = sendTestMessage;

// Lắng nghe sự kiện lỗi xác thực
window.addEventListener('auth-failed', () => {
    logout();
});

// Khởi tạo ứng dụng
document.addEventListener('DOMContentLoaded', async () => {
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
        await Promise.all([
            loadKeys(),
            loadModels(),
            loadChatXAccount(),
            loadEaseMateAccount()
        ]);
    }
});
