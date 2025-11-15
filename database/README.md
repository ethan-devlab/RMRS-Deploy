# 隨機餐點推薦系統 - 資料庫說明文件

## 資料庫概述

這是一個完整的隨機餐點推薦系統資料庫架構，支援餐廳管理、餐點資訊、使用者偏好設定、推薦歷史記錄、收藏功能和評價系統。

## 資料庫架構

### 核心資料表

#### 1. restaurants（餐廳資訊表）
儲存餐廳的基本資訊。

**欄位說明：**
- `id`: 主鍵，自動遞增
- `name`: 餐廳名稱（必填）
- `address`: 地址
- `phone`: 電話號碼
- `cuisine_type`: 料理類型（如：台式、日式、義式等）
- `price_range`: 價格範圍（低、中、高）
- `rating`: 評分（0-5分）
- `is_active`: 是否啟用
- `created_at`: 建立時間
- `updated_at`: 更新時間

**索引：**
- cuisine_type, price_range, is_active

---

#### 2. meals（餐點資訊表）
儲存各餐廳提供的餐點資訊。

**欄位說明：**
- `id`: 主鍵，自動遞增
- `restaurant_id`: 餐廳ID（外鍵）
- `name`: 餐點名稱（必填）
- `description`: 餐點描述
- `price`: 價格
- `category`: 類別（主餐、點心、飲料等）
- `is_vegetarian`: 是否素食
- `is_spicy`: 是否辣
- `image_url`: 圖片網址
- `is_available`: 是否可供應
- `created_at`: 建立時間
- `updated_at`: 更新時間

**索引：**
- restaurant_id, category, is_vegetarian, is_available

---

#### 3. users（使用者資訊表）
儲存使用者帳號資訊。

**欄位說明：**
- `id`: 主鍵，自動遞增
- `username`: 使用者名稱（唯一，必填）
- `email`: 電子郵件（唯一，必填）
- `password_hash`: 密碼雜湊值
- `full_name`: 全名
- `created_at`: 建立時間
- `updated_at`: 更新時間

**索引：**
- username, email

---

#### 4. user_preferences（使用者偏好設定表）
儲存使用者的個人化偏好設定。

**欄位說明：**
- `id`: 主鍵，自動遞增
- `user_id`: 使用者ID（外鍵，唯一）
- `cuisine_type`: 偏好料理類型
- `price_range`: 偏好價格範圍
- `is_vegetarian`: 素食偏好
- `avoid_spicy`: 避免辣食
- `created_at`: 建立時間
- `updated_at`: 更新時間

---

#### 5. recommendation_history（推薦歷史記錄表）
記錄系統推薦給使用者的餐點歷史。

**欄位說明：**
- `id`: 主鍵，自動遞增
- `user_id`: 使用者ID（外鍵，可為空）
- `meal_id`: 餐點ID（外鍵）
- `restaurant_id`: 餐廳ID（外鍵）
- `recommended_at`: 推薦時間
- `was_selected`: 是否被選擇

**索引：**
- user_id, recommended_at

---

#### 6. favorites（收藏餐點表）
儲存使用者收藏的餐點。

**欄位說明：**
- `id`: 主鍵，自動遞增
- `user_id`: 使用者ID（外鍵）
- `meal_id`: 餐點ID（外鍵）
- `created_at`: 建立時間

**唯一鍵：**
- (user_id, meal_id)

---

#### 7. reviews（評價表）
儲存使用者對餐點和餐廳的評價。

**欄位說明：**
- `id`: 主鍵，自動遞增
- `user_id`: 使用者ID（外鍵）
- `meal_id`: 餐點ID（外鍵）
- `restaurant_id`: 餐廳ID（外鍵）
- `rating`: 評分（1-5分）
- `comment`: 評論內容
- `created_at`: 建立時間
- `updated_at`: 更新時間

**唯一鍵：**
- (user_id, meal_id)

---

#### 8. tags（標籤表）
儲存可用的標籤。

**欄位說明：**
- `id`: 主鍵，自動遞增
- `name`: 標籤名稱（唯一）
- `created_at`: 建立時間

---

#### 9. meal_tags（餐點標籤關聯表）
關聯餐點與標籤的多對多關係。

**欄位說明：**
- `meal_id`: 餐點ID（外鍵）
- `tag_id`: 標籤ID（外鍵）

**主鍵：**
- (meal_id, tag_id)

---

## 資料庫關聯圖

```
restaurants (1) ----< (N) meals
     |                      |
     |                      |----< (N) meal_tags >---- (N) tags
     |                      |
     |                      |----< (N) reviews
     |                      |
     |                      |----< (N) favorites
     |                      |
     |                      |----< (N) recommendation_history
     |
     |----< (N) reviews
     |
     |----< (N) recommendation_history

users (1) ---- (1) user_preferences
  |
  |----< (N) favorites
  |
  |----< (N) reviews
  |
  |----< (N) recommendation_history
```

---

## 安裝說明

### 前置需求
- MySQL 5.7+ 或 MariaDB 10.2+
- 資料庫管理工具（如 MySQL Workbench、phpMyAdmin 或命令列工具）

