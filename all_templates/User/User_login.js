// ====== C：輸入框聚焦時卡片放大效果 ======
const container = document.querySelector(".login-container");
const inputs = document.querySelectorAll("input");

inputs.forEach(input => {
    input.addEventListener("focus", () => {
        container.style.transform = "scale(1.02)";
        container.style.transition = "0.2s ease";
    });

    input.addEventListener("blur", () => {
        container.style.transform = "scale(1)";
    });
});


// ====== A：登入按鈕 Loading 效果 + 跳轉 ======
const btn = document.querySelector('.login-btn');

btn.addEventListener("click", () => {
    // 1. 顯示 Loading 效果
    btn.disabled = true;
    btn.innerHTML = "Loading...";

    // 2. 模擬登入過程（1.2 秒後跳轉）
    setTimeout(() => {
        window.location.href = "user_homepage.html";
    }, 1200);
});
