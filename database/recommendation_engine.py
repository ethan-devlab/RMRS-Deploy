"""
隨機餐點推薦系統 - 餐點推薦引擎
提供各種餐點推薦策略
"""

import random
from db_manager import DatabaseManager


class RecommendationEngine:
    """餐點推薦引擎"""
    
    def __init__(self):
        """初始化推薦引擎"""
        self.db = DatabaseManager()
        self.db.connect()
    
    def __del__(self):
        """清理資源"""
        if self.db:
            self.db.disconnect()
    
    # ==================== 基礎推薦策略 ====================
    
    def random_recommendation(self, count=1):
        """
        完全隨機推薦
        
        Args:
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_random_meal(count)
    
    def filter_based_recommendation(self, cuisine_type=None, price_range=None,
                                   is_vegetarian=None, avoid_spicy=False, count=5,
                                   city=None, district=None):
        """
        基於條件篩選的推薦
        
        Args:
            cuisine_type: 料理類型
            price_range: 價格範圍
            is_vegetarian: 是否素食
            avoid_spicy: 是否避免辣食
            count: 推薦數量
            city: 指定城市
            district: 指定行政區
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_random_meal_by_filters(
            cuisine_type=cuisine_type,
            price_range=price_range,
            is_vegetarian=is_vegetarian,
            avoid_spicy=avoid_spicy,
            limit=count,
            city=city,
            district=district
        )
    
    # ==================== 個人化推薦策略 ====================
    
    def user_preference_recommendation(self, user_id, count=5):
        """
        根據使用者偏好推薦
        
        Args:
            user_id: 使用者ID
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        recommendations = self.db.get_recommendation_by_user_preference(user_id, count)
        
        # 如果根據偏好找不到足夠的餐點，補充隨機推薦
        if len(recommendations) < count:
            additional = self.db.get_random_meal(count - len(recommendations))
            recommendations.extend(additional)
        
        return recommendations
    
    def new_experience_recommendation(self, user_id, count=5):
        """
        推薦使用者未嘗試過的餐點
        
        Args:
            user_id: 使用者ID
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_new_recommendations(user_id, count)
    
    def mixed_recommendation(self, user_id, count=5):
        """
        混合推薦策略：結合偏好推薦和新體驗推薦
        
        Args:
            user_id: 使用者ID
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        # 70% 根據偏好推薦
        preference_count = int(count * 0.7)
        # 30% 推薦新體驗
        new_count = count - preference_count
        
        recommendations = []
        
        # 取得偏好推薦
        preference_meals = self.db.get_recommendation_by_user_preference(
            user_id, preference_count
        )
        recommendations.extend(preference_meals)
        
        # 取得新體驗推薦
        new_meals = self.db.get_new_recommendations(user_id, new_count)
        recommendations.extend(new_meals)
        
        # 隨機打亂順序
        random.shuffle(recommendations)
        
        return recommendations[:count]
    
    # ==================== 情境推薦策略 ====================
    
    def budget_friendly_recommendation(self, count=5):
        """
        經濟實惠推薦
        
        Args:
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_random_meal_by_filters(
            price_range='低',
            limit=count
        )
    
    def luxury_recommendation(self, count=5):
        """
        高級餐點推薦
        
        Args:
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_random_meal_by_filters(
            price_range='高',
            limit=count
        )
    
    def vegetarian_recommendation(self, count=5):
        """
        素食推薦
        
        Args:
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_random_meal_by_filters(
            is_vegetarian=True,
            limit=count
        )
    
    def mild_flavor_recommendation(self, count=5):
        """
        清淡口味推薦（不辣）
        
        Args:
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_random_meal_by_filters(
            avoid_spicy=True,
            limit=count
        )
    
    def nearby_recommendation(self, latitude, longitude, radius_km=2, count=5):
        """
        依GPS座標取得鄰近推薦
        
        Args:
            latitude: 緯度
            longitude: 經度
            radius_km: 搜尋半徑（公里）
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_nearby_meals(latitude, longitude, radius_km, count)
    
    def cuisine_type_recommendation(self, cuisine_type, count=5):
        """
        特定料理類型推薦
        
        Args:
            cuisine_type: 料理類型
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_random_meal_by_filters(
            cuisine_type=cuisine_type,
            limit=count
        )
    
    # ==================== 熱門推薦 ====================
    
    def popular_recommendation(self, count=5):
        """
        熱門餐點推薦（根據收藏數）
        
        Args:
            count: 推薦數量
            
        Returns:
            list: 推薦的餐點列表
        """
        return self.db.get_popular_meals(count)
    
    # ==================== 互動式推薦 ====================
    
    def interactive_recommendation(self):
        """
        互動式推薦：讓使用者選擇偏好條件
        
        Returns:
            list: 推薦的餐點列表
        """
        print("\n=== 互動式餐點推薦 ===")
        
        # 詢問料理類型
        print("\n請選擇料理類型（留空表示不限）：")
        cuisine_types = ['台式', '日式', '義式', '川菜', '素食', '美式', '韓式', '粵菜', '泰式', '法式']
        for i, cuisine in enumerate(cuisine_types, 1):
            print(f"{i}. {cuisine}")
        
        cuisine_choice = input("\n請輸入編號或留空：").strip()
        cuisine_type = cuisine_types[int(cuisine_choice) - 1] if cuisine_choice.isdigit() and 1 <= int(cuisine_choice) <= len(cuisine_types) else None
        
        # 詢問價格範圍
        print("\n請選擇價格範圍（留空表示不限）：")
        print("1. 低")
        print("2. 中")
        print("3. 高")
        
        price_choice = input("\n請輸入編號或留空：").strip()
        price_map = {'1': '低', '2': '中', '3': '高'}
        price_range = price_map.get(price_choice)
        
        # 詢問素食偏好
        vegetarian_choice = input("\n只要素食嗎？(y/n，留空表示不限)：").strip().lower()
        is_vegetarian = True if vegetarian_choice == 'y' else None
        
        # 詢問辣度偏好
        spicy_choice = input("\n要避免辣食嗎？(y/n，留空表示不限)：").strip().lower()
        avoid_spicy = True if spicy_choice == 'y' else False
        
        # 推薦數量
        count_choice = input("\n要推薦幾個餐點？(預設5個)：").strip()
        count = int(count_choice) if count_choice.isdigit() else 5
        
        # 執行推薦
        return self.filter_based_recommendation(
            cuisine_type=cuisine_type,
            price_range=price_range,
            is_vegetarian=is_vegetarian,
            avoid_spicy=avoid_spicy,
            count=count
        )
    
    # ==================== 推薦記錄 ====================
    
    def record_recommendation(self, user_id, meal_id, restaurant_id, was_selected=False):
        """
        記錄推薦結果
        
        Args:
            user_id: 使用者ID
            meal_id: 餐點ID
            restaurant_id: 餐廳ID
            was_selected: 是否被選擇
        """
        return self.db.add_recommendation_history(user_id, meal_id, restaurant_id, was_selected)
    
    # ==================== 輔助方法 ====================
    
    def format_meal_info(self, meal):
        """
        格式化餐點資訊顯示
        
        Args:
            meal: 餐點資料
            
        Returns:
            str: 格式化的餐點資訊
        """
        info = f"\n{'='*50}\n"
        info += f"餐點名稱：{meal['name']}\n"
        info += f"餐廳：{meal['restaurant_name']}\n"
        
        if 'address' in meal and meal['address']:
            info += f"地址：{meal['address']}\n"
        
        location_parts = []
        if meal.get('city'):
            location_parts.append(meal['city'])
        if meal.get('district'):
            location_parts.append(meal['district'])
        if location_parts:
            info += f"地區：{' '.join(location_parts)}\n"
        
        if 'cuisine_type' in meal and meal['cuisine_type']:
            info += f"料理類型：{meal['cuisine_type']}\n"
        
        if 'price' in meal and meal['price']:
            info += f"價格：${meal['price']}\n"
        
        if 'category' in meal and meal['category']:
            info += f"類別：{meal['category']}\n"
        
        if 'description' in meal and meal['description']:
            info += f"描述：{meal['description']}\n"
        
        if meal.get('distance_km') is not None:
            info += f"距離：約 {meal['distance_km']:.2f} 公里\n"
        
        # 標記
        tags = []
        if meal.get('is_vegetarian'):
            tags.append('素食')
        if meal.get('is_spicy'):
            tags.append('辣')
        
        if tags:
            info += f"標記：{', '.join(tags)}\n"
        
        info += f"{'='*50}\n"
        
        return info


# 使用範例
if __name__ == "__main__":
    # 建立推薦引擎
    engine = RecommendationEngine()
    
    # 測試各種推薦策略
    print("\n【1. 隨機推薦】")
    random_meals = engine.random_recommendation(3)
    for meal in random_meals:
        print(engine.format_meal_info(meal))
    
    print("\n【2. 經濟實惠推薦】")
    budget_meals = engine.budget_friendly_recommendation(3)
    for meal in budget_meals:
        print(engine.format_meal_info(meal))
    
    print("\n【3. 素食推薦】")
    vegetarian_meals = engine.vegetarian_recommendation(3)
    for meal in vegetarian_meals:
        print(engine.format_meal_info(meal))
    
    print("\n【4. 熱門推薦】")
    popular_meals = engine.popular_recommendation(3)
    for meal in popular_meals:
        print(engine.format_meal_info(meal))
    
    # 互動式推薦（可選）
    # interactive_choice = input("\n要使用互動式推薦嗎？(y/n)：").strip().lower()
    # if interactive_choice == 'y':
    #     interactive_meals = engine.interactive_recommendation()
    #     print("\n【互動式推薦結果】")
    #     for meal in interactive_meals:
    #         print(engine.format_meal_info(meal))
