const container = document.querySelector(".login-container");
const inputs = document.querySelectorAll("input");

inputs.forEach(input => {
    input.addEventListener("focus", () => {
        if (container) {
            container.style.transform = "scale(1.02)";
            container.style.transition = "0.2s ease";
        }
    });

    input.addEventListener("blur", () => {
        if (container) {
            container.style.transform = "scale(1)";
        }
    });
});

const btn = document.querySelector('.login-btn');
const authRoutes = window.authRoutes || {};

if (btn) {
    btn.addEventListener("click", () => {
        btn.disabled = true;
        btn.innerHTML = "Loading...";
        setTimeout(() => {
            window.location.href = authRoutes.home || "/";
        }, 1200);
    });
}
