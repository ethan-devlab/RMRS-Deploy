# Refactor Plan for RandomMealRecommendationSystem

## Overview

This document outlines the refactoring plan for the RMRS project, focusing on:
1. **CSS Separation** - Splitting the monolithic `User_homepage.css` into page-specific CSS files
2. **UserSideApp Views Separation** - Breaking `dashboard.py` into logical view modules
3. **MerchantSideApp Views Separation** - Breaking `dashboard.py` into logical view modules

**CRITICAL**: All existing functionality must remain intact after refactoring. Run all tests after each change.

---

## 1. CSS Separation (UserSideApp)

### Current State
- Location: `RMRS/UserSideApp/static/usersideapp/css/`
- Files: `User_homepage.css` (1400+ lines containing styles for ALL pages), `User_login.css`, `User_register.css`, `Search_rest.css`

### Target State
Create separate CSS files for each template:

| Template | New CSS File |
|----------|--------------|
| `home.html` | `home.css` |
| `today_meal.html` | `today_meal.css` |
| `record_meal.html` | `record_meal.css` |
| `random.html` | `random.css` (recommendation styles) |
| `search.html` | `search.css` (can merge with existing `Search_rest.css`) |
| `notify.html` | `notify.css` |
| `health.html` | `health.css` |
| `settings.html` | `settings.css` |
| `interactions.html` | `interactions.css` |
| `base_sidebar.html` | `base.css` (shared layout: sidebar, flash messages, global styles) |

### CSS Extraction Guide

#### `base.css` (Shared/Global Styles)
Extract from `User_homepage.css`:
- **Global settings** (lines ~1-10): `body`, `.flash-messages`
- **Sidebar styles** (lines ~370-530): `.sidebar`, `.sidebar-header`, `.toggle-btn`, `.logo`, sidebar collapse states, `.sidebar-user`, `.user-avatar`, `.user-info`
- **Main content area** (lines ~770-810): `.main`, `.main-inner`
- **Welcome/Card basics** (lines ~815-870): `.welcome-box`, `.card`, `.card-long`, `.card-row`
- **Section title** (lines ~880-900): `.section-title`
- **Flash messages** (lines ~290-320): `.flash-message`, `.flash-message.success`, `.flash-message.error`, `.flash-message.info`
- **Form errors** (lines ~325-330): `.form-errors`, `.field-error`
- **Common pills/badges** (lines ~645-680): `.pill`, `.badge`, `.alert`
- **Common buttons** (lines ~175-195): `.primary-btn`, `.outline-btn`, `.text-btn`

#### `home.css` (Home Page)
Extract from `User_homepage.css`:
- **Hero section** (lines ~15-60): `.home-hero`, `.hero-stats`, `.hero-stat`
- **Stats card** (lines ~65-170): `.card-long.stats-card`, `.stats-grid`, `.stats-metric`, `.metric-icon`, `.metric-text`, `.stats-head`, `.stats-headline`, `.stats-kicker`, `.stats-tagline`, `.stats-range-pill`
- **Notification mini list** (lines ~260-290): `.notify-mini-list`

#### `today_meal.css` (Today Meal Page)
Extract from `User_homepage.css`:
- **Today header** (lines ~905-970): `.today-header`, `.today-left`, `.today-right`, `.today-date-pill`, `.today-summary`
- **Mini cards** (lines ~975-1000): `.mini-card`, `.mini-title`, `.mini-value`, `.mini-note`
- **Meal grid** (lines ~1005-1060): `.meal-grid`, `.meal-card`, `.meal-header`, `.meal-tag` (breakfast/lunch/dinner/snack), `.meal-kcal`, `.meal-empty`, `.meal-add-btn`

#### `record_meal.css` (Record Meal Page)
Extract from `User_homepage.css`:
- **Record header** (lines ~1070-1100): `.record-header`, `.record-left`, `.record-right`, `.range-meta`
- **Stats card variations** (lines ~1105-1160): `.stats-card`, `.stats-card__header`, `.stats-card__eyebrow`, `.stats-card__title`, `.stats-card__subtitle`, `.stats-card__summary`, `.stats-card__grid`, `.stat-tile`
- **Record list/timeline** (lines ~1165-1250): `.record-list`, `.timeline-list`, `.record-item`, `.timeline-card`, `.record-date-main`, `.record-date-sub`, `.record-macro-chips`, `.macro-chip`, `.record-actions`
- **Component builder** (lines ~200-260): `.component-builder`, `.component-header`, `.component-rows`, `.component-row`, `.component-input`, `.remove-component`
- **Filter bar** (lines ~135-175): `.record-filter-bar`, `.filter-pill`
- **Meal form** (lines ~120-175): `.meal-form`, `.form-grid`, `.form-group`, `.form-actions`, `.editing-banner`, `.readonly-input`, `.readonly-hint`
- **Component list** (lines ~220-235): `.component-list`

