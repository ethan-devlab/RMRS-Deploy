(function () {
    const builderScript = document.currentScript;
    const seed = builderScript?.dataset.componentSeed || "[]";
    const form = document.getElementById("meal-record-form");
    if (!form) {
        return;
    }

    const rowsContainer = document.getElementById("component-rows");
    const addBtn = document.getElementById("add-component");
    const payloadInput = document.getElementById("id_components_payload");

    const parseSeed = () => {
        try {
            const parsed = JSON.parse(seed);
            if (Array.isArray(parsed)) {
                return parsed;
            }
        } catch (err) {
            console.warn("Invalid component seed", err);
        }
        return [];
    };

    const createRow = (data = { name: "", quantity: "", calories: "" }) => {
        const row = document.createElement("div");
        row.className = "component-row";

        const nameInput = document.createElement("input");
        nameInput.type = "text";
        nameInput.className = "component-input";
        nameInput.placeholder = "名稱";
        nameInput.value = data.name || "";

        const qtyInput = document.createElement("input");
        qtyInput.type = "text";
        qtyInput.className = "component-input";
        qtyInput.placeholder = "份量";
        qtyInput.value = data.quantity || "";

        const calInput = document.createElement("input");
        calInput.type = "number";
        calInput.className = "component-input";
        calInput.placeholder = "熱量";
        calInput.min = "0";
        calInput.step = "0.1";
        calInput.value = data.calories || "";

        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "remove-component";
        removeBtn.textContent = "✕";
        removeBtn.addEventListener("click", () => {
            row.remove();
            syncPayload();
        });

        row.append(nameInput, qtyInput, calInput, removeBtn);
        rowsContainer.appendChild(row);
    };

    const syncPayload = () => {
        const rows = Array.from(rowsContainer.querySelectorAll(".component-row"));
        const payload = rows
            .map((row) => {
                const [nameInput, qtyInput, calInput] = row.querySelectorAll(".component-input");
                return {
                    name: nameInput.value.trim(),
                    quantity: qtyInput.value.trim(),
                    calories: calInput.value.trim(),
                };
            })
            .filter((item) => item.name);
        payloadInput.value = JSON.stringify(payload);
    };

    addBtn?.addEventListener("click", () => {
        createRow();
    });

    form.addEventListener("submit", () => {
        syncPayload();
    });

    const seedData = parseSeed();
    if (seedData.length) {
        seedData.forEach((component) => createRow(component));
    } else {
        createRow();
    }
})();
