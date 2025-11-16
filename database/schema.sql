-- 隨機餐點推薦系統 - 資料庫架構
-- Random Meal Recommendation System - Database Schema

-- 創建資料庫
CREATE DATABASE IF NOT EXISTS meal_recommendation;
USE meal_recommendation;

-- 餐廳資料表
CREATE TABLE IF NOT EXISTS restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '餐廳名稱',
    address VARCHAR(255) COMMENT '地址',
    city VARCHAR(50) COMMENT '城市',
    district VARCHAR(50) COMMENT '行政區',
    phone VARCHAR(20) COMMENT '電話',
    cuisine_type VARCHAR(50) COMMENT '料理類型',
    price_range ENUM('低', '中', '高') DEFAULT '中' COMMENT '價格範圍',
    rating DECIMAL(2,1) DEFAULT 0.0 COMMENT '評分 (0-5)',
    latitude DECIMAL(10,7) COMMENT '緯度',
    longitude DECIMAL(10,7) COMMENT '經度',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否啟用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cuisine_type (cuisine_type),
    INDEX idx_price_range (price_range),
    INDEX idx_is_active (is_active),
    INDEX idx_city_district (city, district),
    INDEX idx_geo_coordinates (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='餐廳資訊表';

-- 餐點資料表
CREATE TABLE IF NOT EXISTS meals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL COMMENT '餐廳ID',
    name VARCHAR(100) NOT NULL COMMENT '餐點名稱',
    description TEXT COMMENT '餐點描述',
    price DECIMAL(10,2) COMMENT '價格',
    category VARCHAR(50) COMMENT '類別 (主餐/點心/飲料等)',
    is_vegetarian BOOLEAN DEFAULT FALSE COMMENT '是否素食',
    is_spicy BOOLEAN DEFAULT FALSE COMMENT '是否辣',
    image_url VARCHAR(255) COMMENT '圖片網址',
    is_available BOOLEAN DEFAULT TRUE COMMENT '是否可供應',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_meals_restaurant (restaurant_id),
    INDEX idx_category (category),
    INDEX idx_is_vegetarian (is_vegetarian),
    INDEX idx_is_available (is_available)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='餐點資訊表';

-- 使用者資料表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '使用者名稱',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '電子郵件',
    password_hash VARCHAR(255) NOT NULL COMMENT '密碼雜湊',
    full_name VARCHAR(100) COMMENT '全名',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='使用者資訊表';

-- 使用者偏好設定表
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '使用者ID',
    cuisine_type VARCHAR(50) COMMENT '偏好料理類型',
    price_range ENUM('低', '中', '高') COMMENT '偏好價格範圍',
    is_vegetarian BOOLEAN DEFAULT FALSE COMMENT '素食偏好',
    avoid_spicy BOOLEAN DEFAULT FALSE COMMENT '避免辣食',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_preference (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='使用者偏好設定表';

-- 推薦歷史記錄表
CREATE TABLE IF NOT EXISTS recommendation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '使用者ID (可為空，表示訪客)',
    meal_id INT NOT NULL COMMENT '餐點ID',
    restaurant_id INT NOT NULL COMMENT '餐廳ID',
    recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '推薦時間',
    was_selected BOOLEAN DEFAULT FALSE COMMENT '是否被選擇',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_rec_history_user (user_id),
    INDEX idx_recommended_at (recommended_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推薦歷史記錄表';

-- 收藏餐點表
CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '使用者ID',
    meal_id INT NOT NULL COMMENT '餐點ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_meal (user_id, meal_id),
    INDEX idx_favorites_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏餐點表';

-- 評價表
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '使用者ID',
    meal_id INT NOT NULL COMMENT '餐點ID',
    restaurant_id INT NOT NULL COMMENT '餐廳ID',
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5) COMMENT '評分 (1-5)',
    comment TEXT COMMENT '評論內容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_meal_review (user_id, meal_id),
    INDEX idx_meal_id (meal_id),
    INDEX idx_restaurant_id (restaurant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='評價表';

-- 標籤表
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '標籤名稱',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='標籤表';

-- 餐點標籤關聯表
CREATE TABLE IF NOT EXISTS meal_tags (
    meal_id INT NOT NULL COMMENT '餐點ID',
    tag_id INT NOT NULL COMMENT '標籤ID',
    PRIMARY KEY (meal_id, tag_id),
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='餐點標籤關聯表';
