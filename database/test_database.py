"""
隨機餐點推薦系統 - 單元測試
測試資料庫管理器和推薦引擎的功能
"""

import unittest
from db_manager import DatabaseManager
from recommendation_engine import RecommendationEngine


class TestDatabaseManager(unittest.TestCase):
    """測試 DatabaseManager 類別"""
    
    @classmethod
    def setUpClass(cls):
        """測試開始前的設定"""
        cls.db = DatabaseManager()
        cls.db.connect()
    
    @classmethod
    def tearDownClass(cls):
        """測試結束後的清理"""
        cls.db.disconnect()
    
    def test_connection(self):
        """測試資料庫連線"""
        self.assertIsNotNone(self.db.connection)
        self.assertTrue(self.db.connection.is_connected())
    
    def test_get_all_restaurants(self):
        """測試取得所有餐廳"""
        restaurants = self.db.get_all_restaurants()
        self.assertIsInstance(restaurants, list)
        self.assertGreater(len(restaurants), 0)
        
        # 檢查第一個餐廳的資料結構
        if restaurants:
            restaurant = restaurants[0]
            self.assertIn('id', restaurant)
            self.assertIn('name', restaurant)
            self.assertIn('cuisine_type', restaurant)
    
    def test_get_restaurant_by_id(self):
        """測試根據ID取得餐廳"""
        restaurant = self.db.get_restaurant_by_id(1)
        self.assertIsNotNone(restaurant)
        self.assertEqual(restaurant['id'], 1)
        self.assertIn('name', restaurant)
    
    def test_get_all_meals(self):
        """測試取得所有餐點"""
        meals = self.db.get_all_meals()
        self.assertIsInstance(meals, list)
        self.assertGreater(len(meals), 0)
        
        # 檢查第一個餐點的資料結構
        if meals:
            meal = meals[0]
            self.assertIn('id', meal)
            self.assertIn('name', meal)
            self.assertIn('restaurant_name', meal)
    
    def test_get_meal_by_id(self):
        """測試根據ID取得餐點"""
        meal = self.db.get_meal_by_id(1)
        self.assertIsNotNone(meal)
        self.assertEqual(meal['id'], 1)
        self.assertIn('name', meal)
    
    def test_get_random_meal(self):
        """測試隨機取得餐點"""
        meals = self.db.get_random_meal(5)
        self.assertIsInstance(meals, list)
        self.assertLessEqual(len(meals), 5)
        self.assertGreater(len(meals), 0)
    
    def test_get_restaurants_by_cuisine(self):
        """測試根據料理類型取得餐廳"""
        restaurants = self.db.get_restaurants_by_cuisine('台式')
        self.assertIsInstance(restaurants, list)
        
        # 如果有結果，檢查料理類型是否正確
        for restaurant in restaurants:
            self.assertEqual(restaurant['cuisine_type'], '台式')
    
    def test_get_meals_by_restaurant(self):
        """測試取得某餐廳的餐點"""
        meals = self.db.get_meals_by_restaurant(1)
        self.assertIsInstance(meals, list)
        
        # 如果有結果，檢查餐廳ID是否正確
        for meal in meals:
            self.assertEqual(meal['restaurant_id'], 1)
    
    def test_get_popular_meals(self):
        """測試取得熱門餐點"""
        meals = self.db.get_popular_meals(5)
        self.assertIsInstance(meals, list)
        self.assertLessEqual(len(meals), 5)
    
    def test_get_cuisine_statistics(self):
        """測試料理類型統計"""
        stats = self.db.get_cuisine_statistics()
        self.assertIsInstance(stats, list)
        self.assertGreater(len(stats), 0)
        
        # 檢查統計資料結構
        if stats:
            stat = stats[0]
            self.assertIn('cuisine_type', stat)
            self.assertIn('count', stat)
    
    def test_get_user_by_username(self):
        """測試根據使用者名稱取得使用者"""
        user = self.db.get_user_by_username('testuser1')
        if user:  # 如果測試資料存在
            self.assertEqual(user['username'], 'testuser1')
            self.assertIn('email', user)
    
    def test_is_favorite(self):
        """測試檢查收藏狀態"""
        # 假設使用者1已收藏餐點1（根據測試資料）
        is_fav = self.db.is_favorite(1, 1)
        self.assertIsInstance(is_fav, bool)