### 安裝步驟

1. **建立資料庫和資料表**
```bash
mysql -u root -p < database/schema.sql
```

2. **匯入測試資料**
```bash
mysql -u root -p < database/sample_data.sql
```

3. **驗證安裝**
```sql
USE meal_recommendation;
SHOW TABLES;
SELECT COUNT(*) FROM restaurants;
SELECT COUNT(*) FROM meals;
```

---

## 使用範例

### 1. 隨機推薦餐點

```sql
-- 隨機推薦一個可用的餐點
SELECT m.*, r.name AS restaurant_name, r.address
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
WHERE m.is_available = TRUE AND r.is_active = TRUE
ORDER BY RAND()
LIMIT 1;
```

### 2. 根據使用者偏好推薦

```sql
-- 根據使用者ID為1的偏好推薦餐點
SELECT m.*, r.name AS restaurant_name
FROM meals m
JOIN restaurants r ON m.restaurant_id = r.id
JOIN user_preferences up ON up.user_id = 1
WHERE m.is_available = TRUE 
  AND r.is_active = TRUE
  AND (up.is_vegetarian = FALSE OR m.is_vegetarian = TRUE)
  AND (up.avoid_spicy = FALSE OR m.is_spicy = FALSE)
  AND r.cuisine_type = up.cuisine_type
  AND r.price_range = up.price_range
ORDER BY RAND()
LIMIT 5;
```

### 3. 記錄推薦歷史

```sql
-- 記錄推薦給使用者
INSERT INTO recommendation_history (user_id, meal_id, restaurant_id, was_selected)
VALUES (1, 5, 2, TRUE);
```

### 4. 新增收藏

```sql
-- 使用者收藏餐點
INSERT INTO favorites (user_id, meal_id)
VALUES (1, 5);
```

### 5. 提交評價

```sql
-- 使用者評價餐點
INSERT INTO reviews (user_id, meal_id, restaurant_id, rating, comment)
VALUES (1, 5, 2, 5, '非常好吃！');
```

---

## 查詢範例

詳細的查詢範例請參考 `database/queries.sql` 檔案，包含：

1. 基本查詢（餐廳、餐點查詢）
2. 推薦系統查詢（隨機推薦、智能推薦）
3. 統計查詢（評分、人氣統計）
4. 進階查詢（個人化推薦、歷史分析）
5. 維護查詢（資料清理、更新）

---

## 效能優化建議

### 1. 索引優化
資料庫已經建立了必要的索引，包括：
- 外鍵索引
- 常用查詢欄位索引
- 唯一鍵索引

### 2. 查詢優化
- 使用 `EXPLAIN` 分析查詢計畫
- 避免 `SELECT *`，只選擇需要的欄位
- 適當使用 `LIMIT` 限制結果數量
- 使用 JOIN 而非子查詢（在適當情況下）

### 3. 資料維護
- 定期清理舊的推薦歷史記錄
- 更新餐廳平均評分
- 歸檔或刪除不活躍的資料

### 4. 快取策略
- 熱門餐廳和餐點可以快取在 Redis 或 Memcached
- 使用者偏好設定適合快取
- 評分統計可以定期更新而非即時計算

---

## 安全性考量

### 1. 密碼處理
- 密碼必須使用 bcrypt、scrypt 或 Argon2 進行雜湊
- 範例中的密碼雜湊僅供測試使用

### 2. SQL 注入防護
- 使用參數化查詢（Prepared Statements）
- 驗證和清理使用者輸入

### 3. 存取控制
- 實作使用者認證和授權機制
- 限制資料庫使用者權限
- 使用 HTTPS 保護資料傳輸

---

## 擴展建議

### 1. 功能擴展
- 增加餐廳營業時間表
- 支援餐點圖片上傳和管理
- 增加優惠券和促銷活動功能
- 實作餐廳預約系統
- 增加配送服務資訊

### 2. 推薦演算法優化
- 協同過濾（Collaborative Filtering）
- 內容基礎推薦（Content-Based Filtering）
- 混合式推薦系統
- 機器學習模型整合

### 3. 資料分析
- 使用者行為分析
- 熱門餐點趨勢分析
- 時段分析（午餐、晚餐）
- 地理位置分析

---

## 備份與還原

### 備份資料庫
```bash
mysqldump -u root -p meal_recommendation > backup_$(date +%Y%m%d).sql
```

### 還原資料庫
```bash
mysql -u root -p meal_recommendation < backup_20231101.sql
```

---

## 疑難排解

### 常見問題

**Q: 無法建立外鍵約束**
A: 確認 InnoDB 引擎已啟用，且參考的表和欄位存在。

**Q: 字元編碼問題**
A: 確保資料庫、資料表和連線都使用 utf8mb4 編碼。

**Q: 推薦結果不夠隨機**
A: MySQL 的 RAND() 函數在大資料集上效能較差，考慮在應用層實作隨機選擇。

---

## 授權與聯絡

本資料庫架構為隨機餐點推薦系統專案的一部分。

**版本：** 1.0  
**最後更新：** 2025-11-06
