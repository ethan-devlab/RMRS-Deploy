(function () {
    const form = document.querySelector(".recommendation-filter");
    if (!form) {
        return;
    }
    const endpoint = form.dataset.endpoint;
    if (!endpoint) {
        return;
    }

    let lastAction = "filters";
    const submitButtons = form.querySelectorAll('button[type="submit"]');
    submitButtons.forEach((button) => {
        button.addEventListener("click", () => {
            lastAction = button.value || "filters";
        });
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const submitter = event.submitter;
        const actionValue = (submitter && submitter.value) || lastAction || "filters";
        fetchRecommendations(actionValue);
    });

    function fetchRecommendations(action) {
        const formData = new FormData(form);
        formData.set("action", action || "filters");
        toggleLoading(true);
        fetch(endpoint, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": formData.get("csrfmiddlewaretoken") || "",
            },
            body: formData,
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                updatePrimary(data.primary || {});
                updateSecondary(data.secondary || []);
                updateAlert(data.alert);
                updateErrors(data.formErrors || {});
                updateCooldownHint(data.cooldownDays);
            })
            .catch((error) => {
                console.error("Recommendation refresh failed:", error);
                updateErrors({ __all__: ["無法取得最新推薦，請稍後再試。"] });
            })
            .finally(() => toggleLoading(false));
    }

    function toggleLoading(isLoading) {
        form.classList.toggle("is-loading", Boolean(isLoading));
    }

    function updateAlert(message) {
        const alertEl = document.getElementById("recommendation-alert");
        if (!alertEl) {
            return;
        }
        if (message) {
            alertEl.textContent = message;
            alertEl.hidden = false;
        } else {
            alertEl.textContent = "";
            alertEl.hidden = true;
        }
    }

    function updatePrimary(primary) {
        const reasonEl = document.getElementById("primary-reason");
        if (reasonEl && primary.reason) {
            reasonEl.textContent = primary.reason;
        }
        const grid = document.getElementById("primary-recommendation-grid");
        if (!grid) {
            return;
        }
        grid.innerHTML = "";
        const cards = Array.isArray(primary.cards) ? primary.cards : [];
        if (!cards.length) {
            const empty = document.createElement("p");
            empty.className = "muted recommendation-empty";
            empty.textContent = grid.dataset.emptyText || "暫時沒有符合條件的餐點。";
            grid.appendChild(empty);
            return;
        }
        cards.forEach((card) => {
            grid.appendChild(createCardElement(card));
        });
    }

    function updateSecondary(sections) {
        const wrapper = document.getElementById("secondary-sections");
        if (!wrapper) {
            return;
        }
        wrapper.innerHTML = "";
        sections.forEach((section) => {
            wrapper.appendChild(createSectionElement(section));
        });
    }

    function updateErrors(errors) {
        const errorBox = document.getElementById("filter-errors");
        if (!errorBox) {
            return;
        }
        const entries = [];
        Object.keys(errors || {}).forEach((key) => {
            const messages = errors[key];
            if (!Array.isArray(messages)) {
                return;
            }
            messages.forEach((message) => {
                if (message) {
                    entries.push(message);
                }
            });
        });
        if (!entries.length) {
            errorBox.innerHTML = "";
            errorBox.hidden = true;
            return;
        }
        errorBox.innerHTML = "";
        entries.forEach((message) => {
            const p = document.createElement("p");
            p.textContent = message;
            errorBox.appendChild(p);
        });
        errorBox.hidden = false;
    }

    function updateCooldownHint(days) {
        const hintEl = document.getElementById("recommendation-cooldown-hint");
        if (!hintEl || days === undefined || days === null) {
            return;
        }
        const numericDays = Number(days);
        if (!Number.isFinite(numericDays) || numericDays <= 0) {
            return;
        }
        const template = hintEl.dataset.template || "系統會避免推薦過去 {days} 天內你選過的餐點。";
        hintEl.textContent = template.replace("{days}", numericDays);
    }

    function createSectionElement(section) {
        const cardCount = Array.isArray(section.cards) ? section.cards.length : 0;
        const sectionEl = document.createElement("div");
        sectionEl.className = "card-long";
        const head = document.createElement("div");
        head.className = "section-head";
        const title = document.createElement("h3");
        title.textContent = section.title || "推薦";
        const subtitle = document.createElement("p");
        subtitle.className = "label muted";
        subtitle.textContent = section.subtitle || "";
        head.appendChild(title);
        head.appendChild(subtitle);
        sectionEl.appendChild(head);
        if (!cardCount) {
            const empty = document.createElement("p");
            empty.textContent = "目前沒有資料可以顯示。";
            sectionEl.appendChild(empty);
            return sectionEl;
        }
        const grid = document.createElement("div");
        grid.className = "recommendation-grid compact";
        section.cards.forEach((card) => {
            grid.appendChild(createCardElement(card));
        });
        sectionEl.appendChild(grid);
        return sectionEl;
    }

    function createCardElement(card) {
        const wrapper = document.createElement("div");
        wrapper.className = "recommendation-card";

        const titleRow = document.createElement("div");
        titleRow.className = "card-title-row";

        const left = document.createElement("div");
        const title = document.createElement("h4");
        const mealLink = document.createElement("a");
        mealLink.className = "recommendation-link";
        mealLink.textContent = (card.meal && card.meal.name) || "餐點";
        if (card.meal && card.meal.url) {
            mealLink.href = card.meal.url;
        }
        title.appendChild(mealLink);

        const restaurantName = document.createElement("p");
        restaurantName.className = "muted";
        const restaurantLink = document.createElement("a");
        restaurantLink.className = "recommendation-link recommendation-link--muted";
        restaurantLink.textContent = (card.restaurant && card.restaurant.name) || "";
        if (card.restaurant && card.restaurant.url) {
            restaurantLink.href = card.restaurant.url;
        }
        restaurantName.appendChild(restaurantLink);
        left.appendChild(title);
        left.appendChild(restaurantName);
        titleRow.appendChild(left);

        if (card.favoriteCount) {
            const badge = document.createElement("span");
            badge.className = "badge hot";
            badge.textContent = `❤️ ${card.favoriteCount}`;
            titleRow.appendChild(badge);
        }
        wrapper.appendChild(titleRow);

        const metaPieces = [];
        if (card.restaurant) {
            if (card.restaurant.cuisineType) {
                metaPieces.push(card.restaurant.cuisineType);
            }
            const priceLabel = card.restaurant.priceLabel || card.restaurant.priceRange;
            if (priceLabel) {
                metaPieces.push(`價格 ${priceLabel}`);
            }
            const locationParts = [card.restaurant.city || "", card.restaurant.district || ""]
                .join(" ")
                .trim();
            if (locationParts) {
                metaPieces.push(locationParts);
            }
        }
        if (metaPieces.length) {
            const meta = document.createElement("p");
            meta.className = "recommendation-meta";
            meta.textContent = metaPieces.join(" · ");
            wrapper.appendChild(meta);
        }

        if (card.meal && card.meal.description) {
            const desc = document.createElement("p");
            desc.className = "muted";
            desc.textContent = card.meal.description;
            wrapper.appendChild(desc);
        }

        const tags = document.createElement("div");
        tags.className = "recommendation-tags";
        let hasTag = false;
        if (card.meal && card.meal.isVegetarian) {
            tags.appendChild(createTag("素", "pill veggie"));
            hasTag = true;
        }
        if (card.meal && card.meal.isSpicy === false) {
            tags.appendChild(createTag("不辣", "pill mild"));
            hasTag = true;
        } else if (card.meal && card.meal.isSpicy === true) {
            tags.appendChild(createTag("微辣", "pill spicy"));
            hasTag = true;
        }
        if (card.reason) {
            tags.appendChild(createTag(card.reason, "pill muted"));
            hasTag = true;
        }
        if (hasTag) {
            wrapper.appendChild(tags);
        }

        return wrapper;
    }

    function createTag(text, className) {
        const tag = document.createElement("span");
        tag.className = className;
        tag.textContent = text;
        return tag;
    }
})();
