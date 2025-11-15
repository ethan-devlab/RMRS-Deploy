-- 隨機餐點推薦系統 - 測試資料
-- Random Meal Recommendation System - Sample Data

USE meal_recommendation;

-- 插入餐廳資料
INSERT INTO restaurants (name, address, phone, cuisine_type, price_range, rating) VALUES
('小吃天堂', '台北市大安區復興南路一段100號', '02-2345-6789', '台式', '低', 4.2),
('義式風情', '台北市信義區信義路五段7號', '02-8765-4321', '義式', '高', 4.5),
('日本料理屋', '台北市中山區南京東路三段200號', '02-2567-8901', '日式', '中', 4.3),
('川味館', '台北市萬華區昆明街50號', '02-2311-2233', '川菜', '中', 4.0),
('素食養生坊', '台北市松山區南京東路四段150號', '02-2578-9012', '素食', '中', 4.4),
('美式漢堡店', '台北市大安區仁愛路四段88號', '02-2708-1234', '美式', '低', 3.8),
('韓式料理', '台北市中正區羅斯福路一段30號', '02-2395-6789', '韓式', '中', 4.1),
('廣東茶樓', '台北市大同區迪化街一段120號', '02-2555-7788', '粵菜', '高', 4.6),
('泰式餐廳', '台北市松山區八德路三段50號', '02-2570-3456', '泰式', '中', 4.2),
('法式小館', '台北市大安區敦化南路二段180號', '02-2705-8899', '法式', '高', 4.7);

-- 插入餐點資料
-- 小吃天堂的餐點
INSERT INTO meals (restaurant_id, name, description, price, category, is_vegetarian, is_spicy, is_available) VALUES
(1, '滷肉飯', '經典台灣滷肉飯，肥瘦適中', 50.00, '主餐', FALSE, FALSE, TRUE),
(1, '蚵仔煎', '新鮮蚵仔配上特製醬料', 80.00, '主餐', FALSE, FALSE, TRUE),
(1, '珍珠奶茶', '招牌珍珠奶茶', 60.00, '飲料', TRUE, FALSE, TRUE),
(1, '臭豆腐', '香脆外皮搭配泡菜', 70.00, '小吃', TRUE, FALSE, TRUE),

-- 義式風情的餐點
(2, '瑪格麗特披薩', '經典番茄莫札瑞拉披薩', 380.00, '主餐', TRUE, FALSE, TRUE),
(2, '海鮮義大利麵', '新鮮海鮮搭配白酒醬汁', 450.00, '主餐', FALSE, FALSE, TRUE),
(2, '提拉米蘇', '義大利經典甜點', 180.00, '甜點', TRUE, FALSE, TRUE),
(2, '凱薩沙拉', '新鮮生菜配凱薩醬', 250.00, '沙拉', TRUE, FALSE, TRUE),

-- 日本料理屋的餐點
(3, '鮭魚握壽司', '新鮮鮭魚握壽司套餐', 320.00, '主餐', FALSE, FALSE, TRUE),
(3, '天婦羅定食', '綜合海鮮蔬菜天婦羅', 380.00, '主餐', FALSE, FALSE, TRUE),
(3, '拉麵', '濃郁豚骨湯底拉麵', 280.00, '主餐', FALSE, FALSE, TRUE),
(3, '抹茶冰淇淋', '京都抹茶冰淇淋', 120.00, '甜點', TRUE, FALSE, TRUE),

-- 川味館的餐點
(4, '麻婆豆腐', '經典川味麻婆豆腐', 180.00, '主餐', TRUE, TRUE, TRUE),
(4, '宮保雞丁', '花生雞丁香辣可口', 220.00, '主餐', FALSE, TRUE, TRUE),
(4, '水煮魚', '麻辣鮮香水煮魚', 480.00, '主餐', FALSE, TRUE, TRUE),
(4, '酸辣湯', '開胃酸辣湯', 100.00, '湯品', FALSE, TRUE, TRUE),

-- 素食養生坊的餐點
(5, '素食滷味拼盤', '多種素料滷味', 200.00, '主餐', TRUE, FALSE, TRUE),
(5, '蔬菜咖哩', '印度風味蔬菜咖哩', 180.00, '主餐', TRUE, FALSE, TRUE),
(5, '養生燉湯', '中藥材燉煮養生湯', 150.00, '湯品', TRUE, FALSE, TRUE),
(5, '素食春捲', '新鮮蔬菜春捲', 120.00, '小吃', TRUE, FALSE, TRUE),

-- 美式漢堡店的餐點
(6, '經典牛肉漢堡', '炭烤牛肉漢堡', 180.00, '主餐', FALSE, FALSE, TRUE),
(6, '起司薯條', '金黃酥脆起司薯條', 100.00, '小吃', TRUE, FALSE, TRUE),
(6, '可樂', '冰涼可樂', 40.00, '飲料', TRUE, FALSE, TRUE),
(6, '炸雞翅', '香辣炸雞翅', 150.00, '小吃', FALSE, TRUE, TRUE),

