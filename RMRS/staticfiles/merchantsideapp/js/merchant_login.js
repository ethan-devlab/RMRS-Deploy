const container = document.querySelector(".auth-card");
const inputs = container ? container.querySelectorAll("input") : document.querySelectorAll("input");

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

const form = container ? container.querySelector("form") : null;
const btn = form ? form.querySelector("button[type='submit']") : null;

if (btn && form) {
    form.addEventListener("submit", () => {
        btn.disabled = true;
        btn.textContent = "登入中...";
    });
}
