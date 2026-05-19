(() => {
    console.clear();
    let visitorId = "";
    let identityId = "";
    const appMainStr = localStorage.getItem("app-main");
    if (appMainStr) {
        try {
            const appMain = JSON.parse(appMainStr);
            visitorId = appMain.visitorId || appMain.visitor_id || "";
            identityId = appMain.identityId || appMain.identity_id || "";
        } catch (e) {
            console.error("Lỗi khi giải mã cấu hình localStorage:", e);
        }
    }
    
    if (!visitorId) {
        const updateTrigger = localStorage.getItem("visitor-id-update-trigger");
        if (updateTrigger) {
            try {
                const triggerObj = JSON.parse(updateTrigger);
                visitorId = triggerObj.visitorId || "";
            } catch (e) {}
        }
    }
    
    if (!visitorId || !identityId) {
        console.log("%cKhông tìm thấy thông tin định danh tài khoản.", "color: #ff3333; font-weight: bold;");
        console.log("Hãy thử gửi 1 tin nhắn và chạy lại script này.");
        return;
    }
    
    // Trích xuất JWT Token từ Cookie đăng nhập
    let token = "";
    try {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith("_e_easeus_account_center_account_info=")) {
                const rawVal = cookie.substring("_e_easeus_account_center_account_info=".length);
                const decodedVal = decodeURIComponent(rawVal);
                const cookieObj = JSON.parse(decodedVal);
                token = cookieObj.token || "";
                break;
            }
        }
    } catch (e) {
        console.error("Lỗi khi trích xuất JWT Cookie:", e);
    }
    
    if (!token) {
        console.log("%c⚠️ Cảnh báo: Không tìm thấy JWT Token đăng nhập (Bạn chưa đăng nhập hoặc đang chạy bằng Guest).", "color: #ff9900; font-weight: bold;");
    } else {
        console.log("%c✅ Đã tìm thấy JWT Token đăng nhập tài khoản!", "color: #00ff00; font-weight: bold;");
    }
    
    const configData = {
        "device_uuid": visitorId,
        "identity_id": identityId,
        "token": token
    };
    
    const jsonString = JSON.stringify(configData, null, 4);
    
    console.log("=== EaseMate Config ===");
    console.log("%c" + jsonString, "color: #00ffcc; font-family: monospace; font-size: 12px; background-color: #1e1e1e; padding: 12px; border-radius: 6px; border: 1px solid #333; display: block;");
    
    try {
        copy(jsonString);
        console.log("%c👉 Đã tự động copy cấu hình JSON vào Clipboard! Hãy dán đè vào mục Quản lý tài khoản.", "color: #00ffcc; font-weight: bold;");
    } catch {}
})();
