from django import forms
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction

from .models import MerchantAccount, Restaurant


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
