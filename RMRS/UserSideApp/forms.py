from datetime import timedelta
from decimal import Decimal, InvalidOperation
import json

from django import forms
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from django.utils import timezone

from MerchantSideApp.models import Meal, Restaurant

from .models import AppUser, DailyMealRecord, Favorite, NotificationSetting, Review, UserPreference


def _meal_category_choices() -> list[tuple[str, str]]:
    categories = (
        Meal.objects.filter(category__isnull=False)
        .exclude(category__exact="")
        .values_list("category", flat=True)
        .order_by("category")
        .distinct()
    )
    choices = [("", "不限")]
    choices.extend((category, category) for category in categories)
    return choices


class MealCategoryChoiceMixin:

    category_field_name = "category"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields.get(self.category_field_name)
        if field:
            field.choices = _meal_category_choices()


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(
            attrs={"placeholder": "密碼", "autocomplete": "new-password"}
        ),
    )
    password2 = forms.CharField(
        label="確認密碼",
        widget=forms.PasswordInput(
            attrs={"placeholder": "再次輸入密碼", "autocomplete": "new-password"}
        ),
    )

    class Meta:
        model = AppUser
        fields = ["username", "full_name", "email"]
        widgets = {
            "username": forms.TextInput(
                attrs={"placeholder": "使用者名稱", "autocomplete": "username"}
            ),
            "full_name": forms.TextInput(
                attrs={"placeholder": "顯示名稱(可留空)", "autocomplete": "name"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "使用者 Email", "autocomplete": "email"}
            ),
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if AppUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("此使用者名稱已被註冊。")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if AppUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("此 Email 已被註冊。")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("兩次輸入的密碼不一致。")
        return cleaned_data

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.password_hash = make_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    identifier = forms.CharField(
        label="帳號 (Email / 手機 / 使用者名稱)",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email / 手機 / 使用者名稱",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(
            attrs={"placeholder": "密碼", "autocomplete": "current-password"}
        ),
    )

    error_messages = {
        "invalid_login": "帳號或密碼不正確。",
    }

    identifier_fields = ("username", "email", "phone", "phone_number")

    @classmethod
    def _has_field(cls, field_name: str) -> bool:
        try:
            AppUser._meta.get_field(field_name)
            return True
        except FieldDoesNotExist:
            return False

    def _identifier_variants(self, identifier: str) -> list[str]:
        base = identifier.strip()
        variants: list[str] = [base]
        digits_only = "".join(ch for ch in base if ch.isdigit())
        if digits_only and digits_only != base:
            variants.append(digits_only)
        # Preserve order but remove duplicates
        seen = set()
        deduped = []
        for value in variants:
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(value)
        return deduped

    def _build_identifier_query(self, identifier: str) -> Q:
        query = Q()
        for field_name in self.identifier_fields:
            if self._has_field(field_name):
                query |= Q(**{f"{field_name}__iexact": identifier})
        if not query:
            query = Q(email__iexact=identifier)
        return query

    def clean(self):
        cleaned_data = super().clean()
        identifier = (cleaned_data.get("identifier") or "").strip()
        password = cleaned_data.get("password")
        if not identifier or not password:
            return cleaned_data

        user = None
        for variant in self._identifier_variants(identifier):
            user = AppUser.objects.filter(self._build_identifier_query(variant)).first()
            if user:
                break

        if not user or not check_password(password, user.password_hash):
            raise forms.ValidationError(self.error_messages["invalid_login"])

        self.user = user
        return cleaned_data

    def get_user(self):
        return getattr(self, "user", None)


