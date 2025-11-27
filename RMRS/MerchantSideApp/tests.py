from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse

from .auth_utils import SESSION_MERCHANT_KEY
from .models import MerchantAccount, Restaurant


class MerchantAuthTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(name="測試餐廳")
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			email="owner@example.com",
			password_hash=make_password("SecurePass!23"),
		)

	def test_register_creates_merchant_and_logs_in(self):
		response = self.client.post(
			reverse("merchantsideapp:register"),
			{
				"restaurant_name": "新餐廳",
				"email": "new-owner@example.com",
				"password1": "AnotherPass#45",
				"password2": "AnotherPass#45",
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(
			MerchantAccount.objects.filter(email="new-owner@example.com").exists()
		)
		session = self.client.session
		self.assertIn(SESSION_MERCHANT_KEY, session)
		new_merchant = MerchantAccount.objects.get(email="new-owner@example.com")
		self.assertEqual(new_merchant.restaurant.name, "新餐廳")

	def test_register_requires_unique_email(self):
		response = self.client.post(
			reverse("merchantsideapp:register"),
			{
				"restaurant_name": "重複餐廳",
				"email": "owner@example.com",
				"password1": "RepeatPass!23",
				"password2": "RepeatPass!23",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "此 Email 已被註冊。")
		self.assertEqual(MerchantAccount.objects.filter(email="owner@example.com").count(), 1)

	def test_login_succeeds_with_valid_credentials(self):
		response = self.client.post(
			reverse("merchantsideapp:login"),
			{
				"email": "owner@example.com",
				"password": "SecurePass!23",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse("merchantsideapp:dashboard"))
		self.assertEqual(self.client.session.get(SESSION_MERCHANT_KEY), self.merchant.pk)

	def test_login_rejects_invalid_credentials(self):
		response = self.client.post(
			reverse("merchantsideapp:login"),
			{
				"email": "owner@example.com",
				"password": "WrongPass",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Email 或密碼不正確。")
		self.assertNotIn(SESSION_MERCHANT_KEY, self.client.session)

	def test_dashboard_requires_authentication(self):
		response = self.client.get(reverse("merchantsideapp:dashboard"))
		self.assertEqual(response.status_code, 302)
		self.assertTrue(response.url.startswith(reverse("merchantsideapp:login")))

	def test_dashboard_displays_restaurant_name_for_logged_in_merchant(self):
		session = self.client.session
		session[SESSION_MERCHANT_KEY] = self.merchant.pk
		session.save()
		response = self.client.get(reverse("merchantsideapp:dashboard"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "測試餐廳")
