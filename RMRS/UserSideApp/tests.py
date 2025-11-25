from datetime import date, timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from MerchantSideApp.models import Meal, Restaurant

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


class UserPortalTestCase(TestCase):
	def setUp(self):
		self.user = AppUser.objects.create(
			username="tester",
			email="tester@example.com",
			password_hash=make_password("InitialPass!23"),
		)
		self.restaurant = Restaurant.objects.create(name="測試餐廳")
		self.other_restaurant = Restaurant.objects.create(name="另一家餐廳")
		self.meal = Meal.objects.create(restaurant=self.restaurant, name="經典飯盒")
		self.other_meal = Meal.objects.create(restaurant=self.other_restaurant, name="異國燉飯")

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
			"price_range": UserPreference.PriceRange.MEDIUM,
			"is_vegetarian": "on",
			"avoid_spicy": "on",
		}
		response = self.client.post(
			reverse("usersideapp:settings"),
			payload,
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		preference = UserPreference.objects.get(user=self.user)
		self.assertEqual(preference.cuisine_type, "日式")
		self.assertEqual(preference.price_range, UserPreference.PriceRange.MEDIUM)
		self.assertTrue(preference.is_vegetarian)
		self.assertTrue(preference.avoid_spicy)

	def test_user_can_update_account_info(self):
		self._login()
		response = self.client.post(
			reverse("usersideapp:settings"),
			{
				"form_type": "account",
				"full_name": "Tester Updated",
				"email": "tester+new@example.com",
			},
			follow=True,
		)
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertEqual(self.user.full_name, "Tester Updated")
		self.assertEqual(self.user.email, "tester+new@example.com")

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
		self.assertEqual(Review.objects.filter(user=self.user, meal=self.meal).count(), 1)

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
