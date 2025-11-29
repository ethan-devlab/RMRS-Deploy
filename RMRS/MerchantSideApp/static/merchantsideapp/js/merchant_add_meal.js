(function () {
    const payloadInput = document.getElementById("id_nutrition_payload");
    if (!payloadInput) {
        return;
    }

    const listEl = document.getElementById("nutrition-list");
    const errorEl = document.getElementById("nutrition-error");
    const addBtn = document.getElementById("nutrition-add-btn");
    const countEl = document.getElementById("nutrition-count");
    const cancelBtn = document.getElementById("nutrition-cancel-btn");
    const fieldIds = {
        name: "nutrition-name",
        quantity: "nutrition-quantity",
        calories: "nutrition-calories",
        protein: "nutrition-protein",
        carb: "nutrition-carb",
        fat: "nutrition-fat",
        notes: "nutrition-notes",
    };

    function getField(id) {
        return document.getElementById(fieldIds[id]);
    }

    function parseNumber(value) {
        if (value === "" || value === null || value === undefined) {
            return null;
        }
        const parsed = Number(value);
        if (Number.isNaN(parsed) || parsed < 0) {
            return "invalid";
        }
        return Math.round(parsed * 100) / 100;
    }

    let entries = [];
    let editingIndex = null;
    const addBtnDefault = addBtn ? addBtn.textContent.trim() : "加入營養成分";

    function updateEditControls() {
        if (addBtn) {
            addBtn.textContent = editingIndex !== null ? "更新營養成分" : addBtnDefault;
        }
        if (cancelBtn) {
            cancelBtn.hidden = editingIndex === null;
        }
    }

    function syncPayload() {
        payloadInput.value = entries.length ? JSON.stringify(entries) : "";
    }

    function setError(message) {
        if (!errorEl) {
            return;
        }
        errorEl.textContent = message || "";
    }

    function renderList() {
        if (!listEl) {
            return;
        }
        if (countEl) {
            countEl.textContent = entries.length;
        }
        listEl.innerHTML = "";
        if (!entries.length) {
            const empty = document.createElement("div");
            empty.className = "nutrition-empty";
            empty.textContent = "尚未新增任何營養成分";
            listEl.appendChild(empty);
            syncPayload();
            return;
        }
        entries.forEach((entry, index) => {
            const item = document.createElement("div");
            item.className = "nutrition-item";
            if (editingIndex === index) {
                item.classList.add("is-editing");
            }
            const metaParts = [];
            if (entry.quantity) {
                metaParts.push(entry.quantity);
            }
            metaParts.push(`熱量 ${entry.calories} kcal`);
            ["protein", "carb", "fat"].forEach((key) => {
                const source = entry[key] ?? entry?.metadata?.[key];
                if (source !== undefined && source !== null) {
                    const labelMap = { protein: "蛋白質", carb: "碳水", fat: "脂肪" };
                    metaParts.push(`${labelMap[key]} ${source} g`);
                }
            });
            const notes = entry.notes ?? entry?.metadata?.notes;
            if (notes) {
                metaParts.push(notes);
            }
            item.innerHTML = `
                <div>
                    <strong>${entry.name}</strong>
                    <div class="meta">${metaParts.join(" · ")}</div>
                </div>
            `;
            const actionsWrap = document.createElement("div");
            actionsWrap.className = "nutrition-item-actions";
            const editBtn = document.createElement("button");
            editBtn.type = "button";
            editBtn.className = "nutrition-action nutrition-edit";
            editBtn.textContent = "編輯";
            editBtn.addEventListener("click", () => {
                populateFields(entry);
                editingIndex = index;
                updateEditControls();
                renderList();
            });
            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.className = "nutrition-action nutrition-remove";
            removeBtn.textContent = "刪除";
            removeBtn.addEventListener("click", () => {
                entries.splice(index, 1);
                if (editingIndex !== null) {
                    if (editingIndex === index) {
                        exitEditMode();
                    } else if (index < editingIndex) {
                        editingIndex -= 1;
                    }
                }
                renderList();
            });
            actionsWrap.appendChild(editBtn);
            actionsWrap.appendChild(removeBtn);
            item.appendChild(actionsWrap);
            listEl.appendChild(item);
        });
        syncPayload();
    }

    function resetFields() {
        Object.values(fieldIds).forEach((id) => {
            const field = document.getElementById(id);
            if (field) {
                field.value = "";
            }
        });
    }

    function populateFields(entry) {
        const nameField = getField("name");
        if (nameField) {
            nameField.value = entry.name ?? "";
        }
        const quantityField = getField("quantity");
        if (quantityField) {
            quantityField.value = entry.quantity ?? "";
        }
        const caloriesField = getField("calories");
        if (caloriesField) {
            caloriesField.value = entry.calories ?? entry?.metadata?.calories ?? "";
        }
        const macroKeys = ["protein", "carb", "fat"];
        macroKeys.forEach((key) => {
            const field = getField(key);
            if (field) {
                const source = entry[key];
                const fallback = entry?.metadata?.[key];
                field.value = source ?? fallback ?? "";
            }
        });
        const notesField = getField("notes");
        if (notesField) {
            notesField.value = entry.notes ?? entry?.metadata?.notes ?? "";
        }
        nameField?.focus();
        if (nameField) {
            const length = nameField.value.length;
            nameField.setSelectionRange(length, length);
        }
    }

    function exitEditMode() {
        editingIndex = null;
        updateEditControls();
        resetFields();
    }

    function addEntry() {
        if (!addBtn) {
            return;
        }
        const nameField = getField("name");
        const quantityField = getField("quantity");
        const caloriesField = getField("calories");
        const proteinField = getField("protein");
        const carbField = getField("carb");
        const fatField = getField("fat");
        const notesField = getField("notes");

        if (!nameField || !caloriesField) {
            return;
        }
        const name = nameField.value.trim();
        if (!name) {
            setError("請輸入營養名稱。");
            return;
        }
        const calories = parseNumber(caloriesField.value.trim() || "0");
        if (calories === "invalid") {
            setError("請輸入有效的熱量數值。");
            return;
        }

        const protein = parseNumber(proteinField.value.trim());
        if (protein === "invalid") {
            setError("蛋白質數值需為正數。");
            return;
        }
        const proteinValue = protein ?? null;
        const carb = parseNumber(carbField.value.trim());
        if (carb === "invalid") {
            setError("碳水數值需為正數。");
            return;
        }
        const carbValue = carb ?? null;
        const fat = parseNumber(fatField.value.trim());
        if (fat === "invalid") {
            setError("脂肪數值需為正數。");
            return;
        }
        const fatValue = fat ?? null;
        const notes = notesField.value.trim();

        const entryPayload = {
            name,
            quantity: quantityField.value.trim() || null,
            calories: calories ?? 0,
            protein: proteinValue,
            carb: carbValue,
            fat: fatValue,
            notes: notes || null,
        };
        if (editingIndex !== null) {
            entries[editingIndex] = entryPayload;
            setError("");
            exitEditMode();
        } else {
            entries.push(entryPayload);
            setError("");
            resetFields();
        }
        renderList();
    }

    function hydrateFromInput() {
        if (!payloadInput.value) {
            renderList();
            return;
        }
        try {
            const existing = JSON.parse(payloadInput.value);
            if (Array.isArray(existing)) {
                entries = existing;
            }
        } catch (err) {
            console.warn("Failed to parse nutrition payload", err);
        }
        renderList();
    }

    addBtn?.addEventListener("click", addEntry);
    cancelBtn?.addEventListener("click", () => {
        exitEditMode();
        setError("");
    });
    hydrateFromInput();
    updateEditControls();
})();
