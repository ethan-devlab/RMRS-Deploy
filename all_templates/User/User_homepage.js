// 側邊欄收合
const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("toggleBtn");

if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });
}

// 首頁
const menuHome = document.getElementById("menu-home");
if (menuHome) {
    menuHome.addEventListener("click", () => {
        location.href = "User_homepage.html";
    });
}

// 搜尋餐廳
const menuSearch = document.getElementById("menu-search");
if (menuSearch) {
    menuSearch.addEventListener("click", () => {
        location.href = "Search_rest.html";
    });
}

// 今日飲食
const menuToday = document.getElementById("menu-today");
if (menuToday) {
    menuToday.addEventListener("click", () => {
        location.href = "Today_meal.html";
    });
}

// 飲食紀錄
const menuRecord = document.getElementById("menu-record");
if (menuRecord) {
    menuRecord.addEventListener("click", () => {
        location.href = "Record_meal.html";
    });
}

// 推播通知
const menuNotify = document.getElementById("menu-notify");
if (menuNotify) {
    menuNotify.addEventListener("click", () => {
        location.href = "Notify.html";
    });
}

// ⭐ 健康建議
const menuHealth = document.getElementById("menu-health");
if (menuHealth) {
    menuHealth.addEventListener("click", () => {
        location.href = "Health.html";   // 檔名要跟上面的 HTML 一樣
    });
}

// 登出 → 回登入頁
const menuLogout = document.getElementById("menu-logout");
if (menuLogout) {
    menuLogout.addEventListener("click", () => {
        location.href = "User_login.html";
    });
}
