(function () {
    const builderScript = document.currentScript || document.querySelector("script[data-meal-api]");
    const seed = builderScript?.dataset.componentSeed || "[]";
    const mealApiUrl = builderScript?.dataset.mealApi || "";
    const initialRestaurantId = builderScript?.dataset.initialRestaurant || "";
    const initialMealId = builderScript?.dataset.initialMeal || "";
    const form = document.getElementById("meal-record-form");
    if (!form) {
        return;
    }

    const rowsContainer = document.getElementById("component-rows");
    const addBtn = document.getElementById("add-component");
    const payloadInput = document.getElementById("id_components_payload");
    const seedSource = (payloadInput?.value?.trim() || seed || "[]");
    const restaurantField = document.getElementById("id_restaurant");
    const mealField = document.getElementById("id_source_meal");
    const macroFields = {
        calories: document.getElementById("id_calories"),
        protein: document.getElementById("id_protein_grams"),
        carbs: document.getElementById("id_carb_grams"),
        fat: document.getElementById("id_fat_grams"),
    };
    const mealNameField = document.getElementById("id_meal_name");
    const mealCache = new Map();

    const parseSeed = () => {
        const source = seedSource || "[]";
        try {
            const parsed = JSON.parse(source);
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
        syncPayload();
    } else {
        createRow();
    }

    const normalizeValue = (value) => {
        if (value === null || value === undefined || value === "") {
            return "";
        }
        const numeric = Number(value);
        if (Number.isFinite(numeric)) {
            return numeric.toString();
        }
        return String(value);
    };

    const applyNutrition = (nutrition) => {
        if (!nutrition) {
            return;
        }
        if (macroFields.calories) {
            macroFields.calories.value = normalizeValue(nutrition.calories);
        }
        if (macroFields.protein) {
            macroFields.protein.value = normalizeValue(nutrition.protein);
        }
        if (macroFields.carbs) {
            macroFields.carbs.value = normalizeValue(nutrition.carbohydrate);
        }
        if (macroFields.fat) {
            macroFields.fat.value = normalizeValue(nutrition.fat);
        }
    };

    const applyMealNameIfEmpty = (meal) => {
        if (!mealNameField || !meal) {
            return;
        }
        if (!mealNameField.value.trim()) {
            mealNameField.value = meal.name || mealNameField.value;
        }
    };

    const getSelectedOption = () => {
        if (!mealField) {
            return null;
        }
        if (typeof mealField.selectedIndex === "number" && mealField.selectedIndex >= 0) {
            return mealField.options[mealField.selectedIndex];
        }
        return mealField.selectedOptions?.[0] || null;
    };

    const hydrateFromSelection = () => {
        if (!mealField) {
            return;
        }
        const selectedMealId = mealField.value;
        if (!selectedMealId) {
            return;
        }
        const cachedMeal = mealCache.get(selectedMealId);
        if (cachedMeal && cachedMeal.nutrition) {
            applyNutrition(cachedMeal.nutrition);
            applyMealNameIfEmpty(cachedMeal);
            return;
        }
        const selectedOption = getSelectedOption();
        const payload = selectedOption?.dataset?.nutrition;
        if (!payload) {
            return;
        }
        try {
            const parsed = JSON.parse(payload);
            applyNutrition(parsed);
            if (cachedMeal) {
                applyMealNameIfEmpty(cachedMeal);
            }
        } catch (error) {
            console.warn("Unable to parse nutrition payload", error);
        }
    };

    const buildMealOption = (meal) => {
        const option = document.createElement("option");
        option.value = String(meal.id);
        option.textContent = meal.name;
        if (meal.nutrition) {
            option.dataset.nutrition = JSON.stringify(meal.nutrition);
        }
        return option;
    };

    const populateMeals = (meals, selectedId) => {
        if (!mealField) {
            return;
        }
        mealCache.clear();
        mealField.innerHTML = "";
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = meals.length ? "選擇餐點" : "請先選擇餐廳";
        mealField.appendChild(placeholder);
        meals.forEach((meal) => {
            mealCache.set(String(meal.id), meal);
            mealField.appendChild(buildMealOption(meal));
        });
        if (selectedId) {
            mealField.value = String(selectedId);
            hydrateFromSelection();
        }
    };

    const fetchMealsForRestaurant = async (restaurantId, preselectedMealId) => {
        if (!mealField) {
            return;
        }
        if (!mealApiUrl || !restaurantId) {
            populateMeals([], null);
            return;
        }
        try {
            const url = new URL(mealApiUrl, window.location.origin);
            url.searchParams.set("restaurant_id", restaurantId);
            const response = await fetch(url.toString(), {
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            const data = await response.json();
            populateMeals(data.meals || [], preselectedMealId);
        } catch (error) {
            console.warn("無法載入餐廳餐點", error);
            populateMeals([], null);
        }
    };

    if (restaurantField) {
        restaurantField.addEventListener("change", () => {
            const restaurantId = restaurantField.value;
            fetchMealsForRestaurant(restaurantId, null);
        });
    }

    if (mealField) {
        mealField.addEventListener("change", hydrateFromSelection);
    }

    if (initialRestaurantId) {
        fetchMealsForRestaurant(initialRestaurantId, initialMealId || mealField?.value || null);
    } else if (mealField?.value) {
        hydrateFromSelection();
    }
})();
