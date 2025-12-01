-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: meal_recommendation
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `daily_meal_records`
--

DROP TABLE IF EXISTS `daily_meal_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_meal_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `meal_type` varchar(16) NOT NULL,
  `meal_name` varchar(100) NOT NULL,
  `calories` decimal(6,2) NOT NULL,
  `protein_grams` decimal(6,2) NOT NULL,
  `carb_grams` decimal(6,2) NOT NULL,
  `fat_grams` decimal(6,2) NOT NULL,
  `meal_notes` longtext,
  `ingredients` json DEFAULT NULL,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `updated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `source_meal_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `daily_meal_records_user_id_date_meal_type_m_9366e28a_uniq` (`user_id`,`date`,`meal_type`,`meal_name`),
  KEY `idx_meal_user_date` (`user_id`,`date`),
  KEY `daily_meal_records_source_meal_id_d4ca9437_fk_meals_id` (`source_meal_id`),
  CONSTRAINT `daily_meal_records_source_meal_id_d4ca9437_fk_meals_id` FOREIGN KEY (`source_meal_id`) REFERENCES `meals` (`id`),
  CONSTRAINT `daily_meal_records_user_id_98ead3df_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `favorites`
--

DROP TABLE IF EXISTS `favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `favorites` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `meal_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `favorites_user_id_meal_id_728e64dd_uniq` (`user_id`,`meal_id`),
  KEY `favorites_meal_id_2464a1ce_fk_meals_id` (`meal_id`),
  KEY `idx_favorites_user` (`user_id`),
  CONSTRAINT `favorites_meal_id_2464a1ce_fk_meals_id` FOREIGN KEY (`meal_id`) REFERENCES `meals` (`id`),
  CONSTRAINT `favorites_user_id_d60eb79f_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `meal_components`
--

DROP TABLE IF EXISTS `meal_components`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meal_components` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `quantity` varchar(50) DEFAULT NULL,
  `calories` decimal(6,2) NOT NULL,
  `metadata` json DEFAULT NULL,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `meal_record_id` bigint DEFAULT NULL,
  `meal_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_component_record` (`meal_record_id`),
  KEY `idx_component_meal` (`meal_id`),
  CONSTRAINT `meal_components_meal_id_0aa8c011_fk_meals_id` FOREIGN KEY (`meal_id`) REFERENCES `meals` (`id`),
  CONSTRAINT `meal_components_meal_record_id_1ae3bac8_fk_daily_meal_records_id` FOREIGN KEY (`meal_record_id`) REFERENCES `daily_meal_records` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `meal_tags`
--

DROP TABLE IF EXISTS `meal_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meal_tags` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `meal_id` bigint NOT NULL,
  `tag_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `meal_tags_meal_id_tag_id_53eb23c7_uniq` (`meal_id`,`tag_id`),
  KEY `meal_tags_tag_id_93557b72_fk_tags_id` (`tag_id`),
  CONSTRAINT `meal_tags_meal_id_8cb44d93_fk_meals_id` FOREIGN KEY (`meal_id`) REFERENCES `meals` (`id`),
  CONSTRAINT `meal_tags_tag_id_93557b72_fk_tags_id` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `meals`
--

DROP TABLE IF EXISTS `meals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meals` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` longtext,
  `price` decimal(10,2) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `is_vegetarian` tinyint(1) NOT NULL,
  `is_spicy` tinyint(1) NOT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `is_available` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `updated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `restaurant_id` bigint NOT NULL,
  `image_file` varchar(100) DEFAULT NULL,
  `slug` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `idx_meals_restaurant` (`restaurant_id`),
  KEY `idx_category` (`category`),
  KEY `idx_is_vegetarian` (`is_vegetarian`),
  KEY `idx_is_available` (`is_available`),
  CONSTRAINT `meals_restaurant_id_25d01013_fk_restaurants_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `merchant_accounts`
--

DROP TABLE IF EXISTS `merchant_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `merchant_accounts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `updated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `restaurant_id` bigint NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `merchant_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `restaurant_id` (`restaurant_id`),
  UNIQUE KEY `phone` (`phone`),
  UNIQUE KEY `merchant_name` (`merchant_name`),
  KEY `idx_merchant_email` (`email`),
  CONSTRAINT `merchant_accounts_restaurant_id_19143c95_fk_restaurants_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notification_logs`
--

DROP TABLE IF EXISTS `notification_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(120) NOT NULL,
  `body` longtext NOT NULL,
  `notification_type` varchar(20) DEFAULT NULL,
  `status` varchar(10) NOT NULL,
  `sent_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `read_at` datetime(6) DEFAULT NULL,
  `extra_payload` json DEFAULT NULL,
  `user_id` bigint NOT NULL,
  `setting_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_notify_log_user` (`user_id`),
  KEY `idx_notify_log_status` (`status`),
  KEY `notification_logs_setting_id_588fd6ef_fk_notificat` (`setting_id`),
  CONSTRAINT `notification_logs_setting_id_588fd6ef_fk_notificat` FOREIGN KEY (`setting_id`) REFERENCES `notification_settings` (`id`),
  CONSTRAINT `notification_logs_user_id_d1571769_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notification_settings`