#### `random.css` (Recommendation Page)
Extract from `User_homepage.css`:
- **Preference chip** (lines ~535-550): `.preference-chip`
- **Recommendation filter** (lines ~555-660): `.recommendation-filter`, `.filter-layout`, `.filter-section`, `.form-grid`, `.form-group`, `.preference-toggle`, `.checkbox-pill`, `.limit-control`, `.limit-hint`, `.filter-actions`
- **Section head** (lines ~685-695): `.section-head`
- **Recommendation grid/cards** (lines ~700-770): `.recommendation-grid`, `.recommendation-card`, `.card-title-row`, `.recommendation-link`, `.recommendation-meta`, `.recommendation-tags`

#### `notify.css` (Notification Page)
Extract from `User_homepage.css`:
- **Notify header** (lines ~1270-1295): `.notify-header`, `.notify-left`, `.notify-right`, `.notify-status-pill`
- **Switch toggle** (lines ~1300-1360): `.switch`, `.slider`
- **Notify settings** (lines ~1365-1420): `.notify-settings`, `.notify-row`, `.notify-title`, `.notify-sub`, `.notify-actions`, `.notify-time-pill`
- **Notify items** (lines ~1425-1470): `.notify-item`, `.notify-item-main`, `.notify-item-title`, `.notify-item-sub`, `.notify-item-meta`, `.notify-badge`, `.notify-time-text`

#### `health.css` (Health Advice Page)
Extract from `User_homepage.css`:
- **Health header** (lines ~1480-1530): `.health-header`, `.health-left`, `.health-metrics`, `.health-metric`, `.health-right`, `.health-pill`, `.health-status-*`, `.health-range`, `.health-tags`, `.health-tag`
- **Health cards** (lines ~1570-1620): `.health-today-card`, `.health-today-main`, `.health-today-icon`, `.health-today-title`, `.health-today-desc`, `.health-list`, `.health-grid`, `.health-card`, `.health-card-title`, `.health-card-text`, `.health-lifestyle-card`

#### `settings.css` (Settings Page)
- Extract any settings-specific styles (currently uses shared form styles)
- May need to create dedicated styles for settings layout

#### `interactions.css` (Interactions Page)
Extract from `User_homepage.css`:
- **Review list** (lines ~235-260): `.review-list`, `.review-header`, `.review-footer`, `.review-meal`, `.review-rating`
- **Favorite list** (lines ~235-260): `.favorite-list`, `.favorite-form`

### Implementation Steps

1. **Create `base.css`** with all shared styles (global, sidebar, layout, common components)

2. **Create page-specific CSS files** extracting relevant styles from `User_homepage.css`

3. **Update each template** to include appropriate CSS files:
   ```html
   <!-- In each template's head block -->
   {% load static %}
   <link rel="stylesheet" href="{% static 'usersideapp/css/base.css' %}">
   <link rel="stylesheet" href="{% static 'usersideapp/css/<page-specific>.css' %}">
   ```

4. **Update `base_sidebar.html`** to only include `base.css`

5. **Test each page** to ensure styles are correctly applied

6. **Keep `User_homepage.css` as backup** initially, then remove after verification

---

## 2. UserSideApp Views Separation

### Current State
- Location: `RMRS/UserSideApp/views/`
- Files: `auth.py` (login/logout/register), `dashboard.py` (ALL other views ~800 lines), `__init__.py`

### Target State
Split `dashboard.py` into logical modules:

```
RMRS/UserSideApp/views/
├── __init__.py          # Export all views
├── auth.py              # (existing) login_view, logout_view, register_view
├── home.py              # home view
├── search.py            # search_restaurants view
├── recommendation.py    # random_recommendation, random_recommendation_data
├── meals.py             # today_meal, record_meal, restaurant_meals_api
├── notifications.py     # notifications view
├── health.py            # health_advice view
├── settings.py          # settings view
├── interactions.py      # interactions view
└── utils.py             # Shared helper functions
```

