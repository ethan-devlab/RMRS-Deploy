(function () {
    function attachDeleteConfirmation() {
        const forms = document.querySelectorAll(".delete-form");
        forms.forEach((form) => {
            form.addEventListener("submit", (event) => {
                const name = form.getAttribute("data-meal-name") || "該餐點";
                const confirmed = window.confirm(`確定要下架「${name}」嗎？可在「狀態：已下架」篩選中再度查看。`);
                if (!confirmed) {
                    event.preventDefault();
                }
            });
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        attachDeleteConfirmation();
    });
})();
