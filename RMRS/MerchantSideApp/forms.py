import json
from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.db.models import Q

from .models import Meal, MerchantAccount, Restaurant


class MerchantImageInput(forms.ClearableFileInput):
    template_name = "merchantsideapp/widgets/image_input.html"
    initial_text = ""
    input_text = ""
    clear_checkbox_label = "移除目前照片"

    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault("attrs", {})
        attrs.setdefault("class", "field-input file-upload-input")
        attrs.setdefault("accept", "image/*")
        super().__init__(*args, **kwargs)


class MerchantRegistrationForm(forms.Form):
    restaurant_name = forms.CharField(
        label="餐廳名稱",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "餐廳名稱",
                "autocomplete": "organization",
                "class": "form-input",
            }
        ),
    )
    merchant_name = forms.CharField(
        label="商家名稱",
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "placeholder": "設定登入時使用的名稱",
                "autocomplete": "username",
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
        "merchant_name_in_use": "此商家名稱已被使用。",
    }

    def clean_restaurant_name(self):
        name = self.cleaned_data["restaurant_name"].strip()
        if not name:
            raise forms.ValidationError("餐廳名稱不可空白。")
        return name

    def clean_merchant_name(self):
        merchant_name = self.cleaned_data["merchant_name"].strip()
        if not merchant_name:
            raise forms.ValidationError("商家名稱不可空白。")
        if MerchantAccount.objects.filter(merchant_name__iexact=merchant_name).exists():
            raise forms.ValidationError(self.error_messages["merchant_name_in_use"])
        return merchant_name

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
                merchant_name=self.cleaned_data["merchant_name"],
                email=self.cleaned_data["email"],
                password_hash=make_password(self.cleaned_data["password1"]),
            )
        return merchant


class MerchantLoginForm(forms.Form):
    identifier = forms.CharField(
        label="商家帳號 (商家名稱 / Email / 手機)",
        widget=forms.TextInput(
            attrs={
                "placeholder": "商家名稱 / Email / 手機",
                "autocomplete": "username",
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
        "invalid_login": "帳號或密碼不正確。",
    }

    identifier_fields = ("merchant_name", "email", "phone", "phone_number")

    @classmethod
    def _has_field(cls, field_name: str) -> bool:
        try:
            MerchantAccount._meta.get_field(field_name)
            return True
        except FieldDoesNotExist:
            return False

    def _identifier_variants(self, identifier: str) -> list[str]:
        base = identifier.strip()
        variants: list[str] = [base]
        digits_only = "".join(ch for ch in base if ch.isdigit())
        if digits_only and digits_only != base:
            variants.append(digits_only)
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
        cleaned = super().clean()
        identifier = (cleaned.get("identifier") or "").strip()
        password = cleaned.get("password")
        if not identifier or not password:
            return cleaned

        merchant = None
        for variant in self._identifier_variants(identifier):
            merchant = (
                MerchantAccount.objects.select_related("restaurant")
                .filter(self._build_identifier_query(variant))
                .first()
            )
            if merchant:
                break

        if not merchant or not check_password(password, merchant.password_hash):
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
            "image_file",
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
            "image_file": MerchantImageInput(),
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
            macro_values: dict[str, Decimal] = {}
            for key in ("protein", "carb", "fat"):
                parsed = self._parse_decimal(raw.get(key))
                if parsed is not None:
                    macro_values[key] = parsed
            notes = str(raw.get("notes", "")).strip() or None
            metadata = {"notes": notes} if notes else None
            cleaned_entries.append(
                {
                    "name": name,
                    "quantity": quantity,
                    "calories": calories_decimal,
                    "protein": macro_values.get("protein"),
                    "carb": macro_values.get("carb"),
                    "fat": macro_values.get("fat"),
                    "notes": notes,
                    "metadata": metadata,
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


class MerchantAccountForm(forms.ModelForm):
    class Meta:
        model = MerchantAccount
        fields = ["merchant_name", "email", "phone"]
        widgets = {
            "merchant_name": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "設定登入時使用的名稱",
                    "autocomplete": "username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "商家 Email",
                    "autocomplete": "email",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "商家聯絡電話",
                    "autocomplete": "tel",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = MerchantAccount.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("此 Email 已被其他帳號使用。")
        return email

    def clean_merchant_name(self):
        name = (self.cleaned_data.get("merchant_name") or "").strip()
        if not name:
            raise forms.ValidationError("商家名稱不可空白。")
        qs = MerchantAccount.objects.filter(merchant_name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("此商家名稱已被其他帳號使用。")
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return phone
        qs = MerchantAccount.objects.filter(phone__iexact=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("此電話已被其他帳號使用。")
        return phone

    def save(self, commit: bool = True):
        merchant = super().save(commit=False)
        merchant.merchant_name = self.cleaned_data["merchant_name"].strip()
        merchant.email = self.cleaned_data["email"].strip().lower()
        phone = self.cleaned_data.get("phone") or None
        merchant.phone = phone
        if commit:
            merchant.save()
        self.save_m2m()
        return merchant


class MerchantPasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label="目前密碼",
        widget=forms.PasswordInput(
            attrs={
                "class": "field-input",
                "autocomplete": "current-password",
            }
        ),
    )
    new_password1 = forms.CharField(
        label="新密碼",
        widget=forms.PasswordInput(
            attrs={
                "class": "field-input",
                "autocomplete": "new-password",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="再次輸入新密碼",
        widget=forms.PasswordInput(
            attrs={
                "class": "field-input",
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, merchant: MerchantAccount, *args, **kwargs):
        self.merchant = merchant
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get("current_password", "")
        if not check_password(current, self.merchant.password_hash):
            raise forms.ValidationError("目前密碼不正確。")
        return current

    def clean_new_password1(self):
        new_password = self.cleaned_data.get("new_password1", "")
        if len(new_password) < 8:
            raise forms.ValidationError("新密碼需至少 8 碼。")
        return new_password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("兩次輸入的新密碼不一致。")
        return cleaned

    def save(self):
        new_password = self.cleaned_data["new_password1"]
        self.merchant.password_hash = make_password(new_password)
        self.merchant.save(update_fields=["password_hash", "updated_at"])
        return self.merchant


class RestaurantProfileForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            "name",
            "address",
            "city",
            "district",
            "phone",
            "cuisine_type",
            "price_range",
            "latitude",
            "longitude",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "餐廳名稱",
                    "autocomplete": "organization",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "地址",
                    "autocomplete": "street-address",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "城市",
                }
            ),
            "district": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "行政區",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "聯絡電話",
                    "autocomplete": "tel",
                }
            ),
            "cuisine_type": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "料理風格 (如：早午餐、日式)",
                }
            ),
            "price_range": forms.Select(attrs={"class": "field-input"}),
            "latitude": forms.NumberInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "緯度 (例如 25.03396)",
                    "step": "0.000001",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "經度 (例如 121.56447)",
                    "step": "0.000001",
                }
            ),
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("餐廳名稱不可空白。")
        return name

    def clean_latitude(self):
        value = self.cleaned_data.get("latitude")
        if value is None:
            return value
        if not (-90 <= value <= 90):
            raise forms.ValidationError("緯度應介於 -90 到 90 之間。")
        return value

    def clean_longitude(self):
        value = self.cleaned_data.get("longitude")
        if value is None:
            return value
        if not (-180 <= value <= 180):
            raise forms.ValidationError("經度應介於 -180 到 180 之間。")
        return value