### Views Distribution

#### `utils.py` (New - Shared Utilities)
Move from `dashboard.py`:
- `_serialize_components()` function
- `_save_components()` function
- `_render()` helper function
- `_collect_form_errors()` function
- Constants: `DEFAULT_MAP_CENTER`, `MAX_MAP_RESULTS`, `MAX_MEAL_RESULTS`

#### `home.py` (New)
Move from `dashboard.py`:
- `home()` view function

Required imports:
```python
from django.utils import timezone
from ..auth_utils import get_current_user, user_login_required
from ..models import DailyMealRecord, NotificationSetting, NotificationLog
from ..services import summarize_today, recalculate_weekly_summary, ensure_notification_settings
from .utils import _render
```

#### `search.py` (New)
Move from `dashboard.py`:
- `search_restaurants()` view function
- Related folium map building logic

Required imports:
```python
import folium
from folium.plugins import Fullscreen, LocateControl
from django.db.models import Q
from django.utils.html import escape
from MerchantSideApp.models import Meal, Restaurant
from ..auth_utils import get_current_user, user_login_required
from ..forms import RestaurantSearchForm
from .utils import _render, DEFAULT_MAP_CENTER, MAX_MAP_RESULTS, MAX_MEAL_RESULTS
```

#### `recommendation.py` (New)
Move from `dashboard.py`:
- `_build_recommendation_cards()` helper
- `_serialize_card()` helper
- `_build_random_context()` helper
- `random_recommendation()` view
- `random_recommendation_data()` view

Required imports:
```python
import json
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from MerchantSideApp.models import Meal
from RecommendationSystem.services import get_recommendation_cooldown_days, record_user_choice
from ..auth_utils import get_current_user, user_login_required
from ..forms import RecommendationFilterForm
from ..models import UserPreference
from ..services import RecommendationEngine
from .utils import _render, _collect_form_errors
```

#### `meals.py` (New)
Move from `dashboard.py`:
- `today_meal()` view
- `record_meal()` view
- `restaurant_meals_api()` view

Required imports:
```python
import json
from datetime import timedelta
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from MerchantSideApp.models import Meal, Restaurant
from RecommendationSystem.services import record_user_choice
from ..auth_utils import get_current_user, user_login_required
from ..forms import MealRecordForm
from ..models import DailyMealRecord, MealComponent
from ..services import summarize_today, recalculate_weekly_summary, log_meal_record_notification
from .utils import _render, _serialize_components, _save_components
```

#### `notifications.py` (New)
Move from `dashboard.py`:
- `notifications()` view

Required imports:
```python
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from ..auth_utils import get_current_user, user_login_required
from ..forms import NotificationSettingFormSet
from ..models import NotificationSetting, NotificationLog
from ..services import ensure_notification_settings
from .utils import _render
```

#### `health.py` (New)
Move from `dashboard.py`:
- `health_advice()` view

Required imports:
```python
from ..auth_utils import get_current_user, user_login_required
from ..services import build_health_summary
from .utils import _render
```

#### `settings.py` (New - rename to avoid conflict with Django settings)
**Note**: Name this file `user_settings.py` to avoid import conflicts with Django's settings module.

Move from `dashboard.py`:
- `settings()` view (rename to `user_settings()` in new file)

Required imports:
```python
from django.contrib import messages
from django.shortcuts import redirect
from ..auth_utils import get_current_user, user_login_required
from ..forms import UserPreferenceForm, AccountProfileForm, PasswordChangeForm
from ..models import UserPreference, NotificationSetting
from ..services import ensure_notification_settings
from .utils import _render
```

#### `interactions.py` (New)
Move from `dashboard.py`:
- `interactions()` view

Required imports:
```python
from django.contrib import messages
from django.shortcuts import redirect
from ..auth_utils import get_current_user, user_login_required
from ..forms import ReviewForm, FavoriteForm
from ..models import Review, Favorite
from .utils import _render
```

### Update `__init__.py`