--

DROP TABLE IF EXISTS `notification_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification_settings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reminder_type` varchar(20) NOT NULL,
  `scheduled_time` time(6) DEFAULT NULL,
  `is_enabled` tinyint(1) NOT NULL,
  `channel` varchar(10) NOT NULL,
  `quiet_hours_start` time(6) DEFAULT NULL,
  `quiet_hours_end` time(6) DEFAULT NULL,
  `last_triggered_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `updated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `notification_settings_user_id_reminder_type_272ef176_uniq` (`user_id`,`reminder_type`),
  KEY `idx_notify_settings_user` (`user_id`),
  CONSTRAINT `notification_settings_user_id_ce43fde1_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nutrition_info`
--

DROP TABLE IF EXISTS `nutrition_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nutrition_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `calories` decimal(7,2) NOT NULL,
  `protein` decimal(6,2) NOT NULL,
  `fat` decimal(6,2) NOT NULL,
  `carbohydrate` decimal(6,2) NOT NULL,
  `sodium` decimal(6,2) NOT NULL,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `updated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `meal_id` bigint NOT NULL,
  `breakdown` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `meal_id` (`meal_id`),
  KEY `idx_nutrition_calories` (`calories`),
  CONSTRAINT `nutrition_info_meal_id_7e2306f3_fk_meals_id` FOREIGN KEY (`meal_id`) REFERENCES `meals` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recommendation_history`
--

DROP TABLE IF EXISTS `recommendation_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recommendation_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `recommended_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `was_selected` tinyint(1) NOT NULL DEFAULT '0',
  `meal_id` bigint NOT NULL,
  `restaurant_id` bigint NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `recommendation_history_meal_id_21980458_fk_meals_id` (`meal_id`),
  KEY `recommendation_history_restaurant_id_69aaee93_fk_restaurants_id` (`restaurant_id`),
  KEY `idx_rec_history_user` (`user_id`),
  KEY `idx_recommended_at` (`recommended_at`),
  CONSTRAINT `recommendation_history_meal_id_21980458_fk_meals_id` FOREIGN KEY (`meal_id`) REFERENCES `meals` (`id`),
  CONSTRAINT `recommendation_history_restaurant_id_69aaee93_fk_restaurants_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`id`),
  CONSTRAINT `recommendation_history_user_id_c07bb387_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `restaurants`
--

DROP TABLE IF EXISTS `restaurants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurants` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `district` varchar(50) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `cuisine_type` varchar(50) DEFAULT NULL,
  `price_range` varchar(1) NOT NULL,
  `rating` decimal(3,1) NOT NULL,
  `latitude` decimal(10,7) DEFAULT NULL,
  `longitude` decimal(10,7) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `updated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `slug` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `idx_cuisine_type` (`cuisine_type`),
  KEY `idx_price_range` (`price_range`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_city_district` (`city`,`district`),
  KEY `idx_geo_coordinates` (`latitude`,`longitude`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rating` smallint unsigned NOT NULL,
  `comment` longtext,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `updated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `meal_id` bigint NOT NULL,
  `restaurant_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reviews_user_id_meal_id_4fb37b1f_uniq` (`user_id`,`meal_id`),
  KEY `idx_reviews_meal` (`meal_id`),
  KEY `idx_reviews_restaurant` (`restaurant_id`),
  CONSTRAINT `reviews_meal_id_13424641_fk_meals_id` FOREIGN KEY (`meal_id`) REFERENCES `meals` (`id`),
  CONSTRAINT `reviews_restaurant_id_f0049c06_fk_restaurants_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`id`),
  CONSTRAINT `reviews_user_id_c23b0903_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `reviews_chk_1` CHECK ((`rating` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tags` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_preferences`
--

DROP TABLE IF EXISTS `user_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_preferences` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cuisine_type` varchar(50) DEFAULT NULL,
  `price_range` varchar(1) DEFAULT NULL,
  `is_vegetarian` tinyint(1) NOT NULL,
  `avoid_spicy` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `updated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `user_id` bigint NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `recommendation_cooldown_days` smallint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_preferences_user_id_7d5d22f7_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `user_preferences_chk_1` CHECK ((`recommendation_cooldown_days` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `updated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weekly_intake_summaries`
--

DROP TABLE IF EXISTS `weekly_intake_summaries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weekly_intake_summaries` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `week_start` date NOT NULL,
  `total_calories` decimal(8,2) NOT NULL,
  `total_protein` decimal(8,2) NOT NULL,
  `total_carbs` decimal(8,2) NOT NULL,
  `total_fat` decimal(8,2) NOT NULL,
  `meal_count` int unsigned NOT NULL,
  `calculated_at` datetime(6) NOT NULL DEFAULT (now(6)),
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `weekly_intake_summaries_user_id_week_start_56fc5410_uniq` (`user_id`,`week_start`),
  KEY `idx_weekly_user` (`user_id`,`week_start`),
  CONSTRAINT `weekly_intake_summaries_user_id_24e85f55_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `weekly_intake_summaries_chk_1` CHECK ((`meal_count` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-01 16:38:23
