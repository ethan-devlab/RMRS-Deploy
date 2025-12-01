from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.hashers import check_password, make_password
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from MerchantSideApp.models import Meal, Restaurant, NutritionInfo
from RecommendationSystem.models import RecommendationHistory
from RecommendationSystem.services import DEFAULT_COOLDOWN_DAYS

from .auth_utils import SESSION_USER_KEY
from .models import (
	AppUser,
	DailyMealRecord,
	Favorite,
	NotificationSetting,
	Review,
	UserPreference,
	WeeklyIntakeSummary,
)


class UserAuthTests(TestCase):
	def setUp(self):
		self.password = "SecurePass!23"
		self.user = AppUser.objects.create(
			username="tester",
			email="tester@example.com",
			phone="0987654321",
			password_hash=make_password(self.password),
		)
		self.phone_user = AppUser.objects.create(
			username="phoneuser",
			email="phone@example.com",
			phone="0912345678",
			password_hash=make_password(self.password),
		)

	def _post_login(self, identifier, password=None):
		return self.client.post(
			reverse("usersideapp:login"),
			{"identifier": identifier, "password": password or self.password},
		)

	def test_login_with_email_identifier(self):
		response = self._post_login(self.user.email)
		self.assertRedirects(response, reverse("usersideapp:home"))
		self.assertEqual(self.client.session.get(SESSION_USER_KEY), self.user.pk)

	def test_login_with_username_identifier(self):
		response = self._post_login(self.user.username)
		self.assertRedirects(response, reverse("usersideapp:home"))
		self.assertEqual(self.client.session.get(SESSION_USER_KEY), self.user.pk)

	def test_login_rejects_unknown_identifier(self):
		response = self._post_login("unknown@example.com")
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "帳號或密碼不正確。")
		self.assertNotIn(SESSION_USER_KEY, self.client.session)

	def test_login_accepts_digits_only_variant(self):
		response = self._post_login("0912-345-678")
		self.assertRedirects(response, reverse("usersideapp:home"))
		self.assertEqual(self.client.session.get(SESSION_USER_KEY), self.phone_user.pk)

	def test_login_with_phone_identifier(self):
		response = self._post_login(self.user.phone)
		self.assertRedirects(response, reverse("usersideapp:home"))
		self.assertEqual(self.client.session.get(SESSION_USER_KEY), self.user.pk)


