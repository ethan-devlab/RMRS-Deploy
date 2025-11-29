(function () {
    const routes = window.merchantRoutes || {};

    function go(key) {
        if (routes[key]) {
            window.location.href = routes[key];
        }
    }

    function setupSidebar() {
        const sidebar = document.getElementById("sidebar");
        const toggleBtn = document.getElementById("toggleBtn");
        if (sidebar && toggleBtn) {
            toggleBtn.addEventListener("click", () => {
                sidebar.classList.toggle("collapsed");
            });
        }

        const menuItems = document.querySelectorAll(".sidebar ul li");
        menuItems.forEach((item) => {
            item.addEventListener("click", () => {
                if (item.id === "menu-logout") return;
                menuItems.forEach((li) => li.classList.remove("active"));
                item.classList.add("active");
            });
        });

        const mapping = {
            "menu-dashboard": "dashboard",
            "menu-add": "addMeal",
            "menu-manage": "manageMeals",
            "menu-settings": "settings",
            "menu-logout": "logout",
        };

        Object.entries(mapping).forEach(([elementId, routeKey]) => {
            const el = document.getElementById(elementId);
            if (!el) {
                return;
            }
            el.addEventListener("click", () => go(routeKey));
        });
    }

    function setupQuickActions() {
        const goAdd = document.getElementById("btn-go-add");
        const goManage = document.getElementById("btn-go-manage");
        if (goAdd) {
            goAdd.addEventListener("click", () => go("addMeal"));
        }
        if (goManage) {
            goManage.addEventListener("click", () => go("manageMeals"));
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        setupSidebar();
        setupQuickActions();
    });
})();
