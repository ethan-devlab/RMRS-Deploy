// merchant_homepage.js

// ------------------------------
// 側欄收合 / 展開
// ------------------------------
const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("toggleBtn");

if (sidebar && toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });
}

// ------------------------------
// 左側選單導頁 + active 樣式
// ------------------------------

// 小工具：導頁
function go(page) {
    window.location.href = page;
}

// 抓所有側欄項目（之後好一起處理 active）
const menuItems = document.querySelectorAll(".sidebar ul li");

// 幫每一個 menu 綁 click 的 active 處理
menuItems.forEach((item) => {
    item.addEventListener("click", () => {
        // 登出另外處理，不在這邊切 active
        if (item.id === "menu-logout") return;

        menuItems.forEach(li => li.classList.remove("active"));
        item.classList.add("active");
    });
});

// 個別功能導頁（依照你的檔名）：
const menuDashboard = document.getElementById("menu-dashboard");
const menuAdd       = document.getElementById("menu-add");
const menuManage    = document.getElementById("menu-manage");
const menuLogout    = document.getElementById("menu-logout");

// 主頁總覽
if (menuDashboard) {
    menuDashboard.addEventListener("click", () => {
        go("merchant_homepage.html");
    });
}

// 新增餐點
if (menuAdd) {
    menuAdd.addEventListener("click", () => {
        go("merchant_add_meal.html");
    });
}

// 管理餐點（之後你做 merchant_manage_meal.html 就會用到）
if (menuManage) {
    menuManage.addEventListener("click", () => {
        go("merchant_manage_meal.html");
        // 如果檔案還沒做，可以先暫時：
        // alert("管理餐點頁面尚未完成");
    });
}

// 登出 → 回商家登入頁
if (menuLogout) {
    menuLogout.addEventListener("click", () => {
        go("merchant_login.html");
    });
}
