import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class DatabaseManager:
    """資料庫管理類別，處理所有資料庫連線和操作"""
    
    def __init__(self):
        """初始化資料庫連線設定"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'meal_recommendation')
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """建立資料庫連線"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print(f"成功連線到資料庫 {self.database}")
                return True
        except Error as e:
            print(f"資料庫連線錯誤: {e}")
            return False
    
    def disconnect(self):
        """關閉資料庫連線"""
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            print("資料庫連線已關閉")
    
    def execute_query(self, query, params=None):
        """執行查詢語句（SELECT）"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"查詢執行錯誤: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """執行更新語句（INSERT, UPDATE, DELETE）"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"更新執行錯誤: {e}")
            self.connection.rollback()
            return None
    
    # ==================== 餐廳相關操作 ====================
    
    def get_all_restaurants(self, is_active=True):
        """取得所有餐廳"""
        query = "SELECT * FROM restaurants WHERE is_active = %s ORDER BY rating DESC"
        return self.execute_query(query, (is_active,))
    
    def get_restaurant_by_id(self, restaurant_id):
        """根據ID取得餐廳資訊"""
        query = "SELECT * FROM restaurants WHERE id = %s"
        result = self.execute_query(query, (restaurant_id,))
        return result[0] if result else None
    
    def get_restaurants_by_cuisine(self, cuisine_type):
        """根據料理類型取得餐廳"""
        query = """
            SELECT * FROM restaurants 
            WHERE cuisine_type = %s AND is_active = TRUE 
            ORDER BY rating DESC
        """
        return self.execute_query(query, (cuisine_type,))
    
    def add_restaurant(self, name, address, phone, cuisine_type, price_range,
                      city=None, district=None, latitude=None, longitude=None):
        """新增餐廳"""
        query = """
            INSERT INTO restaurants 
            (name, address, city, district, phone, cuisine_type, price_range, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_update(query, (
            name, address, city, district, phone, cuisine_type, price_range, latitude, longitude
        ))

    def get_restaurants_by_city(self, city, district=None, is_active=True):
        """根據城市/行政區取得餐廳"""
        query = """
            SELECT * FROM restaurants
            WHERE city = %s AND is_active = %s
        """
        params = [city, is_active]
        
        if district:
            query += " AND district = %s"
            params.append(district)
        
        query += " ORDER BY rating DESC"
        return self.execute_query(query, tuple(params))
    
    def get_nearby_restaurants(self, latitude, longitude, radius_km=3, limit=10):
        """根據GPS座標取得鄰近餐廳"""
        query = """
            SELECT r.*,
                   (
                       6371 * ACOS(
                           LEAST(
                               1,
                               GREATEST(-1,
                                   COS(RADIANS(%s)) * COS(RADIANS(r.latitude)) *
                                   COS(RADIANS(r.longitude) - RADIANS(%s)) +
                                   SIN(RADIANS(%s)) * SIN(RADIANS(r.latitude))
                               )
                           )
                       )
                   ) AS distance_km
            FROM restaurants r
            WHERE r.is_active = TRUE
              AND r.latitude IS NOT NULL
              AND r.longitude IS NOT NULL
            HAVING distance_km <= %s
            ORDER BY distance_km ASC, r.rating DESC
            LIMIT %s
        """
        params = (latitude, longitude, latitude, radius_km, limit)
        return self.execute_query(query, params)
    
    def get_nearby_meals(self, latitude, longitude, radius_km=3, limit=10):
        """根據GPS座標取得鄰近餐點"""
        query = """
            SELECT m.*, r.name AS restaurant_name, r.address, r.city, r.district,
                   r.phone, r.cuisine_type, r.price_range,
                   (
                       6371 * ACOS(
                           LEAST(
                               1,
                               GREATEST(-1,
                                   COS(RADIANS(%s)) * COS(RADIANS(r.latitude)) *
                                   COS(RADIANS(r.longitude) - RADIANS(%s)) +
                                   SIN(RADIANS(%s)) * SIN(RADIANS(r.latitude))
                               )
                           )
                       )
                   ) AS distance_km
            FROM meals m
            JOIN restaurants r ON m.restaurant_id = r.id
            WHERE m.is_available = TRUE
              AND r.is_active = TRUE
              AND r.latitude IS NOT NULL
              AND r.longitude IS NOT NULL
            HAVING distance_km <= %s
            ORDER BY distance_km ASC, r.rating DESC
            LIMIT %s
        """
        params = (latitude, longitude, latitude, radius_km, limit)
        return self.execute_query(query, params)
    
    # ==================== 餐點相關操作 ====================
    
    def get_all_meals(self, is_available=True):
        """取得所有餐點"""
        query = """
            SELECT m.*, r.name AS restaurant_name, r.address, r.phone
            FROM meals m
            JOIN restaurants r ON m.restaurant_id = r.id
            WHERE m.is_available = %s AND r.is_active = TRUE
        """
        return self.execute_query(query, (is_available,))
    
    def get_meal_by_id(self, meal_id):
        """根據ID取得餐點資訊"""
        query = """
            SELECT m.*, r.name AS restaurant_name, r.address, r.phone, r.cuisine_type
            FROM meals m
            JOIN restaurants r ON m.restaurant_id = r.id
            WHERE m.id = %s
        """
        result = self.execute_query(query, (meal_id,))
        return result[0] if result else None
    
    def get_meals_by_restaurant(self, restaurant_id, is_available=True):
        """取得某餐廳的所有餐點"""
        query = """
            SELECT * FROM meals 
            WHERE restaurant_id = %s AND is_available = %s
        """
        return self.execute_query(query, (restaurant_id, is_available))
    
    def add_meal(self, restaurant_id, name, description, price, category, 
                 is_vegetarian=False, is_spicy=False):
        """新增餐點"""
        query = """
            INSERT INTO meals 
            (restaurant_id, name, description, price, category, is_vegetarian, is_spicy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_update(query, (restaurant_id, name, description, price, 
                                          category, is_vegetarian, is_spicy))
    
    # ==================== 推薦系統操作 ====================
    
    def get_random_meal(self, limit=1):
        """隨機取得餐點"""
        query = """
            SELECT m.*, r.name AS restaurant_name, r.address, r.phone, r.cuisine_type
            FROM meals m
            JOIN restaurants r ON m.restaurant_id = r.id
            WHERE m.is_available = TRUE AND r.is_active = TRUE
            ORDER BY RAND()
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def get_random_meal_by_filters(self, cuisine_type=None, price_range=None, 
                                   is_vegetarian=None, avoid_spicy=False, limit=5,
                                   city=None, district=None):
        """根據條件隨機取得餐點"""
        query = """
            SELECT m.*, r.name AS restaurant_name, r.address, r.phone, r.cuisine_type, r.price_range
            FROM meals m
            JOIN restaurants r ON m.restaurant_id = r.id
            WHERE m.is_available = TRUE AND r.is_active = TRUE
        """
        params = []
        
        if cuisine_type:
            query += " AND r.cuisine_type = %s"
            params.append(cuisine_type)
        
        if price_range:
            query += " AND r.price_range = %s"
            params.append(price_range)
        
        if city:
            query += " AND r.city = %s"
            params.append(city)
        
        if district:
            query += " AND r.district = %s"
            params.append(district)
        
        if is_vegetarian:
            query += " AND m.is_vegetarian = TRUE"
        
        if avoid_spicy:
            query += " AND m.is_spicy = FALSE"
        
        query += " ORDER BY RAND() LIMIT %s"
        params.append(limit)
        
        return self.execute_query(query, tuple(params))
    
    def get_recommendation_by_user_preference(self, user_id, limit=5):
        """根據使用者偏好推薦餐點"""
        query = """
            SELECT m.*, r.name AS restaurant_name, r.address, r.cuisine_type
            FROM meals m
            JOIN restaurants r ON m.restaurant_id = r.id
            JOIN user_preferences up ON up.user_id = %s
            WHERE m.is_available = TRUE 
              AND r.is_active = TRUE
              AND (up.is_vegetarian = FALSE OR m.is_vegetarian = TRUE)
              AND (up.avoid_spicy = FALSE OR m.is_spicy = FALSE)
              AND r.cuisine_type = up.cuisine_type
              AND r.price_range = up.price_range
            ORDER BY RAND()
            LIMIT %s
        """
        return self.execute_query(query, (user_id, limit))
    
    def get_new_recommendations(self, user_id, limit=5):
        """推薦使用者未嘗試過的餐點"""
        query = """
            SELECT m.*, r.name AS restaurant_name, r.address
            FROM meals m
            JOIN restaurants r ON m.restaurant_id = r.id
            WHERE m.is_available = TRUE 
              AND r.is_active = TRUE
              AND m.id NOT IN (
                SELECT meal_id 
                FROM recommendation_history 
                WHERE user_id = %s AND was_selected = TRUE
              )
            ORDER BY RAND()
            LIMIT %s
        """
        return self.execute_query(query, (user_id, limit))
    
    # ==================== 使用者相關操作 ====================
    
    def add_user(self, username, email, password_hash, full_name=None):
        """新增使用者"""
        query = """
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_update(query, (username, email, password_hash, full_name))
    
    def get_user_by_username(self, username):
        """根據使用者名稱取得使用者資訊"""
        query = "SELECT * FROM users WHERE username = %s"
        result = self.execute_query(query, (username,))
        return result[0] if result else None
    
    def get_user_preferences(self, user_id):
        """取得使用者偏好設定"""
        query = "SELECT * FROM user_preferences WHERE user_id = %s"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def set_user_preferences(self, user_id, cuisine_type, price_range, 
                           is_vegetarian=False, avoid_spicy=False):
        """設定使用者偏好"""
        query = """
            INSERT INTO user_preferences 
            (user_id, cuisine_type, price_range, is_vegetarian, avoid_spicy)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            cuisine_type = VALUES(cuisine_type),
            price_range = VALUES(price_range),
            is_vegetarian = VALUES(is_vegetarian),
            avoid_spicy = VALUES(avoid_spicy)
        """
        return self.execute_update(query, (user_id, cuisine_type, price_range, 
                                          is_vegetarian, avoid_spicy))
    
    # ==================== 推薦歷史操作 ====================
    
    def add_recommendation_history(self, user_id, meal_id, restaurant_id, was_selected=False):
        """記錄推薦歷史"""
        query = """
            INSERT INTO recommendation_history 
            (user_id, meal_id, restaurant_id, was_selected)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_update(query, (user_id, meal_id, restaurant_id, was_selected))
    
    def get_user_recommendation_history(self, user_id, limit=20):
        """取得使用者推薦歷史"""
        query = """
            SELECT rh.*, m.name AS meal_name, r.name AS restaurant_name
            FROM recommendation_history rh
            JOIN meals m ON rh.meal_id = m.id
            JOIN restaurants r ON rh.restaurant_id = r.id
            WHERE rh.user_id = %s
            ORDER BY rh.recommended_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (user_id, limit))
    
    # ==================== 收藏功能 ====================
    
    def add_favorite(self, user_id, meal_id):
        """新增收藏"""
        query = "INSERT INTO favorites (user_id, meal_id) VALUES (%s, %s)"
        return self.execute_update(query, (user_id, meal_id))
    
    def remove_favorite(self, user_id, meal_id):
        """移除收藏"""
        query = "DELETE FROM favorites WHERE user_id = %s AND meal_id = %s"
        return self.execute_update(query, (user_id, meal_id))
    
    def get_user_favorites(self, user_id):
        """取得使用者收藏"""
        query = """
            SELECT m.*, r.name AS restaurant_name, r.address
            FROM favorites f
            JOIN meals m ON f.meal_id = m.id
            JOIN restaurants r ON m.restaurant_id = r.id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
        """
        return self.execute_query(query, (user_id,))
    
    def is_favorite(self, user_id, meal_id):
        """檢查是否已收藏"""
        query = "SELECT COUNT(*) as count FROM favorites WHERE user_id = %s AND meal_id = %s"
        result = self.execute_query(query, (user_id, meal_id))
        return result[0]['count'] > 0 if result else False
    
    # ==================== 評價功能 ====================
    
    def add_review(self, user_id, meal_id, restaurant_id, rating, comment=None):
        """新增評價"""
        query = """
            INSERT INTO reviews (user_id, meal_id, restaurant_id, rating, comment)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_update(query, (user_id, meal_id, restaurant_id, rating, comment))
    
    def get_meal_reviews(self, meal_id):
        """取得餐點評價"""
        query = """
            SELECT r.*, u.username, u.full_name
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.meal_id = %s
            ORDER BY r.created_at DESC
        """
        return self.execute_query(query, (meal_id,))
    
    def get_average_rating(self, meal_id):
        """取得餐點平均評分"""
        query = """
            SELECT AVG(rating) as avg_rating, COUNT(*) as review_count
            FROM reviews
            WHERE meal_id = %s
        """
        result = self.execute_query(query, (meal_id,))
        return result[0] if result else {'avg_rating': 0, 'review_count': 0}
    
    # ==================== 統計功能 ====================
    
    def get_popular_meals(self, limit=10):
        """取得熱門餐點（根據收藏數）"""
        query = """
            SELECT m.*, r.name AS restaurant_name, COUNT(f.id) as favorite_count
            FROM meals m
            JOIN restaurants r ON m.restaurant_id = r.id
            LEFT JOIN favorites f ON m.id = f.meal_id
            WHERE m.is_available = TRUE AND r.is_active = TRUE
            GROUP BY m.id
            ORDER BY favorite_count DESC, r.rating DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def get_cuisine_statistics(self):
        """取得料理類型統計"""
        query = """
            SELECT cuisine_type, COUNT(*) as count
            FROM restaurants
            WHERE is_active = TRUE
            GROUP BY cuisine_type
            ORDER BY count DESC
        """
        return self.execute_query(query)


