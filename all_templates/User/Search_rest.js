const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("toggleBtn");

toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
});

document.getElementById("menu-home").addEventListener("click", () => {
    location.href = "User_homepage.html";
});

document.getElementById("menu-search").addEventListener("click", () => {
    location.href = "Search_rest.html";
});
// ⭐ 登出：回到使用者登入頁
const menuLogout = document.getElementById("menu-logout");
if (menuLogout) {
    menuLogout.addEventListener("click", () => {
        location.href = "User_login.html";      // 使用者登入頁
    });
}
// ⭐ 今日飲食
const menuToday = document.getElementById("menu-today");
if (menuToday) {
    menuToday.addEventListener("click", () => {
        location.href = "Today_meal.html";   // 記得檔名要跟你實際存的一樣
    });
}