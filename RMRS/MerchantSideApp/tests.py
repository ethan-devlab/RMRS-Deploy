import json
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .auth_utils import SESSION_MERCHANT_KEY
from .models import Meal, MerchantAccount, Restaurant
from UserSideApp.models import MealComponent


class MerchantAuthTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(name="測試餐廳")
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			display_name="麻辣一哥",
			email="owner@example.com",
			password_hash=make_password("SecurePass!23"),
		)

	def test_register_creates_merchant_and_logs_in(self):
		response = self.client.post(
			reverse("merchantsideapp:register"),
			{
				"merchant_name": "新商家",
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
		self.assertEqual(new_merchant.display_name, "新商家")

	def test_register_requires_unique_email(self):
		response = self.client.post(
			reverse("merchantsideapp:register"),
			{
				"merchant_name": "重複商家",
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
		self.assertContains(response, "麻辣一哥")


class MerchantMealCreationTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(name="勇者餐館")
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			display_name="勇者商家",
			email="meal-owner@example.com",
			password_hash=make_password("SecurePass!23"),
		)

	def _login(self):
		session = self.client.session
		session[SESSION_MERCHANT_KEY] = self.merchant.pk
		session.save()

	def test_add_meal_with_nutrition_components(self):
		self._login()
		payload = json.dumps(
			[
				{
					"name": "蛋白質",
					"quantity": "25g",
					"calories": "100",
					"protein": "25",
					"carb": "10",
					"fat": "5",
					"notes": "雞胸肉",
				}
			]
		)
		response = self.client.post(
			reverse("merchantsideapp:add_meal"),
			{
				"name": "勇者能量碗",
				"category": "主食",
				"description": "高蛋白餐盒",
				"price": "250",
				"image_url": "https://example.com/meal.jpg",
				"is_vegetarian": "on",
				"is_spicy": "",
				"nutrition_payload": payload,
			},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse("merchantsideapp:manage_meals"))
		meal = Meal.objects.get(name="勇者能量碗")
		components = list(meal.nutrition_components.all())
		self.assertEqual(len(components), 1)
		component = components[0]
		self.assertEqual(component.name, "蛋白質")
		self.assertEqual(component.quantity, "25g")
		self.assertEqual(float(component.calories), 100.0)
		self.assertEqual(component.metadata["protein"], 25.0)
		self.assertEqual(component.metadata["notes"], "雞胸肉")

	def test_add_meal_requires_authentication(self):
		response = self.client.get(reverse("merchantsideapp:add_meal"))
		self.assertEqual(response.status_code, 302)
		self.assertTrue(response.url.startswith(reverse("merchantsideapp:login")))

	def test_invalid_nutrition_payload_shows_error(self):
		self._login()
		response = self.client.post(
			reverse("merchantsideapp:add_meal"),
			{
				"name": "錯誤餐點",
				"category": "其他",
				"price": "120",
				"nutrition_payload": "not-json",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "營養成分格式錯誤")
		self.assertFalse(Meal.objects.filter(name="錯誤餐點").exists())


class MerchantMealManagementTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(name="巧手廚坊")
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			display_name="巧手廚師",
			email="manage-owner@example.com",
			password_hash=make_password("ManagePass!45"),
		)
		Meal.objects.create(
			restaurant=self.restaurant,
			name="暖心番茄燉飯",
			description="慢火拌炒的番茄燉飯",
			category="主食",
			price=280,
			is_available=True,
		)
		Meal.objects.create(
			restaurant=self.restaurant,
			name="涼拌手作豆腐",
			description="附芝麻醬的清爽小菜",
			category="小菜",
			price=120,
			is_available=False,
		)

	def _login(self):
		session = self.client.session
		session[SESSION_MERCHANT_KEY] = self.merchant.pk
		session.save()

	def test_manage_meals_requires_authentication(self):
		response = self.client.get(reverse("merchantsideapp:manage_meals"))
		self.assertEqual(response.status_code, 302)
		self.assertTrue(response.url.startswith(reverse("merchantsideapp:login")))

	def test_manage_meals_lists_existing_meals(self):
		self._login()
		response = self.client.get(reverse("merchantsideapp:manage_meals"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "暖心番茄燉飯")
		self.assertContains(response, "涼拌手作豆腐")

	def test_manage_meals_filter_by_keyword_and_status(self):
		self._login()
		url = reverse("merchantsideapp:manage_meals") + "?keyword=番茄&status=available"
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "暖心番茄燉飯")
		meals = response.context["meals"]
		self.assertEqual(meals.count(), 1)
		self.assertEqual(meals.first().name, "暖心番茄燉飯")

	def test_edit_meal_updates_fields_and_components(self):
		self._login()
		meal = self.restaurant.meals.get(name="暖心番茄燉飯")
		MealComponent.objects.create(
			meal=meal,
			name="舊熱量",
			calories=50,
		)
		payload = json.dumps(
			[
				{
					"name": "蛋白質",
					"quantity": "30g",
					"calories": "120",
					"protein": "30",
				}
			]
		)
		response = self.client.post(
			reverse("merchantsideapp:edit_meal", args=[meal.id]),
			{
				"name": "升級番茄燉飯",
				"category": "主食",
				"price": "300",
				"description": "加入起司",
				"is_vegetarian": "on",
				"nutrition_payload": payload,
			},
		)
		self.assertEqual(response.status_code, 302)
		meal.refresh_from_db()
		self.assertEqual(meal.name, "升級番茄燉飯")
		self.assertTrue(meal.is_vegetarian)
		components = meal.nutrition_components.all()
		self.assertEqual(components.count(), 1)
		self.assertEqual(components.first().name, "蛋白質")

	def test_delete_meal_marks_unavailable(self):
		self._login()
		meal = self.restaurant.meals.get(name="涼拌手作豆腐")
		response = self.client.post(
			reverse("merchantsideapp:delete_meal", args=[meal.id])
		)
		self.assertEqual(response.status_code, 302)
		meal.refresh_from_db()
		self.assertFalse(meal.is_available)

	def test_manage_page_shows_archived_preview(self):
		self._login()
		meal = self.restaurant.meals.get(name="涼拌手作豆腐")
		meal.is_available = False
		meal.save(update_fields=["is_available", "updated_at"])
		response = self.client.get(reverse("merchantsideapp:manage_meals"))
		self.assertContains(response, "已下架餐點")
		self.assertContains(response, "涼拌手作豆腐")


class MerchantDashboardTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(name="星級餐館", is_active=True)
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			display_name="星級主廚",
			email="dash-owner@example.com",
			password_hash=make_password("DashPass!12"),
		)
		self.meal_new = Meal.objects.create(
			restaurant=self.restaurant,
			name="奶油海鮮燉飯",
			price=320,
			is_available=True,
		)
		self.meal_old = Meal.objects.create(
			restaurant=self.restaurant,
			name="日式炸豬排",
			price=260,
			is_available=False,
		)
		Meal.objects.filter(pk=self.meal_old.pk).update(
			updated_at=timezone.now() - timedelta(days=2)
		)

	def _login(self):
		session = self.client.session
		session[SESSION_MERCHANT_KEY] = self.merchant.pk
		session.save()

	def test_dashboard_shows_recent_meals(self):
		self._login()
		response = self.client.get(reverse("merchantsideapp:dashboard"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "奶油海鮮燉飯")
		self.assertContains(response, "日式炸豬排")
		self.assertContains(response, "營業")
		self.assertContains(response, "星級主廚")

	def test_update_restaurant_status(self):
		self._login()
		response = self.client.post(
			reverse("merchantsideapp:restaurant_status"),
			{"status": "closed"},
		)
		self.assertEqual(response.status_code, 302)
		self.restaurant.refresh_from_db()
		self.assertFalse(self.restaurant.is_active)


class MerchantSettingsTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(
			name="設定餐廳",
			address="舊地址",
			price_range=Restaurant.PriceRange.MEDIUM,
		)
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			display_name="設定達人",
			email="settings-owner@example.com",
			password_hash=make_password("SettingsPass!77"),
		)

	def _login(self):
		session = self.client.session
		session[SESSION_MERCHANT_KEY] = self.merchant.pk
		session.save()

	def test_settings_requires_authentication(self):
		response = self.client.get(reverse("merchantsideapp:settings"))
		self.assertEqual(response.status_code, 302)
		self.assertTrue(response.url.startswith(reverse("merchantsideapp:login")))

	def test_settings_page_renders_forms(self):
		self._login()
		response = self.client.get(reverse("merchantsideapp:settings"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.merchant.display_name)
		self.assertContains(response, self.merchant.email)
		self.assertContains(response, self.restaurant.name)

	def test_account_form_updates_profile(self):
		self._login()
		response = self.client.post(
			reverse("merchantsideapp:settings"),
			{
				"form_type": "account",
				"display_name": "全新設定達人",
				"email": "updated-owner@example.com",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.merchant.refresh_from_db()
		self.assertEqual(self.merchant.email, "updated-owner@example.com")
		self.assertEqual(self.merchant.display_name, "全新設定達人")

	def test_password_form_updates_hash(self):
		self._login()
		response = self.client.post(
			reverse("merchantsideapp:settings"),
			{
				"form_type": "password",
				"current_password": "SettingsPass!77",
				"new_password1": "SuperNewPass!88",
				"new_password2": "SuperNewPass!88",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.merchant.refresh_from_db()
		self.assertTrue(check_password("SuperNewPass!88", self.merchant.password_hash))

	def test_restaurant_form_updates_profile(self):
		self._login()
		response = self.client.post(
			reverse("merchantsideapp:settings"),
			{
				"form_type": "restaurant",
				"name": "新設定餐廳",
				"address": "台北市信義路",
				"city": "台北市",
				"district": "大安區",
				"phone": "02-1234-5678",
				"cuisine_type": "早午餐",
				"price_range": Restaurant.PriceRange.HIGH,
				"latitude": "25.03396",
				"longitude": "121.56447",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.restaurant.refresh_from_db()
		self.assertEqual(self.restaurant.name, "新設定餐廳")
		self.assertEqual(self.restaurant.address, "台北市信義路")
		self.assertEqual(self.restaurant.city, "台北市")
		self.assertEqual(self.restaurant.district, "大安區")
		self.assertEqual(self.restaurant.phone, "02-1234-5678")
		self.assertEqual(self.restaurant.cuisine_type, "早午餐")
		self.assertEqual(self.restaurant.price_range, Restaurant.PriceRange.HIGH)
		self.assertEqual(float(self.restaurant.latitude), 25.03396)
		self.assertEqual(float(self.restaurant.longitude), 121.56447)

	def test_restaurant_form_rejects_invalid_coordinates(self):
		self._login()
		response = self.client.post(
			reverse("merchantsideapp:settings"),
			{
				"form_type": "restaurant",
				"name": "設定餐廳",
				"price_range": Restaurant.PriceRange.MEDIUM,
				"latitude": "95.0",
				"longitude": "200.0",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "緯度應介於 -90 到 90 之間。")
		self.assertContains(response, "經度應介於 -180 到 180 之間。")
		self.restaurant.refresh_from_db()
		self.assertIsNone(self.restaurant.latitude)
		self.assertIsNone(self.restaurant.longitude)
