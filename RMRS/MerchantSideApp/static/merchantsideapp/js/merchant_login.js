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
const routes = window.merchantRoutes || {};

if (btn) {
    btn.addEventListener("click", () => {
        btn.disabled = true;
        btn.innerHTML = "Loading...";
        setTimeout(() => {
            window.location.href = routes.dashboard || routes.login || "/merchant/";
        }, 1200);
    });
}