class MealRecordForm(forms.ModelForm):
    """Form used to capture a user's meal intake with validation helpers."""

    restaurant = forms.ModelChoiceField(
        label="餐廳",
        required=False,
        queryset=Restaurant.objects.none(),
        widget=forms.Select(attrs={"class": "select"}),
    )
    source_meal = forms.ModelChoiceField(
        label="餐點",
        required=False,
        queryset=Meal.objects.none(),
        widget=forms.Select(attrs={"class": "select"}),
    )

    ingredients_text = forms.CharField(
        label="食材/內容物",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "每行輸入一個食材或使用說明，例如：雞胸肉 120g",
            }
        ),
    )
    components_payload = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = DailyMealRecord
        fields = [
            "date",
            "meal_type",
            "meal_name",
            "calories",
            "protein_grams",
            "carb_grams",
            "fat_grams",
            "meal_notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "meal_type": forms.Select(attrs={"class": "select"}),
            "meal_name": forms.TextInput(attrs={"placeholder": "餐點名稱"}),
            "calories": forms.NumberInput(
                attrs={"min": 0, "step": 1, "placeholder": "總熱量 (kcal)"}
            ),
            "protein_grams": forms.NumberInput(
                attrs={"min": 0, "step": 0.1, "placeholder": "蛋白質 (g)"}
            ),
            "carb_grams": forms.NumberInput(
                attrs={"min": 0, "step": 0.1, "placeholder": "碳水化合物 (g)"}
            ),
            "fat_grams": forms.NumberInput(
                attrs={"min": 0, "step": 0.1, "placeholder": "脂肪 (g)"}
            ),
            "meal_notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "可選：口味、身體反應等備註",
                }
            ),
        }

    def __init__(self, user: AppUser, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["restaurant"].queryset = (
            Restaurant.objects.filter(is_active=True).order_by("name")
        )
        self.fields["restaurant"].empty_label = "未指定"
        self.fields["source_meal"].queryset = Meal.objects.none()
        self.fields["source_meal"].empty_label = "請先選擇餐廳"
        selected_restaurant_id = self._determine_selected_restaurant()
        if selected_restaurant_id:
            self.fields["source_meal"].queryset = (
                Meal.objects.filter(
                    restaurant_id=selected_restaurant_id,
                    is_available=True,
                )
                .order_by("name")
            )
            self.initial.setdefault("restaurant", selected_restaurant_id)
        if self.instance.pk and self.instance.source_meal_id:
            self.initial.setdefault("source_meal", self.instance.source_meal_id)
        self.fields["meal_name"].required = False
        for field_name in [
            "calories",
            "protein_grams",
            "carb_grams",
            "fat_grams",
        ]:
            self.fields[field_name].required = False
        if not self.initial.get("date"):
            self.initial["date"] = timezone.now().date()
        if self.instance.pk and self.instance.ingredients:
            self.initial.setdefault(
                "ingredients_text", "\n".join(self.instance.ingredients or [])
            )
        for field_name in [
            "calories",
            "protein_grams",
            "carb_grams",
            "fat_grams",
        ]:
            self.fields[field_name].widget.attrs.setdefault("class", "number-input")

    def clean_meal_name(self):
        meal_name = (self.cleaned_data.get("meal_name") or "").strip()
        return meal_name

    def clean_ingredients_text(self):
        text = self.cleaned_data.get("ingredients_text", "")
        parsed = [line.strip() for line in text.splitlines() if line.strip()]
        self.ingredients_data = parsed
        return text

    def clean_components_payload(self):
        payload = self.cleaned_data.get("components_payload")
        if not payload:
            self.components_data = []
            return payload
        try:
            raw_components = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError("餐點組成格式錯誤。") from exc

        cleaned_components = []
        for raw in raw_components:
            name = str(raw.get("name", "")).strip()
            quantity = str(raw.get("quantity", "")).strip() or None
            calories_value = raw.get("calories")
            if not name:
                continue
            if calories_value in (None, ""):
                calories_decimal = Decimal("0")
            else:
                try:
                    calories_decimal = Decimal(str(calories_value))
                except (InvalidOperation, TypeError) as exc:
                    raise forms.ValidationError("請輸入有效的組成熱量數值。") from exc
            if calories_decimal < 0:
                raise forms.ValidationError("組成熱量不可小於 0。")
            cleaned_components.append(
                {
                    "name": name,
                    "quantity": quantity,
                    "calories": calories_decimal,
                }
            )

        self.components_data = cleaned_components
        return payload

    def clean(self):
        cleaned_data = super().clean()
        if not self.user:
            raise forms.ValidationError("需要登入使用者才能建立飲食紀錄。")

        self._apply_selected_meal(cleaned_data)

        meal_name = cleaned_data.get("meal_name")
        date = cleaned_data.get("date")
        if meal_name and date:
            week_start = date - timedelta(days=date.weekday())
            week_end = week_start + timedelta(days=7)
            duplicate_qs = DailyMealRecord.objects.filter(
                user=self.user,
                meal_name__iexact=meal_name.strip(),
                date__gte=week_start,
                date__lt=week_end,
            )
            if self.instance.pk:
                duplicate_qs = duplicate_qs.exclude(pk=self.instance.pk)
            if duplicate_qs.exists():
                raise forms.ValidationError(
                    "同樣的餐點名稱在一週內已經記錄過，請改用其他名稱或更新原紀錄。"
                )

        return cleaned_data

    def save(self, commit: bool = True):
        record = super().save(commit=False)
        record.user = self.user
        record.source_meal = self.cleaned_data.get("source_meal")
        if record.source_meal and not record.meal_name:
            record.meal_name = record.source_meal.name
        record.ingredients = getattr(self, "ingredients_data", []) or None
        if commit:
            record.save()
        return record

    @property
    def components(self):
        return getattr(self, "components_data", [])

    def _determine_selected_restaurant(self) -> int | None:
        candidate = None
        if self.is_bound:
            candidate = (self.data.get("restaurant") or "").strip()
        if not candidate:
            candidate = self.initial.get("restaurant")
        if not candidate and self.instance.pk and self.instance.source_meal_id:
            candidate = self.instance.source_meal.restaurant_id
        try:
            return int(candidate) if candidate else None
        except (TypeError, ValueError):  # pragma: no cover - defensive
            return None

    def _macro_fields(self) -> list[str]:
        return ["calories", "protein_grams", "carb_grams", "fat_grams"]

    def _apply_selected_meal(self, cleaned_data: dict) -> None:
        source_meal: Meal | None = cleaned_data.get("source_meal")
        restaurant: Restaurant | None = cleaned_data.get("restaurant")
        macros = self._macro_fields()
        if source_meal:
            if restaurant and source_meal.restaurant_id != restaurant.id:
                self.add_error("source_meal", "選擇的餐點不屬於該餐廳。")
                return
            cleaned_data["restaurant"] = source_meal.restaurant
            if not cleaned_data.get("meal_name"):
                cleaned_data["meal_name"] = source_meal.name
            nutrition = getattr(source_meal, "nutrition", None)
            if nutrition:
                for field, value in zip(
                    macros,
                    [
                        nutrition.calories,
                        nutrition.protein,
                        nutrition.carbohydrate,
                        nutrition.fat,
                    ],
                ):
                    cleaned_data[field] = value
            else:
                missing = [field for field in macros if not cleaned_data.get(field)]
                if missing:
                    for field in missing:
                        self.add_error(field, "此餐點缺少營養資訊，請手動輸入。")
        else:
            if not cleaned_data.get("meal_name"):
                self.add_error("meal_name", "請輸入餐點名稱，或選擇已登錄的餐點。")
            for field in macros:
                if not cleaned_data.get(field):
                    self.add_error(field, "請輸入此欄位，或選擇有營養資訊的餐點。")


class UserPreferenceForm(MealCategoryChoiceMixin, forms.ModelForm):
    category = forms.ChoiceField(
        label="偏好品項類別",
        required=False,
        choices=[("", "不限")],
        widget=forms.Select(attrs={"class": "select"}),
    )

    class Meta:
        model = UserPreference
        fields = [
            "cuisine_type",
            "category",
            "price_range",
            "is_vegetarian",
            "avoid_spicy",
            "recommendation_cooldown_days",
        ]
        widgets = {
            "cuisine_type": forms.TextInput(
                attrs={
                    "placeholder": "最常搜尋的料理類型，如日式、義式",
                }
            ),
            "price_range": forms.Select(attrs={"class": "select"}),
            "recommendation_cooldown_days": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 30,
                    "placeholder": "1-30 天，留空使用系統預設",
                }
            ),
        }

    def __init__(self, user: AppUser | None = None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["cuisine_type"].required = False
        self.fields["category"].required = False
        self.fields["price_range"].required = False
        self.fields["is_vegetarian"].label = "偏好全素"
        self.fields["avoid_spicy"].label = "避免辛辣"
        cooldown_field = self.fields["recommendation_cooldown_days"]
        cooldown_field.required = False
        cooldown_field.label = "推薦冷卻天數"
        cooldown_field.help_text = "1-30 天，可避免系統太快推薦同一道餐點。"

    def save(self, commit: bool = True):
        preference = super().save(commit=False)
        if not preference.user_id and self.user:
            preference.user = self.user
        if commit:
            preference.save()
        return preference


class AccountProfileForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ["full_name", "email", "phone"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "placeholder": "顯示名稱",
                    "autocomplete": "name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "使用者 Email",
                    "autocomplete": "email",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "手機號碼",
                    "autocomplete": "tel",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = AppUser.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("此 Email 已被其他帳戶使用。")
        return email

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return ""
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 8:
            raise forms.ValidationError("請輸入有效的手機號碼。")
        qs = AppUser.objects.filter(phone__iexact=digits)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("此手機號碼已被其他帳戶使用。")
        return digits

    def save(self, commit: bool = True):
        account = super().save(commit=False)
        if not account.phone:
            account.phone = None
        if commit:
            account.save(update_fields=["full_name", "email", "phone"])
        return account


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label="目前密碼",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    new_password1 = forms.CharField(
        label="新密碼",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    new_password2 = forms.CharField(
        label="再次輸入新密碼",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, user: AppUser, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get("current_password", "")
        if not check_password(current, self.user.password_hash):
            raise forms.ValidationError("目前密碼不正確。")
        return current

    def clean_new_password1(self):
        new_password = self.cleaned_data.get("new_password1", "")
        if len(new_password) < 8:
            raise forms.ValidationError("新密碼至少需 8 碼。")
        return new_password

    def clean(self):
        cleaned = super().clean()
        new_password1 = cleaned.get("new_password1")
        new_password2 = cleaned.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("兩次輸入的新密碼不一致。")
        return cleaned

    def save(self):
        new_password = self.cleaned_data["new_password1"]
        self.user.password_hash = make_password(new_password)
        self.user.save(update_fields=["password_hash"])
        return self.user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["restaurant", "meal", "rating", "comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "分享你的餐點體驗...",
                }
            )
        }

    def __init__(self, user: AppUser, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["restaurant"].queryset = Restaurant.objects.filter(is_active=True)
        self.fields["restaurant"].label = "餐廳"
        self.fields["meal"].queryset = Meal.objects.filter(is_available=True)
        self.fields["meal"].label = "餐點"
        self.fields["rating"].widget = forms.NumberInput(
            attrs={"min": 1, "max": 5, "step": 1}
        )
        self.fields["rating"].label = "評分 (1-5)"

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if rating is None:
            raise forms.ValidationError("請輸入評分。")
        if rating < 1 or rating > 5:
            raise forms.ValidationError("評分需介於 1 到 5 分。")
        return rating

    def clean(self):
        cleaned = super().clean()
        meal = cleaned.get("meal")
        restaurant = cleaned.get("restaurant")
        if meal and restaurant and meal.restaurant_id != restaurant.id:
            raise forms.ValidationError("餐點必須隸屬於所選餐廳。")
        return cleaned

    def save(self, commit: bool = True):
        review = super().save(commit=False)
        review.user = self.user
        if commit:
            review.save()
        return review


class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = ["meal"]
        widgets = {
            "meal": forms.Select(attrs={"class": "select"}),
        }

    def __init__(self, user: AppUser, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["meal"].queryset = Meal.objects.filter(is_available=True)
        self.fields["meal"].label = "餐點"

    def clean_meal(self):
        meal = self.cleaned_data.get("meal")
        if not meal:
            raise forms.ValidationError("請選擇餐點。")
        return meal

    def save(self, commit: bool = True):
        favorite, _created = Favorite.objects.get_or_create(
            user=self.user,
            meal=self.cleaned_data["meal"],
        )
        return favorite



class RestaurantSearchForm(MealCategoryChoiceMixin, forms.Form):
    keyword = forms.CharField(
        label="搜尋關鍵字",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "輸入餐廳、餐點或關鍵字", "class": "search-input"}
        ),
    )
    city = forms.CharField(
        label="城市",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "例：台北", "class": "filter-input"}
        ),
    )
    district = forms.CharField(
        label="行政區",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "例：信義", "class": "filter-input"}
        ),
    )
    cuisine_type = forms.CharField(
        label="餐飲類型",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "例：日式、火鍋", "class": "filter-input"}
        ),
    )
    category = forms.ChoiceField(
        label="品項類別",
        required=False,
        choices=[("", "不限")],
        widget=forms.Select(attrs={"class": "filter-input"}),
    )
    price_range = forms.ChoiceField(
        label="價格範圍",
        required=False,
        choices=[("", "不限")] + list(Restaurant.PriceRange.choices),
        widget=forms.Select(attrs={"class": "filter-input"}),
    )
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())

    def _clean_text(self, field: str) -> str:
        value = self.cleaned_data.get(field) or ""
        return value.strip()

    def clean_keyword(self):
        return self._clean_text("keyword")

    def clean_city(self):
        return self._clean_text("city")

    def clean_district(self):
        return self._clean_text("district")

    def clean_cuisine_type(self):
        return self._clean_text("cuisine_type")

    def clean_category(self):
        return self._clean_text("category")

    def clean_latitude(self):
        value = self.cleaned_data.get("latitude")
        if value is None:
            return value
        if not -90 <= value <= 90:
            raise forms.ValidationError("緯度範圍需在 -90 到 90 之間。")
        return value

    def clean_longitude(self):
        value = self.cleaned_data.get("longitude")
        if value is None:
            return value
        if not -180 <= value <= 180:
            raise forms.ValidationError("經度範圍需在 -180 到 180 之間。")
        return value


