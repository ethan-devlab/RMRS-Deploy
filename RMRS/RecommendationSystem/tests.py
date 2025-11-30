from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from MerchantSideApp.models import Meal, Restaurant
from RecommendationSystem.models import RecommendationHistory
from RecommendationSystem.services import record_user_choice, recent_selected_meal_ids
from UserSideApp.models import AppUser, UserPreference
from UserSideApp.services import RecommendationEngine, RecommendationFilters


class RecommendationHistoryTests(TestCase):
	def setUp(self):
		self.user = AppUser.objects.create(
			username="history-user",
			email="history@example.com",
			password_hash="dummy",
		)
		self.restaurant = Restaurant.objects.create(
			name="歷史餐廳",
			is_active=True,
		)
		self.meal = Meal.objects.create(
			restaurant=self.restaurant,
			name="香煎雞胸",
			category="主食",
			price=250,
		)
		self.other_meal = Meal.objects.create(
			restaurant=self.restaurant,
			name="慢燉牛腩",
			category="主食",
			price=280,
		)

	def test_record_user_choice_creates_history(self):
		record_user_choice(self.user, self.meal)
		history = RecommendationHistory.objects.get(user=self.user, meal=self.meal)
		self.assertTrue(history.was_selected)
		self.assertEqual(history.restaurant, self.restaurant)
		ids = list(recent_selected_meal_ids(self.user))
		self.assertEqual(ids, [self.meal.id])

	def test_engine_skips_recently_selected_meals(self):
		record_user_choice(self.user, self.meal)
		engine = RecommendationEngine(self.user)
		filters = RecommendationFilters(limit=5)
		results = engine.apply_filters(filters)
		self.assertNotIn(self.meal, results)
		self.assertIn(self.other_meal, results)

	def test_engine_allows_meal_after_cooldown_window(self):
		record = record_user_choice(self.user, self.meal)
		RecommendationHistory.objects.filter(pk=record.pk).update(
			recommended_at=timezone.now() - timedelta(days=8)
		)
		engine = RecommendationEngine(self.user)
		filters = RecommendationFilters(limit=5)
		results = engine.apply_filters(filters)
		self.assertIn(self.meal, results)

	def test_engine_respects_default_cooldown_setting(self):
		record = record_user_choice(self.user, self.meal)
		RecommendationHistory.objects.filter(pk=record.pk).update(
			recommended_at=timezone.now() - timedelta(days=4)
		)
		filters = RecommendationFilters(limit=5)
		engine = RecommendationEngine(self.user)
		results = engine.apply_filters(filters)
		self.assertNotIn(self.meal, results)

	def test_user_preference_overrides_cooldown_window(self):
		record = record_user_choice(self.user, self.meal)
		RecommendationHistory.objects.filter(pk=record.pk).update(
			recommended_at=timezone.now() - timedelta(days=8)
		)
		filters = RecommendationFilters(limit=5)
		UserPreference.objects.create(
			user=self.user,
			recommendation_cooldown_days=10,
		)
		engine = RecommendationEngine(self.user)
		results = engine.apply_filters(filters)
		self.assertNotIn(self.meal, results)
		preference = self.user.preferences
		preference.recommendation_cooldown_days = 3
		preference.save()
		again_results = RecommendationEngine(self.user).apply_filters(filters)
		self.assertIn(self.meal, again_results)
