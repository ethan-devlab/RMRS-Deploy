const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("toggleBtn");

if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });
}

const routes = window.appRoutes || {};
const navMapping = [
    { id: "menu-home", key: "home" },
    { id: "menu-search", key: "search" },
    { id: "menu-random", key: "random" },
    { id: "menu-today", key: "today" },
    { id: "menu-record", key: "record" },
    { id: "menu-notify", key: "notify" },
    { id: "menu-health", key: "health" },
    { id: "menu-interactions", key: "interactions" },
    { id: "menu-setting", key: "settings" },
];

const redirectTo = (key) => {
    const path = routes[key];
    if (path) {
        window.location.href = path;
    }
};

navMapping.forEach(({ id, key }) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("click", () => redirectTo(key));
});

const logoutItem = document.getElementById("menu-logout");
const logoutForm = document.getElementById("logout-form");

if (logoutItem && logoutForm) {
    logoutItem.addEventListener("click", () => {
        logoutForm.submit();
    });
}
