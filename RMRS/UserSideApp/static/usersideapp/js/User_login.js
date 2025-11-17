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

const form = document.querySelector('.login-container form');
const btn = document.querySelector('.login-btn');

if (form && btn) {
    form.addEventListener('submit', () => {
        btn.disabled = true;
        btn.innerHTML = "Loading...";
    });
}