class RecommendationFilterForm(MealCategoryChoiceMixin, forms.Form):
    cuisine_type = forms.CharField(
        label="料理類型",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例如：日式、美式"}),
    )
    category = forms.ChoiceField(
        label="品項類別",
        required=False,
        choices=[("", "不限")],
        widget=forms.Select(attrs={"class": "select"}),
    )
    price_range = forms.ChoiceField(
        label="價格範圍",
        required=False,
        choices=[("", "不限")] + list(Restaurant.PriceRange.choices),
    )
    city = forms.CharField(
        label="城市",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例如：台北"}),
    )
    district = forms.CharField(
        label="行政區",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例如：信義"}),
    )
    is_vegetarian = forms.BooleanField(label="僅顯示素食", required=False)
    avoid_spicy = forms.BooleanField(label="避免辛辣", required=False)
    limit = forms.IntegerField(
        label="推薦數量",
        required=False,
        min_value=1,
        max_value=12,
        initial=6,
        widget=forms.NumberInput(attrs={"min": 1, "max": 12}),
    )

    def clean_limit(self):
        limit = self.cleaned_data.get("limit") or 6
        return max(1, min(12, limit))

    def normalized_filters(self):
        data = self.cleaned_data if hasattr(self, "cleaned_data") else self.initial
        return {
            "cuisine_type": (data.get("cuisine_type") or "").strip() or None,
            "category": (data.get("category") or "").strip() or None,
            "price_range": data.get("price_range") or None,
            "city": (data.get("city") or "").strip() or None,
            "district": (data.get("district") or "").strip() or None,
            "is_vegetarian": bool(data.get("is_vegetarian")),
            "avoid_spicy": bool(data.get("avoid_spicy")),
            "limit": data.get("limit") or 6,
        }


class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = ["is_enabled", "scheduled_time", "channel"]
        widgets = {
            "scheduled_time": forms.TimeInput(attrs={"type": "time"}),
            "channel": forms.Select(attrs={"class": "select"}),
        }


NotificationSettingFormSet = forms.modelformset_factory(
    NotificationSetting,
    form=NotificationSettingForm,
    extra=0,
    can_delete=False,
)