```python
from .auth import login_view, logout_view, register_view
from .home import home
from .search import search_restaurants
from .recommendation import random_recommendation, random_recommendation_data
from .meals import today_meal, record_meal, restaurant_meals_api
from .notifications import notifications
from .health import health_advice
from .user_settings import settings  # Note: function still named 'settings' for URL compatibility
from .interactions import interactions

__all__ = [
    "login_view",
    "logout_view",
    "register_view",
    "home",
    "search_restaurants",
    "random_recommendation",
    "random_recommendation_data",
    "today_meal",
    "record_meal",
    "restaurant_meals_api",
    "notifications",
    "health_advice",
    "settings",
    "interactions",
]
```

### Implementation Steps

1. **Create `utils.py`** with shared helper functions and constants
2. **Create each view module** one at a time
3. **Update `__init__.py`** to import from new modules
4. **Run tests** after each module is created: `python RMRS/manage.py test UserSideApp`
5. **Delete `dashboard.py`** only after all tests pass

---

## 3. MerchantSideApp Views Separation

### Current State
- Location: `RMRS/MerchantSideApp/views/`
- Files: `auth.py` (login/logout/register), `dashboard.py` (ALL other views ~400 lines), `__init__.py`

### Target State
Split `dashboard.py` into logical modules:

```
RMRS/MerchantSideApp/views/
├── __init__.py          # Export all views
├── auth.py              # (existing) login_view, logout_view, register_view
├── dashboard.py         # dashboard view only (rename current to _old)
├── meals.py             # add_meal, edit_meal, delete_meal, manage_meals, meal_detail
├── restaurant.py        # restaurant_detail, update_restaurant_status
├── settings.py          # settings view
└── utils.py             # Shared helper functions
```

### Views Distribution

#### `utils.py` (New - Shared Utilities)
Move from current `dashboard.py`:
- `_build_display_nutrition()` function
- `_extract_ingredients()` function
- `_persist_nutrition_components()` function
- `_coerce_decimal()` function
- `_coerce_float()` function
- `_persist_meal_nutrition()` function
- `_build_nutrition_payload()` function

#### `dashboard.py` (Simplified)
Keep only:
- `dashboard()` view

Required imports:
```python
from django.shortcuts import redirect, render
from django.utils import timezone
from ..auth_utils import get_current_merchant, merchant_login_required
```

#### `meals.py` (New)
Move from current `dashboard.py`:
- `add_meal()` view
- `edit_meal()` view
- `delete_meal()` view
- `manage_meals()` view
- `meal_detail()` view

Required imports:
```python
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from ..auth_utils import get_current_merchant, merchant_login_required
from ..forms import MealCreateForm
from ..models import Restaurant, Meal, NutritionInfo
from UserSideApp.models import MealComponent
from .utils import (
    _build_display_nutrition,
    _extract_ingredients,
    _persist_nutrition_components,
    _build_nutrition_payload,
)
```

#### `restaurant.py` (New)
Move from current `dashboard.py`:
- `restaurant_detail()` view
- `update_restaurant_status()` view

Required imports:
```python
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from ..auth_utils import get_current_merchant, merchant_login_required
from ..models import Restaurant
```

#### `merchant_settings.py` (New - avoid conflict)
Move from current `dashboard.py`:
- `settings()` view (keep function name for URL compatibility)

Required imports:
```python
from django.contrib import messages
from django.shortcuts import redirect, render
from ..auth_utils import get_current_merchant, merchant_login_required
from ..forms import MerchantAccountForm, MerchantPasswordChangeForm, RestaurantProfileForm
```

### Update `__init__.py`

```python
from .auth import login_view, logout_view, register_view
from .dashboard import dashboard
from .meals import add_meal, edit_meal, delete_meal, manage_meals, meal_detail
from .restaurant import restaurant_detail, update_restaurant_status
from .merchant_settings import settings

__all__ = [
    "login_view",
    "register_view",
    "logout_view",
    "dashboard",
    "add_meal",
    "edit_meal",
    "delete_meal",
    "manage_meals",
    "meal_detail",
    "restaurant_detail",
    "update_restaurant_status",
    "settings",
]
```

### Implementation Steps

1. **Create `utils.py`** with shared helper functions
2. **Create each view module** one at a time
3. **Update `__init__.py`** to import from new modules
4. **Run tests** after each module is created: `python RMRS/manage.py test MerchantSideApp`
5. **Rename/delete old `dashboard.py`** only after all tests pass

