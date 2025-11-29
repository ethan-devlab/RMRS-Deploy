import json
from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction

from .models import Meal, MerchantAccount, Restaurant


class MerchantRegistrationForm(forms.Form):
    restaurant_name = forms.CharField(
        label="餐廳名稱",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "商家名稱",
                "autocomplete": "organization",
                "class": "form-input",
            }
        ),
    )
    email = forms.EmailField(
        label="商家 Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "商家 Email",
                "autocomplete": "email",
                "class": "form-input",
            }
        ),
    )
    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "密碼",
                "autocomplete": "new-password",
                "class": "form-input",
            }
        ),
    )
    password2 = forms.CharField(
        label="再次輸入密碼",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "再次輸入密碼",
                "autocomplete": "new-password",
                "class": "form-input",
            }
        ),
    )

    error_messages = {
        "password_mismatch": "兩次輸入的密碼不一致。",
        "email_in_use": "此 Email 已被註冊。",
    }

    def clean_restaurant_name(self):
        name = self.cleaned_data["restaurant_name"].strip()
        if not name:
            raise forms.ValidationError("餐廳名稱不可空白。")
        return name

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if MerchantAccount.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(self.error_messages["email_in_use"])
        return email

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages["password_mismatch"])
        return cleaned

    def save(self):
        restaurant_name = self.cleaned_data["restaurant_name"]
        with transaction.atomic():
            restaurant = Restaurant.objects.create(name=restaurant_name)
            merchant = MerchantAccount.objects.create(
                restaurant=restaurant,
                email=self.cleaned_data["email"],
                password_hash=make_password(self.cleaned_data["password1"]),
            )
        return merchant


class MerchantLoginForm(forms.Form):
    email = forms.EmailField(
        label="商家 Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "商家 Email",
                "autocomplete": "email",
                "class": "form-input",
            }
        ),
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "密碼",
                "autocomplete": "current-password",
                "class": "form-input",
            }
        ),
    )

    error_messages = {
        "invalid_login": "Email 或密碼不正確。",
    }

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if not email or not password:
            return cleaned

        try:
            merchant = MerchantAccount.objects.select_related("restaurant").get(
                email__iexact=email.strip().lower()
            )
        except MerchantAccount.DoesNotExist:
            raise forms.ValidationError(self.error_messages["invalid_login"])

        if not check_password(password, merchant.password_hash):
            raise forms.ValidationError(self.error_messages["invalid_login"])

        self.merchant = merchant
        return cleaned

    def get_merchant(self):
        return getattr(self, "merchant", None)


class MealCreateForm(forms.ModelForm):
    nutrition_payload = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Meal
        fields = [
            "name",
            "description",
            "category",
            "price",
            "is_vegetarian",
            "is_spicy",
            "image_url",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "例如：招牌紅燒牛肉麵", "class": "field-input"}
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "新增餐點特色或套餐內容，提升消費者點餐意願！",
                    "class": "field-input textarea",
                }
            ),
            "category": forms.TextInput(
                attrs={"placeholder": "主食 / 湯品 / 點心...", "class": "field-input"}
            ),
            "price": forms.NumberInput(
                attrs={"min": 0, "step": "1", "class": "field-input"}
            ),
            "image_url": forms.URLInput(
                attrs={
                    "placeholder": "可選：餐點照片 URL",
                    "class": "field-input",
                }
            ),
        }

    def __init__(self, restaurant: Restaurant, *args, **kwargs):
        self.restaurant = restaurant
        super().__init__(*args, **kwargs)
        self.fields["category"].required = True
        for toggle in ("is_vegetarian", "is_spicy"):
            self.fields[toggle].widget.attrs.setdefault("class", "toggle-input")
        self.nutrition_entries: list[dict] = []

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("餐點名稱不可空白。")
        return name

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None or price <= 0:
            raise forms.ValidationError("請輸入大於 0 的售價。")
        return price

    def _parse_decimal(self, value):
        if value in (None, ""):
            return None
        try:
            number = Decimal(str(value))
        except (InvalidOperation, TypeError) as exc:
            raise forms.ValidationError("請輸入有效的營養數值。") from exc
        if number < 0:
            raise forms.ValidationError("營養數值不可小於 0。")
        return number

    def clean_nutrition_payload(self):
        payload = self.cleaned_data.get("nutrition_payload", "").strip()
        if not payload:
            self.nutrition_entries = []
            return ""
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError("營養成分格式錯誤，請重新嘗試。") from exc

        cleaned_entries = []
        for raw in data:
            name = str(raw.get("name", "")).strip()
            if not name:
                continue
            quantity = str(raw.get("quantity", "")).strip() or None
            calories_value = raw.get("calories")
            calories_decimal = self._parse_decimal(calories_value) or Decimal("0")
            metadata = {}
            for key in ("protein", "carb", "fat"):
                parsed = self._parse_decimal(raw.get(key))
                if parsed is not None:
                    metadata[key] = float(parsed)
            if raw.get("notes"):
                metadata["notes"] = str(raw["notes"]).strip()
            cleaned_entries.append(
                {
                    "name": name,
                    "quantity": quantity,
                    "calories": calories_decimal,
                    "metadata": metadata or None,
                }
            )

        self.nutrition_entries = cleaned_entries
        return payload

    def save(self, commit: bool = True) -> Meal:
        meal = super().save(commit=False)
        meal.restaurant = self.restaurant
        if commit:
            meal.save()
        return meal