-- 韓式料理的餐點
(7, '石鍋拌飯', '韓式石鍋拌飯', 220.00, '主餐', FALSE, TRUE, TRUE),
(7, '泡菜鍋', '正宗韓式泡菜鍋', 280.00, '主餐', FALSE, TRUE, TRUE),
(7, '韓式炸雞', '甜辣韓式炸雞', 300.00, '主餐', FALSE, TRUE, TRUE),
(7, '海鮮煎餅', '海鮮蔥煎餅', 180.00, '小吃', FALSE, FALSE, TRUE),

-- 廣東茶樓的餐點
(8, '蝦餃', '新鮮蝦仁餃', 120.00, '點心', FALSE, FALSE, TRUE),
(8, '叉燒包', '蜜汁叉燒包', 100.00, '點心', FALSE, FALSE, TRUE),
(8, '港式燒臘拼盤', '叉燒、燒鴨、油雞', 380.00, '主餐', FALSE, FALSE, TRUE),
(8, '艇仔粥', '廣東傳統艇仔粥', 150.00, '主餐', FALSE, FALSE, TRUE),

-- 泰式餐廳的餐點
(9, '綠咖哩雞', '泰式綠咖哩雞', 250.00, '主餐', FALSE, TRUE, TRUE),
(9, '泰式炒河粉', '經典泰式炒河粉', 200.00, '主餐', FALSE, FALSE, TRUE),
(9, '月亮蝦餅', '香酥月亮蝦餅', 180.00, '小吃', FALSE, FALSE, TRUE),
(9, '芒果糯米飯', '泰式芒果糯米飯', 120.00, '甜點', TRUE, FALSE, TRUE),

-- 法式小館的餐點
(10, '法式洋蔥濃湯', '經典法式洋蔥湯', 200.00, '湯品', TRUE, FALSE, TRUE),
(10, '紅酒燉牛肉', '法式紅酒燉牛肉', 680.00, '主餐', FALSE, FALSE, TRUE),
(10, '鵝肝醬', '法式鵝肝醬', 880.00, '前菜', FALSE, FALSE, TRUE),
(10, '焦糖布丁', '法式焦糖布丁', 150.00, '甜點', TRUE, FALSE, TRUE);

-- 插入標籤資料
INSERT INTO tags (name) VALUES
('人氣'), ('推薦'), ('經濟實惠'), ('高級'), ('健康'),
('快速'), ('家庭聚餐'), ('約會'), ('辣味'), ('清淡'),
('海鮮'), ('肉類'), ('蔬菜'), ('甜點'), ('湯品'),
('米飯'), ('麵食'), ('點心'), ('飲料'), ('素食');

-- 插入餐點標籤關聯
INSERT INTO meal_tags (meal_id, tag_id) VALUES
-- 滷肉飯
(1, 1), (1, 3), (1, 16),
-- 海鮮義大利麵
(6, 2), (6, 4), (6, 11),
-- 麻婆豆腐
(13, 1), (13, 9), (13, 20),
-- 素食滷味拼盤
(17, 5), (17, 20),
-- 石鍋拌飯
(25, 1), (25, 9),
-- 紅酒燉牛肉
(38, 2), (38, 4), (38, 12);

-- 插入測試使用者
INSERT INTO users (username, email, password_hash, full_name) VALUES
('testuser1', 'test1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYK5XZz8G', '測試使用者一'),
('testuser2', 'test2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYK5XZz8G', '測試使用者二'),
('testuser3', 'test3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYK5XZz8G', '測試使用者三');

-- 插入使用者偏好
INSERT INTO user_preferences (user_id, cuisine_type, price_range, is_vegetarian, avoid_spicy) VALUES
(1, '台式', '低', FALSE, FALSE),
(2, '日式', '中', FALSE, TRUE),
(3, '素食', '中', TRUE, TRUE);

-- 插入推薦歷史
INSERT INTO recommendation_history (user_id, meal_id, restaurant_id, was_selected) VALUES
(1, 1, 1, TRUE),
(1, 9, 3, FALSE),
(2, 6, 2, TRUE),
(2, 10, 3, FALSE),
(3, 17, 5, TRUE);

-- 插入收藏
INSERT INTO favorites (user_id, meal_id) VALUES
(1, 1),
(1, 9),
(2, 6),
(2, 38),
(3, 17),
(3, 18);

-- 插入評價
INSERT INTO reviews (user_id, meal_id, restaurant_id, rating, comment) VALUES
(1, 1, 1, 5, '非常好吃的滷肉飯，價格實惠！'),
(2, 6, 2, 4, '海鮮很新鮮，但價格稍高'),
(3, 17, 5, 5, '素食選擇豐富，很健康'),
(1, 9, 3, 4, '壽司新鮮，值得推薦'),
(2, 38, 10, 5, '正宗法式料理，值得品嚐');
