-- 隨機餐點推薦系統 - 資料庫查詢範例
-- Random Meal Recommendation System - Query Examples

USE meal_recommendation;

-- ==================== 基本查詢 ====================

-- 1. 查詢所有餐廳
SELECT * FROM restaurants WHERE is_active = TRUE;

-- 2. 查詢特定料理類型的餐廳
SELECT * FROM restaurants 
WHERE cuisine_type = '日式' AND is_active = TRUE 
ORDER BY rating DESC;

-- 3. 查詢某餐廳的所有可供應餐點
SELECT m.* FROM meals m
WHERE m.restaurant_id = 1 AND m.is_available = TRUE;

-- 4. 查詢素食餐點
SELECT m.name, r.name AS restaurant_name, m.price 
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
WHERE m.is_vegetarian = TRUE AND m.is_available = TRUE;

-- ==================== 推薦系統查詢 ====================

-- 5. 隨機推薦一個餐點（所有可用餐點）
SELECT m.*, r.name AS restaurant_name, r.address, r.phone
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
WHERE m.is_available = TRUE AND r.is_active = TRUE
ORDER BY RAND()
LIMIT 1;

-- 6. 根據價格範圍隨機推薦餐點
SELECT m.*, r.name AS restaurant_name, r.price_range
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
WHERE m.is_available = TRUE 
  AND r.is_active = TRUE 
  AND r.price_range = '低'
ORDER BY RAND()
LIMIT 5;

-- 7. 根據料理類型隨機推薦
SELECT m.*, r.name AS restaurant_name, r.cuisine_type
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
WHERE m.is_available = TRUE 
  AND r.is_active = TRUE 
  AND r.cuisine_type IN ('日式', '台式')
ORDER BY RAND()
LIMIT 5;

-- 8. 根據使用者偏好推薦（素食且非辣）
SELECT m.*, r.name AS restaurant_name
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
JOIN user_preferences up ON up.user_id = 1
WHERE m.is_available = TRUE 
  AND r.is_active = TRUE
  AND (up.is_vegetarian = FALSE OR m.is_vegetarian = TRUE)
  AND (up.avoid_spicy = FALSE OR m.is_spicy = FALSE)
ORDER BY RAND()
LIMIT 5;

-- ==================== 統計查詢 ====================

-- 9. 統計各料理類型的餐廳數量
SELECT cuisine_type, COUNT(*) as count
FROM restaurants
WHERE is_active = TRUE
GROUP BY cuisine_type
ORDER BY count DESC;

-- 10. 統計各餐廳的餐點數量
SELECT r.name, COUNT(m.id) as meal_count
FROM restaurants r
LEFT JOIN meals m ON r.id = m.restaurant_id AND m.is_available = TRUE
WHERE r.is_active = TRUE
GROUP BY r.id, r.name
ORDER BY meal_count DESC;

-- 11. 計算餐廳平均評分
SELECT r.name, 
       COUNT(rv.id) as review_count,
       AVG(rv.rating) as avg_rating
FROM restaurants r
LEFT JOIN reviews rv ON r.id = rv.restaurant_id
GROUP BY r.id, r.name
HAVING review_count > 0
ORDER BY avg_rating DESC;

-- 12. 最受歡迎的餐點（根據收藏數）
SELECT m.name, r.name AS restaurant_name, COUNT(f.id) as favorite_count
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
LEFT JOIN favorites f ON m.id = f.meal_id
GROUP BY m.id, m.name, r.name
HAVING favorite_count > 0
ORDER BY favorite_count DESC
LIMIT 10;

-- 13. 使用者推薦歷史統計
SELECT u.username, 
       COUNT(rh.id) as total_recommendations,
       SUM(CASE WHEN rh.was_selected = TRUE THEN 1 ELSE 0 END) as selected_count
FROM users u
LEFT JOIN recommendation_history rh ON u.id = rh.user_id
GROUP BY u.id, u.username;

-- ==================== 進階查詢 ====================

-- 14. 查詢帶有特定標籤的餐點
SELECT m.name, r.name AS restaurant_name, GROUP_CONCAT(t.name) as tags
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
LEFT JOIN meal_tags mt ON m.id = mt.meal_id
LEFT JOIN tags t ON mt.tag_id = t.id
WHERE t.name IN ('人氣', '推薦')
GROUP BY m.id, m.name, r.name;

-- 15. 查詢使用者尚未嘗試過的餐點（排除推薦歷史）
SELECT m.*, r.name AS restaurant_name
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
WHERE m.is_available = TRUE 
  AND r.is_active = TRUE
  AND m.id NOT IN (
    SELECT meal_id 
    FROM recommendation_history 
    WHERE user_id = 1 AND was_selected = TRUE
  )
ORDER BY RAND()
LIMIT 10;

-- 16. 查詢某個價格範圍內的最高評分餐廳
SELECT r.*, AVG(rv.rating) as avg_rating
FROM restaurants r
LEFT JOIN reviews rv ON r.id = rv.restaurant_id
WHERE r.is_active = TRUE AND r.price_range = '中'
GROUP BY r.id
ORDER BY avg_rating DESC
LIMIT 5;

-- 17. 智能推薦：根據使用者歷史喜好推薦相似餐點
SELECT m.*, r.name AS restaurant_name, r.cuisine_type
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
WHERE m.is_available = TRUE 
  AND r.is_active = TRUE
  AND r.cuisine_type IN (
    -- 找出使用者最常選擇的料理類型
    SELECT r2.cuisine_type
    FROM recommendation_history rh
    JOIN restaurants r2 ON rh.restaurant_id = r2.id
    WHERE rh.user_id = 1 AND rh.was_selected = TRUE
    GROUP BY r2.cuisine_type
    ORDER BY COUNT(*) DESC
    LIMIT 3
  )
  AND m.id NOT IN (
    -- 排除已經推薦過的
    SELECT meal_id FROM recommendation_history WHERE user_id = 1
  )
ORDER BY RAND()
LIMIT 5;

-- 18. 查詢某餐廳的完整資訊（包含餐點和評價）
SELECT 
    r.name AS restaurant_name,
    r.address,
    r.phone,
    r.cuisine_type,
    r.price_range,
    r.rating AS restaurant_rating,
    m.name AS meal_name,
    m.description,
    m.price,
    m.category,
    COUNT(DISTINCT rv.id) as review_count,
    AVG(rv.rating) as avg_review_rating
FROM restaurants r
LEFT JOIN meals m ON r.id = m.restaurant_id AND m.is_available = TRUE
LEFT JOIN reviews rv ON r.id = rv.restaurant_id
WHERE r.id = 1
GROUP BY r.id, r.name, r.address, r.phone, r.cuisine_type, r.price_range, 
         r.rating, m.id, m.name, m.description, m.price, m.category;

-- ==================== 維護查詢 ====================

-- 19. 找出沒有餐點的餐廳
SELECT r.* FROM restaurants r
LEFT JOIN meals m ON r.id = m.restaurant_id
WHERE m.id IS NULL;

-- 20. 找出沒有評價的餐點
SELECT m.*, r.name AS restaurant_name
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
LEFT JOIN reviews rv ON m.id = rv.meal_id
WHERE rv.id IS NULL AND m.is_available = TRUE;

-- 21. 更新餐廳平均評分
UPDATE restaurants r
SET rating = (
    SELECT COALESCE(AVG(rating), 0)
    FROM reviews
    WHERE restaurant_id = r.id
);

-- 22. 清理舊的推薦歷史（保留最近3個月）
DELETE FROM recommendation_history
WHERE recommended_at < DATE_SUB(NOW(), INTERVAL 3 MONTH);
