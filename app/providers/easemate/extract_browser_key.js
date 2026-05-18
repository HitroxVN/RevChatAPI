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
            console.error("Lỗi khi giải mã cấu hình:", e);
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
    
    const configData = {
        "device_uuid": visitorId,
        "identity_id": identityId
    };
    
    const jsonString = JSON.stringify(configData, null, 4);
    
    console.log("=== EaseMate Config ===");
    console.log("%c" + jsonString, "color: #00ffcc; font-family: monospace; font-size: 12px; background-color: #1e1e1e; padding: 12px; border-radius: 6px; border: 1px solid #333; display: block;");
    
    try {
        copy(jsonString);
    } catch {}
})();