class UserPortalTestCase(TestCase):
	def setUp(self):
		self.user = AppUser.objects.create(
			username="tester",
			email="tester@example.com",
			password_hash=make_password("InitialPass!23"),
		)
		self.restaurant = Restaurant.objects.create(name="測試餐廳")
		self.other_restaurant = Restaurant.objects.create(name="另一家餐廳")
		self.meal = Meal.objects.create(
			restaurant=self.restaurant,
			name="經典飯盒",
			category="主食",
		)
		self.other_meal = Meal.objects.create(
			restaurant=self.other_restaurant,
			name="異國燉飯",
			category="飲品",
		)

	def _login(self):
		session = self.client.session
		session[SESSION_USER_KEY] = self.user.pk
		session.save()

	def test_meal_record_prevents_weekly_duplicate(self):
		self._login()
		DailyMealRecord.objects.create(
			user=self.user,
			date=date(2025, 1, 6),
			meal_type=DailyMealRecord.MealType.BREAKFAST,
			meal_name="經典蛋餅",
			calories=400,
			protein_grams=15,
			carb_grams=30,
			fat_grams=10,
		)

		response = self.client.post(
			reverse("usersideapp:record"),
			{
				"intent": "create",
				"date": "2025-01-10",
				"meal_type": DailyMealRecord.MealType.DINNER,
				"meal_name": "經典蛋餅",
				"calories": "520",
				"protein_grams": "20",
				"carb_grams": "40",
				"fat_grams": "18",
				"ingredients_text": "",
				"meal_notes": "",
				"components_payload": "[]",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			DailyMealRecord.objects.filter(user=self.user, meal_name="經典蛋餅").count(),
			1,
		)

	def test_meal_record_updates_weekly_summary(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:record"),
			{
				"intent": "create",
				"date": timezone.now().date().isoformat(),
				"meal_type": DailyMealRecord.MealType.LUNCH,
				"meal_name": "舒肥雞胸 + 沙拉",
				"calories": "610",
				"protein_grams": "35",
				"carb_grams": "45",
				"fat_grams": "20",
				"ingredients_text": "雞胸肉\n生菜",
				"meal_notes": "午餐",
				"components_payload": '[{"name":"雞胸肉","quantity":"150g","calories":310}]',
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		summary = WeeklyIntakeSummary.objects.first()
		self.assertIsNotNone(summary)
		self.assertEqual(float(summary.total_calories), 610.0)
		self.assertEqual(summary.meal_count, 1)

	def test_notification_settings_update(self):
		self._login()
		self.client.get(reverse("usersideapp:notify"))
		settings = NotificationSetting.objects.filter(user=self.user)
		self.assertGreater(settings.count(), 0)
		form_data = {
			"action": "update_settings",
		}
		for idx, setting in enumerate(settings):
			prefix = f"form-{idx}"
			form_data[f"{prefix}-id"] = setting.id
			form_data[f"{prefix}-is_enabled"] = "on"
			form_data[f"{prefix}-scheduled_time"] = setting.scheduled_time.strftime("%H:%M") if setting.scheduled_time else ""
			form_data[f"{prefix}-channel"] = setting.channel
		form_data["form-TOTAL_FORMS"] = settings.count()
		form_data["form-INITIAL_FORMS"] = settings.count()
		form_data["form-MIN_NUM_FORMS"] = 0
		form_data["form-MAX_NUM_FORMS"] = 1000
		form_data["form-0-scheduled_time"] = "09:00"
		response = self.client.post(reverse("usersideapp:notify"), form_data, follow=True)
		self.assertEqual(response.status_code, 200)
		settings[0].refresh_from_db()
		self.assertEqual(settings[0].scheduled_time.strftime("%H:%M"), "09:00")

	def test_user_can_edit_meal_record(self):
		self._login()
		original_date = date(2025, 1, 6)
		create_response = self.client.post(
			reverse("usersideapp:record"),
			{
				"intent": "create",
				"date": original_date.isoformat(),
				"meal_type": DailyMealRecord.MealType.LUNCH,
				"meal_name": "舒肥雞胸 + 沙拉",
				"calories": "600",
				"protein_grams": "40",
				"carb_grams": "20",
				"fat_grams": "18",
				"ingredients_text": "雞胸肉\n沙拉",
				"meal_notes": "初始版本",
				"components_payload": '[{"name":"雞胸肉","quantity":"150g","calories":400}]',
			},
			follow=True,
		)
		self.assertEqual(create_response.status_code, 200)
		record = DailyMealRecord.objects.get(user=self.user)
		self.assertEqual(record.components.count(), 1)
		old_week_start = original_date - timedelta(days=original_date.weekday())
		new_date = date(2025, 1, 15)
		update_response = self.client.post(
			reverse("usersideapp:record"),
			{
				"intent": "update",
				"record_id": record.id,
				"date": new_date.isoformat(),
				"meal_type": DailyMealRecord.MealType.DINNER,
				"meal_name": "高蛋白餐盒",
				"calories": "720",
				"protein_grams": "55",
				"carb_grams": "60",
				"fat_grams": "22",
				"ingredients_text": "糙米\n雞肉\n花椰菜",
				"meal_notes": "更新後版本",
				"components_payload": (
					'[{"name":"雞胸肉","quantity":"200g","calories":420},'
					'{"name":"糙米","quantity":"半碗","calories":180}]'
				),
			},
			follow=True,
		)
		self.assertEqual(update_response.status_code, 200)
		record.refresh_from_db()
		self.assertEqual(record.meal_name, "高蛋白餐盒")
		self.assertEqual(float(record.calories), 720.0)
		components = list(record.components.all())
		self.assertEqual(len(components), 2)
		component_map = {component.name: component for component in components}
		self.assertIn("糙米", component_map)
		self.assertAlmostEqual(float(component_map["糙米"].calories), 180.0)
		self.assertEqual(component_map["雞胸肉"].quantity, "200g")
		old_summary = WeeklyIntakeSummary.objects.get(user=self.user, week_start=old_week_start)
		self.assertEqual(old_summary.meal_count, 0)
		new_week_start = new_date - timedelta(days=new_date.weekday())
		new_summary = WeeklyIntakeSummary.objects.get(user=self.user, week_start=new_week_start)
		self.assertEqual(new_summary.meal_count, 1)
		self.assertEqual(float(new_summary.total_calories), 720.0)

	def test_edit_record_prefills_components(self):
		self._login()
		record = DailyMealRecord.objects.create(
			user=self.user,
			date=date(2025, 1, 10),
			meal_type=DailyMealRecord.MealType.LUNCH,
			meal_name="元氣餐",
			calories=500,
			protein_grams=30,
			carb_grams=40,
			fat_grams=15,
		)
		record.components.create(name="雞胸肉", quantity="150g", calories=300)
		response = self.client.get(reverse("usersideapp:record") + f"?edit={record.id}")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["editing_record"].id, record.id)
		self.assertIn("雞胸肉", response.context["components_seed"])
		meal_form = response.context["meal_form"]
		self.assertIn("雞胸肉", meal_form.initial.get("components_payload", ""))

	def test_record_creation_uses_selected_meal_nutrition(self):
		self._login()
		nutrition_meal = Meal.objects.create(
			restaurant=self.restaurant,
			name="特製餐",
			is_available=True,
		)
		NutritionInfo.objects.create(
			meal=nutrition_meal,
			calories=Decimal("650.0"),
			protein=Decimal("40.0"),
			carbohydrate=Decimal("70.0"),
			fat=Decimal("20.0"),
			sodium=Decimal("800.0"),
		)
		response = self.client.post(
			reverse("usersideapp:record"),
			{
				"intent": "create",
				"date": "2025-01-15",
				"meal_type": DailyMealRecord.MealType.DINNER,
				"meal_name": "",
				"restaurant": self.restaurant.id,
				"source_meal": nutrition_meal.id,
				"calories": "",
				"protein_grams": "",
				"carb_grams": "",
				"fat_grams": "",
				"ingredients_text": "",
				"components_payload": "[]",
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		record = DailyMealRecord.objects.filter(user=self.user).latest("id")
		self.assertEqual(record.source_meal, nutrition_meal)
		self.assertEqual(record.meal_name, "特製餐")
		self.assertAlmostEqual(float(record.calories), 650.0)
		self.assertAlmostEqual(float(record.protein_grams), 40.0)
		self.assertAlmostEqual(float(record.carb_grams), 70.0)
		self.assertAlmostEqual(float(record.fat_grams), 20.0)
		self.assertTrue(
			RecommendationHistory.objects.filter(
				user=self.user,
				meal=nutrition_meal,
				was_selected=True,
			).exists()
		)

	def test_restaurant_meals_api_returns_nutrition(self):
		self._login()
		NutritionInfo.objects.create(
			meal=self.meal,
			calories=Decimal("480.0"),
			protein=Decimal("32.0"),
			carbohydrate=Decimal("55.0"),
			fat=Decimal("16.0"),
			sodium=Decimal("600.0"),
		)
		response = self.client.get(
			reverse("usersideapp:restaurant_meals_api"),
			{"restaurant_id": self.restaurant.id},
		)
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertTrue(payload["meals"])
		meal_info = next((item for item in payload["meals"] if item["id"] == self.meal.id), None)
		self.assertIsNotNone(meal_info)
		self.assertEqual(meal_info["nutrition"]["calories"], "480.00")

	def test_settings_page_renders_preference_form(self):
		self._login()
		response = self.client.get(reverse("usersideapp:settings"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "常見料理類型")
		self.assertContains(response, "帳戶資訊")
		self.assertEqual(UserPreference.objects.filter(user=self.user).count(), 1)

	def test_user_can_update_preferences(self):
		self._login()
		payload = {
			"form_type": "preferences",
			"cuisine_type": "日式",
			"category": "主食",
			"price_range": UserPreference.PriceRange.MEDIUM,
			"is_vegetarian": "on",
			"avoid_spicy": "on",
			"recommendation_cooldown_days": "9",
		}
		response = self.client.post(
			reverse("usersideapp:settings"),
			payload,
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		preference = UserPreference.objects.get(user=self.user)
		self.assertEqual(preference.cuisine_type, "日式")
		self.assertEqual(preference.category, "主食")
		self.assertEqual(preference.price_range, UserPreference.PriceRange.MEDIUM)
		self.assertTrue(preference.is_vegetarian)
		self.assertTrue(preference.avoid_spicy)
		self.assertEqual(preference.recommendation_cooldown_days, 9)

	def test_user_can_update_account_info(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:settings"),
			{
				"form_type": "account",
				"full_name": "Tester Updated",
				"email": "tester+new@example.com",
				"phone": "",
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertEqual(self.user.full_name, "Tester Updated")
		self.assertEqual(self.user.email, "tester+new@example.com")
		self.assertIsNone(self.user.phone)

	def test_user_can_update_phone_number(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:settings"),
			{
				"form_type": "account",
				"full_name": "Tester",
				"email": "tester@example.com",
				"phone": "0912-345-678",
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertEqual(self.user.phone, "0912345678")

	def test_account_update_requires_unique_email(self):
		self._login()
		AppUser.objects.create(
			username="other",
			email="taken@example.com",
			password_hash="dummy",
		)
		response = self.client.post(
			reverse("usersideapp:settings"),
			{
				"form_type": "account",
				"full_name": "Another",
				"email": "taken@example.com",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertEqual(self.user.email, "tester@example.com")
		self.assertContains(response, "此 Email 已被其他帳戶使用。")

	def test_account_update_requires_unique_phone(self):
		self._login()
		AppUser.objects.create(
			username="other",
			email="taken2@example.com",
			phone="0912345678",
			password_hash="dummy",
		)
		response = self.client.post(
			reverse("usersideapp:settings"),
			{
				"form_type": "account",
				"full_name": "Tester",
				"email": "tester@example.com",
				"phone": "0912 345 678",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertIsNone(self.user.phone)
		self.assertContains(response, "此手機號碼已被其他帳戶使用。")

	def test_user_can_change_password(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:settings"),
			{
				"form_type": "password",
				"current_password": "InitialPass!23",
				"new_password1": "NewSecret#45",
				"new_password2": "NewSecret#45",
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertTrue(check_password("NewSecret#45", self.user.password_hash))

	def test_password_change_requires_current_password(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:settings"),
			{
				"form_type": "password",
				"current_password": "wrong",
				"new_password1": "NewSecret#45",
				"new_password2": "NewSecret#45",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertTrue(check_password("InitialPass!23", self.user.password_hash))
		self.assertContains(response, "目前密碼不正確。")

	def test_password_change_requires_matching_confirmation(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:settings"),
			{
				"form_type": "password",
				"current_password": "InitialPass!23",
				"new_password1": "NewSecret#45",
				"new_password2": "Mismatch",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertTrue(check_password("InitialPass!23", self.user.password_hash))
		self.assertContains(response, "兩次輸入的新密碼不一致。")

	def test_interactions_page_renders(self):
		self._login()
		response = self.client.get(reverse("usersideapp:interactions"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "我的互動")
		self.assertContains(response, "撰寫評論")
		self.assertContains(response, "收藏餐點")

	def test_user_can_submit_review(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:interactions"),
			{
				"form_type": "review",
				"restaurant": self.restaurant.id,
				"meal": self.meal.id,
				"rating": 5,
				"comment": "超好吃！",
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Review.objects.filter(user=self.user).count(), 1)
		self.assertContains(response, "感謝您的評論！")

	def test_user_cannot_create_duplicate_review(self):
		self._login()
		Review.objects.create(
			user=self.user,
			meal=self.meal,
			restaurant=self.restaurant,
			rating=4,
			comment="第一次評論",
		)
		response = self.client.post(
			reverse("usersideapp:interactions"),
			{
				"form_type": "review",
				"restaurant": self.restaurant.id,
				"meal": self.meal.id,
				"rating": 5,
				"comment": "嘗試重複",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "你已評論過此餐點")

	def test_search_filters_by_meal_category(self):
		self._login()
		response = self.client.get(
			reverse("usersideapp:search"),
			{"category": "主食"},
		)
		self.assertEqual(response.status_code, 200)
		restaurants = response.context["restaurants"]
		self.assertEqual(len(restaurants), 1)
		self.assertEqual(restaurants[0].name, self.restaurant.name)
		category_choices = response.context["form"].fields["category"].choices
		self.assertIn(("主食", "主食"), category_choices)
		self.assertNotContains(response, self.other_restaurant.name)

	def test_random_recommendation_category_filter(self):
		self._login()
		dessert_restaurant = Restaurant.objects.create(name="甜點小館", rating=4.7)
		Meal.objects.create(
			restaurant=dessert_restaurant,
			name="草莓蛋糕",
			category="甜點",
		)
		Meal.objects.create(
			restaurant=dessert_restaurant,
			name="檸檬塔",
			category="甜點",
		)
		response = self.client.post(
			reverse("usersideapp:random_data"),
			{"category": "甜點", "limit": "4"},
		)
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		primary_cards = payload["primary"]["cards"]
		self.assertGreater(len(primary_cards), 0)
		meal_names = {card["meal"]["name"] for card in primary_cards}
		self.assertTrue(meal_names.issubset({"草莓蛋糕", "檸檬塔"}))
		self.assertNotIn("經典飯盒", meal_names)

	def test_random_page_displays_cooldown_hint(self):
		self._login()
		response = self.client.get(reverse("usersideapp:random"))
		self.assertEqual(response.status_code, 200)
		expected = f"系統會避免推薦過去 {DEFAULT_COOLDOWN_DAYS} 天內你選過的餐點。"
		self.assertContains(response, expected)

	def test_random_page_uses_user_defined_cooldown_hint(self):
		self._login()
		UserPreference.objects.create(
			user=self.user,
			recommendation_cooldown_days=5,
		)
		response = self.client.get(reverse("usersideapp:random"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "系統會避免推薦過去 5 天內你選過的餐點。")

	def test_user_can_edit_review_via_hidden_field(self):
		self._login()
		review = Review.objects.create(
			user=self.user,
			meal=self.meal,
			restaurant=self.restaurant,
			rating=3,
			comment="初始評論",
		)
		response = self.client.post(
			reverse("usersideapp:interactions"),
			{
				"form_type": "review",
				"review_id": review.id,
				"restaurant": self.restaurant.id,
				"meal": self.meal.id,
				"rating": 5,
				"comment": "更新後評論",
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		review.refresh_from_db()
		self.assertEqual(review.rating, 5)
		self.assertEqual(review.comment, "更新後評論")
		self.assertContains(response, "評論已更新")

	def test_review_requires_matching_restaurant(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:interactions"),
			{
				"form_type": "review",
				"restaurant": self.restaurant.id,
				"meal": self.other_meal.id,
				"rating": 4,
				"comment": "錯誤測試",
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Review.objects.count(), 0)
		self.assertContains(response, "評論送出失敗")

	def test_user_can_add_and_remove_favorite(self):
		self._login()
		add_response = self.client.post(
			reverse("usersideapp:interactions"),
			{
				"form_type": "favorite_add",
				"meal": self.meal.id,
			},
			follow=True,
		)
		self.assertEqual(add_response.status_code, 200)
		self.assertEqual(Favorite.objects.filter(user=self.user).count(), 1)
		favorite = Favorite.objects.get(user=self.user)
		self.assertContains(add_response, "已加入收藏餐點")
		remove_response = self.client.post(
			reverse("usersideapp:interactions"),
			{
				"form_type": "favorite_remove",
				"favorite_id": favorite.id,
			},
			follow=True,
		)
		self.assertEqual(remove_response.status_code, 200)
		self.assertEqual(Favorite.objects.filter(user=self.user).count(), 0)
		self.assertContains(remove_response, "已移除收藏餐點。")

	def test_search_filters_by_meal_category(self):
		self._login()
		response = self.client.get(
			reverse("usersideapp:search"),
			{"category": self.meal.category},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.restaurant.name)
		self.assertNotContains(response, self.other_restaurant.name)

	def test_search_returns_meal_results(self):
		self._login()
		response = self.client.get(
			reverse("usersideapp:search"),
			{"keyword": self.meal.name},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.meal.name)
		meal_url = reverse("merchantsideapp:meal_detail", args=[self.meal.slug])
		self.assertContains(response, meal_url)

	def test_search_displays_restaurant_links(self):
		self._login()
		response = self.client.get(
			reverse("usersideapp:search"),
			{"keyword": self.restaurant.name},
		)
		self.assertEqual(response.status_code, 200)
		restaurant_url = reverse("merchantsideapp:restaurant_detail", args=[self.restaurant.slug])
		self.assertContains(response, restaurant_url)

	def test_random_page_defaults_to_preferences(self):
		self._login()
		UserPreference.objects.create(
			user=self.user,
			cuisine_type="日式",
			price_range=UserPreference.PriceRange.MEDIUM,
			is_vegetarian=True,
			avoid_spicy=True,
		)
		match_restaurant = Restaurant.objects.create(
			name="日式小館",
			cuisine_type="日式",
			price_range=Restaurant.PriceRange.MEDIUM,
			city="台北",
			district="信義",
		)
		Meal.objects.create(
			restaurant=match_restaurant,
			name="味噌湯麵",
			is_vegetarian=True,
			is_spicy=False,
		)
		response = self.client.get(reverse("usersideapp:random"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "味噌湯麵")

	def test_random_page_displays_meal_and_restaurant_links(self):
		self._login()
		response = self.client.get(reverse("usersideapp:random"))
		self.assertEqual(response.status_code, 200)
		meal_url = reverse("merchantsideapp:meal_detail", args=[self.meal.slug])
		restaurant_url = reverse("merchantsideapp:restaurant_detail", args=[self.restaurant.slug])
		self.assertContains(response, meal_url)
		self.assertContains(response, restaurant_url)

	def test_random_page_filter_form_limits_results(self):
		self._login()
		cheap_restaurant = Restaurant.objects.create(
			name="平價便當",
			price_range=Restaurant.PriceRange.LOW,
			cuisine_type="台式",
		)
		Meal.objects.create(restaurant=cheap_restaurant, name="銅板便當", is_spicy=False)
		expensive_restaurant = Restaurant.objects.create(
			name="高級牛排",
			price_range=Restaurant.PriceRange.HIGH,
			cuisine_type="西式",
		)
		Meal.objects.create(restaurant=expensive_restaurant, name="豪華牛排", is_spicy=False)
		response = self.client.post(
			reverse("usersideapp:random"),
			{
				"price_range": Restaurant.PriceRange.LOW,
				"limit": 2,
				"action": "filters",
			},
		)
		self.assertEqual(response.status_code, 200)
		primary = response.context["primary_recommendations"]
		self.assertGreater(len(primary), 0)
		self.assertTrue(
			all(card["restaurant"].price_range == Restaurant.PriceRange.LOW for card in primary)
		)
		self.assertContains(response, "銅板便當")

	def test_random_page_filters_by_category(self):
		self._login()
		matching_restaurant = Restaurant.objects.create(name="分類餐廳", cuisine_type="混合")
		Meal.objects.create(
			restaurant=matching_restaurant,
			name="辣味咖哩",
			category="咖哩",
		)
		Meal.objects.filter(pk=self.other_meal.pk).update(category="甜點")
		response = self.client.post(
			reverse("usersideapp:random"),
			{
				"category": "咖哩",
				"action": "filters",
				"limit": 4,
			},
		)
		self.assertEqual(response.status_code, 200)
		primary = response.context["primary_recommendations"]
		self.assertGreater(len(primary), 0)
		self.assertTrue(all(card["meal"].category == "咖哩" for card in primary))
		self.assertContains(response, "辣味咖哩")

	def test_random_api_returns_primary_cards(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:random_data"),
			{"action": "surprise", "limit": 1},
		)
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertIn("primary", payload)
		self.assertGreaterEqual(len(payload["primary"].get("cards", [])), 1)
		card = payload["primary"]["cards"][0]
		meal_url = reverse("merchantsideapp:meal_detail", args=[card["meal"]["slug"]])
		restaurant_url = reverse(
			"merchantsideapp:restaurant_detail", args=[card["restaurant"]["slug"]]
		)
		self.assertEqual(card["meal"].get("url"), meal_url)
		self.assertEqual(card["restaurant"].get("url"), restaurant_url)
		self.assertIn("cooldownDays", payload)
		self.assertEqual(payload["cooldownDays"], DEFAULT_COOLDOWN_DAYS)

	def test_random_api_returns_user_cooldown_days(self):
		self._login()
		UserPreference.objects.create(
			user=self.user,
			recommendation_cooldown_days=4,
		)
		response = self.client.post(
			reverse("usersideapp:random_data"),
			{"action": "surprise", "limit": 1},
		)
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertEqual(payload["cooldownDays"], 4)

	def test_random_api_reports_validation_errors(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:random_data"),
			{"action": "filters", "price_range": "超貴"},
		)
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertIn("formErrors", payload)
		self.assertTrue(payload["formErrors"])

	def test_health_page_without_records_prompts_logging(self):
		self._login()
		response = self.client.get(reverse("usersideapp:health"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "開始記錄，取得專屬建議")

	def test_health_page_with_recent_records_shows_macro_feedback(self):
		self._login()
		today = timezone.now().date()
		DailyMealRecord.objects.create(
			user=self.user,
			date=today,
			meal_type=DailyMealRecord.MealType.BREAKFAST,
			meal_name="高碳早餐",
			calories=520,
			protein_grams=18,
			carb_grams=85,
			fat_grams=12,
		)
		DailyMealRecord.objects.create(
			user=self.user,
			date=today,
			meal_type=DailyMealRecord.MealType.LUNCH,
			meal_name="高碳午餐",
			calories=720,
			protein_grams=25,
			carb_grams=110,
			fat_grams=20,
		)
		DailyMealRecord.objects.create(
			user=self.user,
			date=today,
			meal_type=DailyMealRecord.MealType.DINNER,
			meal_name="澱粉晚餐",
			calories=680,
			protein_grams=20,
			carb_grams=95,
			fat_grams=18,
		)
		response = self.client.get(reverse("usersideapp:health"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "碳水偏多")
		self.assertContains(response, "澱粉份量微調")
