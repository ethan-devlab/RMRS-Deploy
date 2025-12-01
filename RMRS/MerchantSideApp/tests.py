import base64
import io
import json
import shutil
import tempfile
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.hashers import check_password, make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .auth_utils import SESSION_MERCHANT_KEY
from .models import Meal, MerchantAccount, Restaurant, NutritionInfo
from UserSideApp.models import MealComponent


class MerchantAuthTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(name="測試餐廳", phone="0212345678")
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			merchant_name="testing-merchant",
			email="owner@example.com",
			phone="0900123456",
			password_hash=make_password("SecurePass!23"),
		)

	def test_register_creates_merchant_and_logs_in(self):
		response = self.client.post(
			reverse("merchantsideapp:register"),
			{
				"restaurant_name": "新餐廳",
				"merchant_name": "new-merchant",
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
				"merchant_name": "duplicate-merchant",
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
				"identifier": "owner@example.com",
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
				"identifier": "owner@example.com",
				"password": "WrongPass",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "帳號或密碼不正確。")
		self.assertNotIn(SESSION_MERCHANT_KEY, self.client.session)

	def test_login_rejects_restaurant_name_identifier(self):
		response = self.client.post(
			reverse("merchantsideapp:login"),
			{
				"identifier": "測試餐廳",
				"password": "SecurePass!23",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "帳號或密碼不正確。")
		self.assertNotIn(SESSION_MERCHANT_KEY, self.client.session)

	def test_login_accepts_merchant_phone_with_digit_normalization(self):
		response = self.client.post(
			reverse("merchantsideapp:login"),
			{
				"identifier": "0900-123-456",
				"password": "SecurePass!23",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(self.client.session.get(SESSION_MERCHANT_KEY), self.merchant.pk)

	def test_login_accepts_merchant_phone_identifier(self):
		response = self.client.post(
			reverse("merchantsideapp:login"),
			{
				"identifier": self.merchant.phone,
				"password": "SecurePass!23",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(self.client.session.get(SESSION_MERCHANT_KEY), self.merchant.pk)

	def test_login_accepts_merchant_name_identifier(self):
		response = self.client.post(
			reverse("merchantsideapp:login"),
			{
				"identifier": "testing-merchant",
				"password": "SecurePass!23",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(self.client.session.get(SESSION_MERCHANT_KEY), self.merchant.pk)

	def test_register_requires_unique_merchant_name(self):
		response = self.client.post(
			reverse("merchantsideapp:register"),
			{
				"restaurant_name": "另一間餐廳",
				"merchant_name": "testing-merchant",
				"email": "second@example.com",
				"password1": "UniquePass!23",
				"password2": "UniquePass!23",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "此商家名稱已被使用。")
		self.assertEqual(MerchantAccount.objects.filter(email="second@example.com").count(), 0)

	def test_dashboard_requires_authentication(self):
		response = self.client.get(reverse("merchantsideapp:dashboard"))
		self.assertEqual(response.status_code, 302)
		self.assertTrue(response.url.startswith(reverse("merchantsideapp:login")))

	def test_dashboard_displays_merchant_name_for_logged_in_merchant(self):
		session = self.client.session
		session[SESSION_MERCHANT_KEY] = self.merchant.pk
		session.save()
		response = self.client.get(reverse("merchantsideapp:dashboard"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.merchant.merchant_name)


class MerchantMealCreationTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(name="勇者餐館")
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			merchant_name="meal-merchant",
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
		self.assertEqual(component.metadata, {"notes": "雞胸肉"})
		nutrition = NutritionInfo.objects.get(meal=meal)
		self.assertEqual(float(nutrition.calories), 100.0)
		self.assertEqual(float(nutrition.protein), 25.0)
		self.assertEqual(float(nutrition.carbohydrate), 10.0)
		self.assertEqual(float(nutrition.fat), 5.0)
		self.assertEqual(float(nutrition.sodium), 0.0)
		self.assertTrue(nutrition.breakdown)
		self.assertEqual(nutrition.breakdown[0]["protein"], 25.0)

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


class MerchantMealImageUploadTests(TestCase):
	@staticmethod
	def _build_image_bytes(color=(255, 0, 0)):
		buffer = io.BytesIO()
		image = Image.new("RGB", (10, 10), color=color)
		image.save(buffer, format="PNG")
		return buffer.getvalue()


	def setUp(self):
		self.temp_media = tempfile.mkdtemp()
		self.addCleanup(lambda: shutil.rmtree(self.temp_media, ignore_errors=True))
		self.media_override = override_settings(MEDIA_ROOT=self.temp_media)
		self.media_override.enable()
		self.addCleanup(self.media_override.disable)
		self.restaurant = Restaurant.objects.create(name="上傳食堂")
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			merchant_name="upload-merchant",
			email="upload-owner@example.com",
			password_hash=make_password("UploadPass!45"),
		)
		session = self.client.session
		session[SESSION_MERCHANT_KEY] = self.merchant.pk
		session.save()

	def test_uploaded_image_saved_and_displayed(self):
		upload = SimpleUploadedFile(
			"hero-meal.png",
			self._build_image_bytes(),
			content_type="image/png",
		)
		response = self.client.post(
			reverse("merchantsideapp:add_meal"),
			{
				"name": "煙燻嫩雞沙拉",
				"category": "主食",
				"price": "180",
				"image_file": upload,
				"image_url": "https://example.com/fallback.jpg",
			},
		)
		form_errors = None
		if getattr(response, "context", None):
			contexts = response.context
			if isinstance(contexts, list):
				for ctx in contexts:
					if ctx and "form" in ctx:
						form_errors = ctx["form"].errors
						break
			elif "form" in contexts:
				form_errors = contexts["form"].errors
		self.assertEqual(response.status_code, 302, msg=form_errors)
		meal = Meal.objects.get(name="煙燻嫩雞沙拉")
		self.assertTrue(meal.image_file.name.startswith("meals/photos/"))
		self.assertTrue(meal.image_file.storage.exists(meal.image_file.name))
		detail = self.client.get(
			reverse("merchantsideapp:meal_detail", args=[meal.slug])
		)
		self.assertContains(detail, meal.image_file.url)
		self.assertNotContains(detail, "https://example.com/fallback.jpg")


class MerchantMealManagementTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(name="巧手廚坊")
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			merchant_name="manage-merchant",
			email="manage-owner@example.com",
			password_hash=make_password("ManagePass!45"),
		)
		self.available_meal = Meal.objects.create(
			restaurant=self.restaurant,
			name="暖心番茄燉飯",
			description="慢火拌炒的番茄燉飯",
			category="主食",
			price=280,
			is_available=True,
		)
		self.archived_meal = Meal.objects.create(
			restaurant=self.restaurant,
			name="涼拌手作豆腐",
			description="附芝麻醬的清爽小菜",
			category="小菜",
			price=120,
			is_available=False,
		)
		NutritionInfo.objects.create(
			meal=self.available_meal,
			calories=520,
			protein=25,
			fat=18,
			carbohydrate=60,
			sodium=800,
		)
		MealComponent.objects.create(
			meal=self.available_meal,
			name="雞胸肉",
			quantity="120g",
			calories=150,
			metadata={"allergens": ["花生", "蛋"]},
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
		nutrition_record = meal.nutrition
		nutrition_record.calories = Decimal("450.0")
		nutrition_record.protein = Decimal("18.0")
		nutrition_record.carbohydrate = Decimal("55.0")
		nutrition_record.fat = Decimal("12.0")
		nutrition_record.sodium = Decimal("800.0")
		nutrition_record.save()
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
		nutrition = NutritionInfo.objects.get(meal=meal)
		self.assertAlmostEqual(float(nutrition.calories), 120.0)
		self.assertAlmostEqual(float(nutrition.protein), 30.0)
		self.assertAlmostEqual(float(nutrition.carbohydrate), 0.0)
		self.assertAlmostEqual(float(nutrition.fat), 0.0)
		self.assertAlmostEqual(float(nutrition.sodium), 800.0)
		self.assertEqual(nutrition.breakdown[0]["protein"], 30.0)

	def test_delete_meal_marks_unavailable(self):
		self._login()
		meal = self.restaurant.meals.get(name="涼拌手作豆腐")
		response = self.client.post(
			reverse("merchantsideapp:delete_meal", args=[meal.id]),
			{"action": "deactivate"},
		)
		self.assertEqual(response.status_code, 302)
		meal.refresh_from_db()
		self.assertFalse(meal.is_available)

	def test_reactivate_archived_meal(self):
		self._login()
		meal = self.restaurant.meals.get(name="涼拌手作豆腐")
		meal.is_available = False
		meal.save(update_fields=["is_available"])
		response = self.client.post(
			reverse("merchantsideapp:delete_meal", args=[meal.id]),
			{"action": "activate"},
		)
		self.assertEqual(response.status_code, 302)
		meal.refresh_from_db()
		self.assertTrue(meal.is_available)

	def test_manage_page_shows_archived_preview(self):
		self._login()
		response = self.client.get(reverse("merchantsideapp:manage_meals"))
		self.assertContains(response, "已下架餐點")
		self.assertContains(response, "涼拌手作豆腐")

	def test_meal_detail_public_access(self):
		url = reverse("merchantsideapp:meal_detail", args=[self.available_meal.slug])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "暖心番茄燉飯")
		self.assertContains(response, "花生")
		self.assertContains(response, "雞胸肉")
		self.assertFalse(response.context["can_edit"])
		nutrition = response.context["nutrition"]
		self.assertEqual(float(nutrition["calories"]), 520.0)

	def test_meal_detail_marks_owner_can_edit(self):
		self._login()
		url = reverse("merchantsideapp:meal_detail", args=[self.available_meal.slug])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context["can_edit"])
		self.assertContains(response, "編輯餐點")

	def test_meal_detail_shows_image_or_placeholder(self):
		self.available_meal.image_url = "https://example.com/meal.jpg"
		self.available_meal.save(update_fields=["image_url"])
		url = reverse("merchantsideapp:meal_detail", args=[self.available_meal.slug])
		response = self.client.get(url)
		self.assertContains(response, "https://example.com/meal.jpg")
		placeholder_url = reverse("merchantsideapp:meal_detail", args=[self.archived_meal.slug])
		response_placeholder = self.client.get(placeholder_url)
		self.assertContains(response_placeholder, "尚未上傳餐點照片")


class MerchantDashboardTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(
			name="星級餐館",
			is_active=True,
			city="台北市",
			district="信義區",
			address="松壽路9號",
			rating=4.6,
			cuisine_type="地中海",
		)
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			merchant_name="dash-merchant",
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

	def test_update_restaurant_status(self):
		self._login()
		response = self.client.post(
			reverse("merchantsideapp:restaurant_status"),
			{"status": "closed"},
		)
		self.assertEqual(response.status_code, 302)
		self.restaurant.refresh_from_db()
		self.assertFalse(self.restaurant.is_active)

	def test_restaurant_detail_accessible_without_login(self):
		url = reverse("merchantsideapp:restaurant_detail", args=[self.restaurant.slug])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "星級餐館")
		self.assertFalse(response.context["can_edit"])

	def test_restaurant_detail_displays_stats_and_meals(self):
		self._login()
		url = reverse("merchantsideapp:restaurant_detail", args=[self.restaurant.slug])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "星級餐館")
		self.assertContains(response, "台北市")
		self.assertContains(response, "奶油海鮮燉飯")
		self.assertContains(response, "日式炸豬排")
		stats = response.context["stats"]
		self.assertEqual(stats["total_meals"], 2)
		self.assertEqual(stats["available_meals"], 1)
		self.assertTrue(response.context["can_edit"])

	def test_restaurant_detail_contains_meal_links(self):
		url = reverse("merchantsideapp:restaurant_detail", args=[self.restaurant.slug])
		response = self.client.get(url)
		meal_url = reverse("merchantsideapp:meal_detail", args=[self.meal_new.slug])
		self.assertContains(response, f'data-meal-url="{meal_url}"')
		self.assertContains(response, "查看餐點")


class MerchantSettingsTests(TestCase):
	def setUp(self):
		self.restaurant = Restaurant.objects.create(
			name="設定餐廳",
			address="舊地址",
			price_range=Restaurant.PriceRange.MEDIUM,
		)
		self.merchant = MerchantAccount.objects.create(
			restaurant=self.restaurant,
			merchant_name="設定達人",
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
		self.assertContains(response, self.merchant.merchant_name)
		self.assertContains(response, self.merchant.email)
		self.assertContains(response, self.restaurant.name)

	def test_account_form_updates_profile(self):
		self._login()
		response = self.client.post(
			reverse("merchantsideapp:settings"),
			{
				"form_type": "account",
				"merchant_name": "全新設定達人",
				"email": "updated-owner@example.com",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.merchant.refresh_from_db()
		self.assertEqual(self.merchant.email, "updated-owner@example.com")
		self.assertEqual(self.merchant.merchant_name, "全新設定達人")

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