---

## 4. Testing Strategy

### Before Starting
```powershell
# Run full test suite to establish baseline
python RMRS/manage.py test UserSideApp MerchantSideApp RecommendationSystem
```

### After Each Change
```powershell
# Run relevant app tests
python RMRS/manage.py test UserSideApp  # For UserSideApp changes
python RMRS/manage.py test MerchantSideApp  # For MerchantSideApp changes
```

### Manual Verification Checklist
- [ ] User login/logout works
- [ ] User home page loads correctly with stats
- [ ] Restaurant search with map works
- [ ] Random recommendation page functions (filter, refresh)
- [ ] Today meal page displays properly
- [ ] Record meal form works (create, edit, delete)
- [ ] Notifications page loads and settings save
- [ ] Health advice page displays
- [ ] Settings page (preferences, account, password) works
- [ ] Interactions page (reviews, favorites) works
- [ ] Merchant login/logout works
- [ ] Merchant dashboard loads
- [ ] Add/edit/delete meal works
- [ ] Meal management page works
- [ ] Restaurant detail page works
- [ ] Merchant settings page works

---

## 5. File Summary

### New Files to Create

#### UserSideApp CSS (8 files)
- `RMRS/UserSideApp/static/usersideapp/css/base.css`
- `RMRS/UserSideApp/static/usersideapp/css/home.css`
- `RMRS/UserSideApp/static/usersideapp/css/today_meal.css`
- `RMRS/UserSideApp/static/usersideapp/css/record_meal.css`
- `RMRS/UserSideApp/static/usersideapp/css/random.css`
- `RMRS/UserSideApp/static/usersideapp/css/notify.css`
- `RMRS/UserSideApp/static/usersideapp/css/health.css`
- `RMRS/UserSideApp/static/usersideapp/css/interactions.css`

#### UserSideApp Views (9 files)
- `RMRS/UserSideApp/views/utils.py`
- `RMRS/UserSideApp/views/home.py`
- `RMRS/UserSideApp/views/search.py`
- `RMRS/UserSideApp/views/recommendation.py`
- `RMRS/UserSideApp/views/meals.py`
- `RMRS/UserSideApp/views/notifications.py`
- `RMRS/UserSideApp/views/health.py`
- `RMRS/UserSideApp/views/user_settings.py`
- `RMRS/UserSideApp/views/interactions.py`

#### MerchantSideApp Views (4 files)
- `RMRS/MerchantSideApp/views/utils.py`
- `RMRS/MerchantSideApp/views/meals.py`
- `RMRS/MerchantSideApp/views/restaurant.py`
- `RMRS/MerchantSideApp/views/merchant_settings.py`

### Files to Modify
- `RMRS/UserSideApp/views/__init__.py`
- `RMRS/MerchantSideApp/views/__init__.py`
- `RMRS/MerchantSideApp/views/dashboard.py` (simplify)
- All HTML templates in `RMRS/UserSideApp/templates/usersideapp/` (CSS imports)

### Files to Remove (After Verification)
- `RMRS/UserSideApp/views/dashboard.py` (after splitting)
- `RMRS/UserSideApp/static/usersideapp/css/User_homepage.css` (after CSS separation)

---

## 6. Recommended Execution Order

1. **Phase 1: UserSideApp Views** (Lower risk, more impactful)
   - Create `utils.py`
   - Create view modules one by one
   - Update `__init__.py`
   - Test and verify

2. **Phase 2: MerchantSideApp Views**
   - Create `utils.py`
   - Create view modules one by one
   - Update `__init__.py`
   - Test and verify

3. **Phase 3: CSS Separation** (Can be done independently)
   - Create `base.css`
   - Create page-specific CSS files
   - Update templates
   - Test styling on all pages

---

## Notes for AI Implementation

1. **Import paths**: When moving functions, ensure relative imports use `..` for parent package and `.` for sibling modules
2. **Circular imports**: Be careful of circular dependencies between views and utils
3. **Function names**: Keep view function names exactly the same to maintain URL compatibility
4. **Decorators**: Ensure `@user_login_required` and `@merchant_login_required` decorators are preserved
5. **Tests**: Run tests frequently to catch issues early
6. **Git commits**: Make small, atomic commits for each module/file created