# 使用範例
if __name__ == "__main__":
    # 建立資料庫管理器實例
    db = DatabaseManager()
    
    # 連線到資料庫
    if db.connect():
        # 測試：隨機取得一個餐點
        print("\n=== 隨機推薦 ===")
        random_meals = db.get_random_meal(3)
        for meal in random_meals:
            print(f"餐點：{meal['name']} | 餐廳：{meal['restaurant_name']} | 價格：${meal['price']}")
        
        # 測試：取得所有餐廳
        print("\n=== 所有餐廳 ===")
        restaurants = db.get_all_restaurants()
        for restaurant in restaurants[:5]:  # 只顯示前5個
            print(f"{restaurant['name']} - {restaurant['cuisine_type']} - 評分：{restaurant['rating']}")
        
        # 測試：根據料理類型篩選
        print("\n=== 日式餐點 ===")
        japanese_meals = db.get_random_meal_by_filters(cuisine_type='日式', limit=3)
        for meal in japanese_meals:
            print(f"餐點：{meal['name']} | 餐廳：{meal['restaurant_name']}")
        
        # 測試：取得熱門餐點
        print("\n=== 熱門餐點 ===")
        popular_meals = db.get_popular_meals(5)
        for meal in popular_meals:
            print(f"餐點：{meal['name']} | 收藏數：{meal['favorite_count']}")
        
        # 關閉連線
        db.disconnect()
