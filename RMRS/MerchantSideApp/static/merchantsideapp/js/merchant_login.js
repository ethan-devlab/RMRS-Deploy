const container = document.querySelector(".login-container");
const inputs = document.querySelectorAll("input");

inputs.forEach((input) => {
    input.addEventListener("focus", () => {
        if (container) {
            container.style.transform = "scale(1.02)";
        }
    });
    input.addEventListener("blur", () => {
        if (container) {
            container.style.transform = "scale(1)";
        }
    });
});

const btn = document.querySelector(".login-btn");
const form = document.querySelector(".login-container form");

if (btn && form) {
    form.addEventListener("submit", () => {
        btn.disabled = true;
        btn.textContent = "登入中...";
    });
}