class TestRecommendationEngine(unittest.TestCase):
    """測試 RecommendationEngine 類別"""
    
    @classmethod
    def setUpClass(cls):
        """測試開始前的設定"""
        cls.engine = RecommendationEngine()
    
    def test_random_recommendation(self):
        """測試隨機推薦"""
        recommendations = self.engine.random_recommendation(5)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)
        self.assertGreater(len(recommendations), 0)
    
    def test_filter_based_recommendation(self):
        """測試條件篩選推薦"""
        # 測試料理類型篩選
        recommendations = self.engine.filter_based_recommendation(
            cuisine_type='日式',
            count=3
        )
        self.assertIsInstance(recommendations, list)
        
        # 如果有結果，檢查料理類型
        for meal in recommendations:
            self.assertEqual(meal.get('cuisine_type'), '日式')
    
    def test_budget_friendly_recommendation(self):
        """測試經濟實惠推薦"""
        recommendations = self.engine.budget_friendly_recommendation(5)
        self.assertIsInstance(recommendations, list)
        
        # 檢查價格範圍
        for meal in recommendations:
            self.assertEqual(meal.get('price_range'), '低')
    
    def test_luxury_recommendation(self):
        """測試高級餐點推薦"""
        recommendations = self.engine.luxury_recommendation(5)
        self.assertIsInstance(recommendations, list)
        
        # 檢查價格範圍
        for meal in recommendations:
            self.assertEqual(meal.get('price_range'), '高')
    
    def test_vegetarian_recommendation(self):
        """測試素食推薦"""
        recommendations = self.engine.vegetarian_recommendation(5)
        self.assertIsInstance(recommendations, list)
        
        # 檢查是否為素食
        for meal in recommendations:
            self.assertTrue(meal.get('is_vegetarian'))
    
    def test_mild_flavor_recommendation(self):
        """測試清淡口味推薦"""
        recommendations = self.engine.mild_flavor_recommendation(5)
        self.assertIsInstance(recommendations, list)
        
        # 檢查是否不辣
        for meal in recommendations:
            self.assertFalse(meal.get('is_spicy'))
    
    def test_popular_recommendation(self):
        """測試熱門推薦"""
        recommendations = self.engine.popular_recommendation(5)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)
    
    def test_format_meal_info(self):
        """測試餐點資訊格式化"""
        meal = {
            'name': '測試餐點',
            'restaurant_name': '測試餐廳',
            'price': 100,
            'is_vegetarian': True,
            'is_spicy': False
        }
        
        formatted = self.engine.format_meal_info(meal)
        self.assertIsInstance(formatted, str)
        self.assertIn('測試餐點', formatted)
        self.assertIn('測試餐廳', formatted)
        self.assertIn('素食', formatted)
    
    def test_user_preference_recommendation(self):
        """測試使用者偏好推薦"""
        # 假設使用者1存在且有偏好設定
        recommendations = self.engine.user_preference_recommendation(1, 3)
        self.assertIsInstance(recommendations, list)
        # 即使沒有完全符合的，也應該返回一些推薦
        self.assertGreater(len(recommendations), 0)
    
    def test_new_experience_recommendation(self):
        """測試新體驗推薦"""
        # 假設使用者1存在
        recommendations = self.engine.new_experience_recommendation(1, 5)
        self.assertIsInstance(recommendations, list)
    
    def test_mixed_recommendation(self):
        """測試混合推薦策略"""
        # 假設使用者1存在
        recommendations = self.engine.mixed_recommendation(1, 5)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)


class TestIntegration(unittest.TestCase):
    """整合測試"""
    
    def setUp(self):
        """每個測試前的設定"""
        self.db = DatabaseManager()
        self.db.connect()
        self.engine = RecommendationEngine()
    
    def tearDown(self):
        """每個測試後的清理"""
        self.db.disconnect()
    
    def test_recommendation_flow(self):
        """測試完整的推薦流程"""
        # 1. 取得隨機推薦
        recommendations = self.engine.random_recommendation(3)
        self.assertGreater(len(recommendations), 0)
        
        # 2. 選擇第一個推薦
        if recommendations:
            selected_meal = recommendations[0]
            meal_id = selected_meal['id']
            
            # 3. 取得詳細資訊
            meal_detail = self.db.get_meal_by_id(meal_id)
            self.assertIsNotNone(meal_detail)
            self.assertEqual(meal_detail['id'], meal_id)
            
            # 4. 檢查餐廳資訊
            restaurant_id = meal_detail['restaurant_id']
            restaurant = self.db.get_restaurant_by_id(restaurant_id)
            self.assertIsNotNone(restaurant)
    
    def test_user_interaction_flow(self):
        """測試使用者互動流程"""
        # 假設使用者ID為1
        user_id = 1
        
        # 1. 檢查使用者是否存在
        user = self.db.get_user_by_username('testuser1')
        if not user:
            self.skipTest("測試使用者不存在，跳過此測試")
        
        # 2. 取得使用者偏好
        preferences = self.db.get_user_preferences(user_id)
        
        # 3. 根據偏好推薦
        if preferences:
            recommendations = self.engine.user_preference_recommendation(user_id, 5)
            self.assertIsInstance(recommendations, list)
        
        # 4. 取得推薦歷史
        history = self.db.get_user_recommendation_history(user_id, 10)
        self.assertIsInstance(history, list)
        
        # 5. 取得收藏列表
        favorites = self.db.get_user_favorites(user_id)
        self.assertIsInstance(favorites, list)


# 執行測試
if __name__ == '__main__':
    # 設定測試輸出格式
    unittest.main(verbosity=2)
