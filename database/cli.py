"""
隨機餐點推薦系統 - 命令列介面
提供簡單的CLI來測試和使用推薦系統
"""

import sys
from recommendation_engine import RecommendationEngine
from db_manager import DatabaseManager


class MealRecommendationCLI:
    """餐點推薦系統命令列介面"""
    
    def __init__(self):
        """初始化CLI"""
        self.engine = RecommendationEngine()
        self.db = DatabaseManager()
        self.db.connect()
        self.current_user_id = None
    
    def __del__(self):
        """清理資源"""
        if self.db:
            self.db.disconnect()
    
    def display_menu(self):
        """顯示主選單"""
        print("\n" + "="*60)
        print("         隨機餐點推薦系統")
        print("="*60)
        print("\n【主選單】")
        print("1. 隨機推薦餐點")
        print("2. 條件篩選推薦")
        print("3. 經濟實惠推薦")
        print("4. 高級餐點推薦")
        print("5. 素食推薦")
        print("6. 清淡口味推薦（不辣）")
        print("7. 熱門餐點推薦")
        print("8. 特定料理類型推薦")
        print("9. 瀏覽所有餐廳")
        print("10. 互動式推薦")
        print("11. 鄰近餐點推薦（輸入GPS）")
        print("0. 離開系統")
        print("="*60)
    
    def display_meals(self, meals, title="推薦結果"):
        """顯示餐點列表"""
        if not meals:
            print("\n抱歉，找不到符合條件的餐點。")
            return
        
        print(f"\n{'='*60}")
        print(f"  {title} (共 {len(meals)} 個)")
        print("="*60)
        
        for i, meal in enumerate(meals, 1):
            print(f"\n【選項 {i}】")
            print(f"餐點名稱：{meal['name']}")
            print(f"餐廳：{meal['restaurant_name']}")
            
            if 'address' in meal and meal['address']:
                print(f"地址：{meal['address']}")
            
            location_parts = []
            if meal.get('city'):
                location_parts.append(meal['city'])
            if meal.get('district'):
                location_parts.append(meal['district'])
            if location_parts:
                print(f"地區：{' '.join(location_parts)}")
            
            if 'phone' in meal and meal['phone']:
                print(f"電話：{meal['phone']}")
            
            if 'cuisine_type' in meal and meal['cuisine_type']:
                print(f"料理類型：{meal['cuisine_type']}")
            
            if 'price' in meal and meal['price']:
                print(f"價格：${meal['price']}")
            
            if 'category' in meal and meal['category']:
                print(f"類別：{meal['category']}")
            
            if 'description' in meal and meal['description']:
                print(f"描述：{meal['description']}")
            
            if meal.get('distance_km') is not None:
                print(f"距離：約 {meal['distance_km']:.2f} 公里")
            
            # 標記
            tags = []
            if meal.get('is_vegetarian'):
                tags.append('🥬 素食')
            if meal.get('is_spicy'):
                tags.append('🌶️ 辣')
            
            if tags:
                print(f"標記：{' '.join(tags)}")
            
            print("-" * 60)
    
    def random_recommendation(self):
        """隨機推薦"""
        count = input("\n要推薦幾個餐點？(預設3個)：").strip()
        count = int(count) if count.isdigit() and int(count) > 0 else 3
        
        meals = self.engine.random_recommendation(count)
        self.display_meals(meals, "隨機推薦")
    
    def filter_recommendation(self):
        """條件篩選推薦"""
        print("\n=== 條件篩選推薦 ===")
        
        # 料理類型
        print("\n料理類型選項：")
        cuisine_types = ['台式', '日式', '義式', '川菜', '素食', '美式', '韓式', '粵菜', '泰式', '法式']
        for i, cuisine in enumerate(cuisine_types, 1):
            print(f"{i}. {cuisine}", end="  ")
            if i % 5 == 0:
                print()
        
        cuisine_choice = input("\n\n請選擇料理類型（輸入編號，留空表示不限）：").strip()
        cuisine_type = None
        if cuisine_choice.isdigit() and 1 <= int(cuisine_choice) <= len(cuisine_types):
            cuisine_type = cuisine_types[int(cuisine_choice) - 1]
        
        # 價格範圍
        print("\n價格範圍：1. 低  2. 中  3. 高")
        price_choice = input("請選擇價格範圍（留空表示不限）：").strip()
        price_map = {'1': '低', '2': '中', '3': '高'}
        price_range = price_map.get(price_choice)
        
        # 城市/行政區
        city = input("\n想限定城市嗎？(例如：台中市，留空表示不限)：").strip()
        city = city if city else None
        district = None
        if city:
            district_choice = input("想限定行政區嗎？(例如：西屯區，留空表示不限)：").strip()
            district = district_choice if district_choice else None
        
        # 素食
        vegetarian_choice = input("\n只要素食嗎？(y/n，留空表示不限)：").strip().lower()
        is_vegetarian = True if vegetarian_choice == 'y' else None
        
        # 辣度
        spicy_choice = input("要避免辣食嗎？(y/n，留空表示不限)：").strip().lower()
        avoid_spicy = True if spicy_choice == 'y' else False
        
        # 數量
        count = input("\n要推薦幾個餐點？(預設5個)：").strip()
        count = int(count) if count.isdigit() and int(count) > 0 else 5
        
        meals = self.engine.filter_based_recommendation(
            cuisine_type=cuisine_type,
            price_range=price_range,
            is_vegetarian=is_vegetarian,
            avoid_spicy=avoid_spicy,
            count=count,
            city=city,
            district=district
        )
        
        self.display_meals(meals, "篩選推薦結果")
    
    def budget_recommendation(self):
        """經濟實惠推薦"""
        count = input("\n要推薦幾個餐點？(預設5個)：").strip()
        count = int(count) if count.isdigit() and int(count) > 0 else 5
        
        meals = self.engine.budget_friendly_recommendation(count)
        self.display_meals(meals, "經濟實惠推薦")
    
    def luxury_recommendation(self):
        """高級餐點推薦"""
        count = input("\n要推薦幾個餐點？(預設5個)：").strip()
        count = int(count) if count.isdigit() and int(count) > 0 else 5
        
        meals = self.engine.luxury_recommendation(count)
        self.display_meals(meals, "高級餐點推薦")
    
    def vegetarian_recommendation(self):
        """素食推薦"""
        count = input("\n要推薦幾個餐點？(預設5個)：").strip()
        count = int(count) if count.isdigit() and int(count) > 0 else 5
        
        meals = self.engine.vegetarian_recommendation(count)
        self.display_meals(meals, "素食推薦")
    
    def mild_recommendation(self):
        """清淡口味推薦"""
        count = input("\n要推薦幾個餐點？(預設5個)：").strip()
        count = int(count) if count.isdigit() and int(count) > 0 else 5
        
        meals = self.engine.mild_flavor_recommendation(count)
        self.display_meals(meals, "清淡口味推薦")
    
    def popular_recommendation(self):
        """熱門推薦"""
        count = input("\n要推薦幾個餐點？(預設5個)：").strip()
        count = int(count) if count.isdigit() and int(count) > 0 else 5
        
        meals = self.engine.popular_recommendation(count)
        self.display_meals(meals, "熱門餐點推薦")
    
    def cuisine_type_recommendation(self):
        """特定料理類型推薦"""
        print("\n=== 料理類型推薦 ===")
        cuisine_types = ['台式', '日式', '義式', '川菜', '素食', '美式', '韓式', '粵菜', '泰式', '法式']
        
        for i, cuisine in enumerate(cuisine_types, 1):
            print(f"{i}. {cuisine}", end="  ")
            if i % 5 == 0:
                print()
        
        choice = input("\n\n請選擇料理類型：").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(cuisine_types)):
            print("無效的選擇！")
            return
        
        cuisine_type = cuisine_types[int(choice) - 1]
        
        count = input(f"\n要推薦幾個{cuisine_type}餐點？(預設5個)：").strip()
        count = int(count) if count.isdigit() and int(count) > 0 else 5
        
        meals = self.engine.cuisine_type_recommendation(cuisine_type, count)
        self.display_meals(meals, f"{cuisine_type}料理推薦")
    
    def browse_restaurants(self):
        """瀏覽所有餐廳"""
        print("\n=== 瀏覽餐廳 ===")
        restaurants = self.db.get_all_restaurants()
        
        if not restaurants:
            print("沒有餐廳資料。")
            return
        
        print(f"\n共有 {len(restaurants)} 家餐廳：\n")
        
        for i, r in enumerate(restaurants, 1):
            print(f"{i}. {r['name']}")
            print(f"   料理類型：{r['cuisine_type']} | 價格：{r['price_range']} | 評分：{r['rating']}")
            if r['address']:
                print(f"   地址：{r['address']}")
            print()
        
        # 選擇餐廳查看詳情
        choice = input("輸入餐廳編號查看詳情（留空返回主選單）：").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(restaurants):
            self.show_restaurant_details(restaurants[int(choice) - 1]['id'])
    
    def show_restaurant_details(self, restaurant_id):
        """顯示餐廳詳情"""
        restaurant = self.db.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            print("找不到餐廳資料。")
            return
        
        print(f"\n{'='*60}")
        print(f"  {restaurant['name']}")
        print("="*60)
        print(f"料理類型：{restaurant['cuisine_type']}")
        print(f"價格範圍：{restaurant['price_range']}")
        print(f"評分：{restaurant['rating']}")
        if restaurant['address']:
            print(f"地址：{restaurant['address']}")
        if restaurant['phone']:
            print(f"電話：{restaurant['phone']}")
        
        # 顯示該餐廳的餐點
        meals = self.db.get_meals_by_restaurant(restaurant_id)
        if meals:
            print(f"\n【菜單】（共 {len(meals)} 道餐點）")
            for i, meal in enumerate(meals, 1):
                tags = []
                if meal.get('is_vegetarian'):
                    tags.append('素')
                if meal.get('is_spicy'):
                    tags.append('辣')
                tag_str = f" [{', '.join(tags)}]" if tags else ""
                
                print(f"{i}. {meal['name']} - ${meal['price']}{tag_str}")
                if meal.get('description'):
                    print(f"   {meal['description']}")
    
    def interactive_recommendation(self):
        """互動式推薦"""
        meals = self.engine.interactive_recommendation()
        self.display_meals(meals, "互動式推薦結果")
    
    def nearby_recommendation(self):
        """GPS鄰近推薦"""
        print("\n=== 鄰近餐點推薦（輸入GPS座標） ===")
        
        try:
            latitude = float(input("請輸入目前緯度 (例如 24.1793)：").strip())
            longitude = float(input("請輸入目前經度 (例如 120.6467)：").strip())
        except ValueError:
            print("緯度或經度格式不正確，請重新操作。")
            return
        
        radius = input("搜尋半徑（公里，預設2km）：").strip()
        radius_km = float(radius) if radius.replace('.', '', 1).isdigit() else 2.0
        
        count_input = input("要推薦幾個餐點？(預設5個)：").strip()
        count = int(count_input) if count_input.isdigit() and int(count_input) > 0 else 5
        
        meals = self.engine.nearby_recommendation(latitude, longitude, radius_km, count)
        self.display_meals(meals, "鄰近餐點推薦")
    
    def run(self):
        """執行CLI主循環"""
        print("\n歡迎使用隨機餐點推薦系統！")
        
        while True:
            self.display_menu()
            choice = input("\n請選擇功能（輸入數字）：").strip()
            
            if choice == '0':
                print("\n感謝使用，再見！")
                break
            elif choice == '1':
                self.random_recommendation()
            elif choice == '2':
                self.filter_recommendation()
            elif choice == '3':
                self.budget_recommendation()
            elif choice == '4':
                self.luxury_recommendation()
            elif choice == '5':
                self.vegetarian_recommendation()
            elif choice == '6':
                self.mild_recommendation()
            elif choice == '7':
                self.popular_recommendation()
            elif choice == '8':
                self.cuisine_type_recommendation()
            elif choice == '9':
                self.browse_restaurants()
            elif choice == '10':
                self.interactive_recommendation()
            elif choice == '11':
                self.nearby_recommendation()
            else:
                print("\n無效的選擇，請重新輸入！")
            
            input("\n按 Enter 繼續...")


# 主程式入口
if __name__ == "__main__":
    try:
        cli = MealRecommendationCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n程式已中斷。")
        sys.exit(0)
    except Exception as e:
        print(f"\n發生錯誤：{e}")
        sys.exit(1)
