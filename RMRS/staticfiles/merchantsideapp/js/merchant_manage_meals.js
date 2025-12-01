(function () {
    function attachStatusConfirmation() {
        const forms = document.querySelectorAll(".status-form");
        forms.forEach((form) => {
            form.addEventListener("submit", (event) => {
                const name = form.getAttribute("data-meal-name") || "該餐點";
                const label = form.getAttribute("data-action-label") || "變更";
                const action = form.querySelector('input[name="action"]').value;
                let message = `確定要${label}「${name}」嗎？`;
                if (action === "deactivate") {
                    message += " 可在「狀態：已下架」篩選中再度查看。";
                }
                const confirmed = window.confirm(message);
                if (!confirmed) {
                    event.preventDefault();
                }
            });
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        attachStatusConfirmation();
    });
})();
