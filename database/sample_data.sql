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
-- Dumping data for table `daily_meal_records`
--

LOCK TABLES `daily_meal_records` WRITE;
/*!40000 ALTER TABLE `daily_meal_records` DISABLE KEYS */;
INSERT INTO `daily_meal_records` VALUES (1,'2025-11-17','breakfast','abc',300.00,12.00,13.00,6.00,'很讚哦','[\"雞胸肉 120g\", \"雞蛋 10g\"]','2025-11-17 14:17:48.988314','2025-11-30 16:59:53.424956',NULL,4),(2,'2025-11-19','lunch','漢堡',500.00,20.00,20.00,30.00,'','[\"牛肉200g\"]','2025-11-19 23:29:06.893498','2025-11-19 23:29:06.893498',NULL,4),(3,'2025-11-20','lunch','qeh',1.00,0.10,0.10,0.10,'',NULL,'2025-11-20 20:34:21.365869','2025-11-29 21:36:07.495000',NULL,4),(4,'2025-11-30','snack','滷蛋',35.00,20.00,4.00,0.00,'',NULL,'2025-11-30 17:07:23.977761','2025-11-30 17:30:03.065467',42,4);
/*!40000 ALTER TABLE `daily_meal_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `favorites`
--

LOCK TABLES `favorites` WRITE;
/*!40000 ALTER TABLE `favorites` DISABLE KEYS */;
INSERT INTO `favorites` VALUES (8,'2025-11-18 11:06:18.212136',12,4);
/*!40000 ALTER TABLE `favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `meal_components`
--

LOCK TABLES `meal_components` WRITE;
/*!40000 ALTER TABLE `meal_components` DISABLE KEYS */;
INSERT INTO `meal_components` VALUES (5,'protein','1份 / 250g',250.00,'{\"fat\": 2.0, \"carb\": 10.0, \"protein\": 8.0}','2025-11-29 14:02:07.861927',NULL,41),(16,'雞胸肉','120g',220.00,NULL,'2025-11-30 16:59:53.434398',1,NULL),(17,'雞蛋','10g',80.00,NULL,'2025-11-30 16:59:53.434398',1,NULL),(18,'大白菜','100g',50.00,NULL,'2025-11-30 16:59:53.434398',1,NULL),(19,'甜不辣','50g',100.00,NULL,'2025-11-30 16:59:53.434398',1,NULL),(22,'蛋白質','1 / 100g',20.00,'{\"notes\": \"None\"}','2025-11-30 17:39:32.921110',NULL,42),(23,'蛋黃','1 / 100g',15.00,'{\"notes\": \"None\"}','2025-11-30 17:39:32.922088',NULL,42);
/*!40000 ALTER TABLE `meal_components` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `meal_tags`
--

LOCK TABLES `meal_tags` WRITE;
/*!40000 ALTER TABLE `meal_tags` DISABLE KEYS */;
INSERT INTO `meal_tags` VALUES (1,1,1),(2,1,3),(3,1,16),(4,6,2),(5,6,4),(6,6,11),(7,13,1),(8,13,9),(9,13,20),(10,17,5),(11,17,20),(12,25,1),(13,25,9),(14,38,2),(15,38,4),(16,38,12);
/*!40000 ALTER TABLE `meal_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `meals`
--

LOCK TABLES `meals` WRITE;
/*!40000 ALTER TABLE `meals` DISABLE KEYS */;
INSERT INTO `meals` VALUES (1,'滷肉飯','經典台灣滷肉飯，肥瘦適中',50.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',1,NULL,'meal-YCBfDQ'),(2,'蚵仔煎','新鮮蚵仔配上特製醬料',80.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',1,NULL,'meal-zKYD4h'),(3,'珍珠奶茶','招牌珍珠奶茶',60.00,'飲料',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',1,NULL,'meal-UKfmj7'),(4,'臭豆腐','香脆外皮搭配泡菜',70.00,'小吃',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',1,NULL,'meal-55MBX6'),(5,'瑪格麗特披薩','經典番茄莫札瑞拉披薩',380.00,'主餐',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',2,NULL,'meal-gNCv3R'),(6,'海鮮義大利麵','新鮮海鮮搭配白酒醬汁',450.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',2,NULL,'meal-ExGAed'),(7,'提拉米蘇','義大利經典甜點',180.00,'甜點',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',2,NULL,'meal-SbLhlW'),(8,'凱薩沙拉','新鮮生菜配凱薩醬',250.00,'沙拉',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',2,NULL,'meal-Mc82L0'),(9,'鮭魚握壽司','新鮮鮭魚握壽司套餐',320.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',3,NULL,'meal-KIoopm'),(10,'天婦羅定食','綜合海鮮蔬菜天婦羅',380.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',3,NULL,'meal-PoWKr2'),(11,'拉麵','濃郁豚骨湯底拉麵',280.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',3,NULL,'meal-oypAJB'),(12,'抹茶冰淇淋','京都抹茶冰淇淋',120.00,'甜點',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',3,NULL,'meal-Mgw5wH'),(13,'麻婆豆腐','經典川味麻婆豆腐',180.00,'主餐',1,1,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',4,NULL,'meal-2wRGkV'),(14,'宮保雞丁','花生雞丁香辣可口',220.00,'主餐',0,1,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',4,NULL,'meal-jU0uXa'),(15,'水煮魚','麻辣鮮香水煮魚',480.00,'主餐',0,1,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',4,NULL,'meal-tBUajx'),(16,'酸辣湯','開胃酸辣湯',100.00,'湯品',0,1,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',4,NULL,'meal-PP8U7p'),(17,'素食滷味拼盤','多種素料滷味',200.00,'主餐',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',5,NULL,'meal-mgqEhq'),(18,'蔬菜咖哩','印度風味蔬菜咖哩',180.00,'主餐',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',5,NULL,'meal-BNGCWO'),(19,'養生燉湯','中藥材燉煮養生湯',150.00,'湯品',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',5,NULL,'meal-5kMqcz'),(20,'素食春捲','新鮮蔬菜春捲',120.00,'小吃',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',5,NULL,'meal-0wXuhU'),(21,'經典牛肉漢堡','炭烤牛肉漢堡',180.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',6,NULL,'meal-q9GwUR'),(22,'起司薯條','金黃酥脆起司薯條',100.00,'小吃',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',6,NULL,'meal-rC6MxI'),(23,'可樂','冰涼可樂',40.00,'飲料',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',6,NULL,'meal-XKCxg3'),(24,'炸雞翅','香辣炸雞翅',150.00,'小吃',0,1,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',6,NULL,'meal-uG5ikI'),(25,'石鍋拌飯','韓式石鍋拌飯',220.00,'主餐',0,1,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',7,NULL,'meal-6eklgZ'),(26,'泡菜鍋','正宗韓式泡菜鍋',280.00,'主餐',0,1,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',7,NULL,'meal-3pwkVJ'),(27,'韓式炸雞','甜辣韓式炸雞',300.00,'主餐',0,1,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',7,NULL,'meal-NFNqSO'),(28,'海鮮煎餅','海鮮蔥煎餅',180.00,'小吃',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',7,NULL,'meal-1yCOrM'),(29,'蝦餃','新鮮蝦仁餃',120.00,'點心',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',8,NULL,'meal-7aVkgC'),(30,'叉燒包','蜜汁叉燒包',100.00,'點心',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',8,NULL,'meal-nAUNc4'),(31,'港式燒臘拼盤','叉燒、燒鴨、油雞',380.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',8,NULL,'meal-SjyN0q'),(32,'艇仔粥','廣東傳統艇仔粥',150.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',8,NULL,'meal-B2zE9A'),(33,'綠咖哩雞','泰式綠咖哩雞',250.00,'主餐',0,1,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',9,NULL,'meal-njre7V'),(34,'泰式炒河粉','經典泰式炒河粉',200.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',9,NULL,'meal-uLZxSa'),(35,'月亮蝦餅','香酥月亮蝦餅',180.00,'小吃',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',9,NULL,'meal-8gBBUt'),(36,'芒果糯米飯','泰式芒果糯米飯',120.00,'甜點',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',9,NULL,'meal-xev70Y'),(37,'法式洋蔥濃湯','經典法式洋蔥湯',200.00,'湯品',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',10,NULL,'meal-P4rSGK'),(38,'紅酒燉牛肉','法式紅酒燉牛肉',680.00,'主餐',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',10,NULL,'meal-uUuewN'),(39,'鵝肝醬','法式鵝肝醬',880.00,'前菜',0,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',10,NULL,'meal-uirUpZ'),(40,'焦糖布丁','法式焦糖布丁',150.00,'甜點',1,0,NULL,1,'2025-11-15 22:53:03.938334','2025-11-15 22:53:03.938334',10,NULL,'meal-MjMSca'),(41,'abc','很好吃的東西',100.00,'甜點',0,0,'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTWirn3R2dxxyKQPULeq46IWK-ZrWOWn3Hemg&s',1,'2025-11-29 13:52:22.247177','2025-12-01 01:20:40.048425',13,NULL,'abcd-abc'),(42,'滷蛋','超級好吃的滷蛋',10.00,'小食',0,0,NULL,1,'2025-11-29 21:49:49.991928','2025-11-30 17:39:32.920086',13,'meals/photos/egg_1oBg0xm.jpg','abcd');
/*!40000 ALTER TABLE `meals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `merchant_accounts`
--

LOCK TABLES `merchant_accounts` WRITE;
/*!40000 ALTER TABLE `merchant_accounts` DISABLE KEYS */;
INSERT INTO `merchant_accounts` VALUES (1,'test@example.com','pbkdf2_sha256$1000000$U15aLtJirB9LOeHHwnT893$uIpRpPyOEDfOu/NHTxTpi6nN2Tkyacn0k8KYpVNmiUA=','2025-11-29 13:34:37.602572','2025-12-01 00:27:30.263326',13,'0912345678','test');
/*!40000 ALTER TABLE `merchant_accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `notification_logs`
--

LOCK TABLES `notification_logs` WRITE;
/*!40000 ALTER TABLE `notification_logs` DISABLE KEYS */;
INSERT INTO `notification_logs` VALUES (1,'已記錄 早餐','abc · 300 kcal','meal_record','sent','2025-11-17 14:17:49.005471',NULL,'{\"meal_type\": \"breakfast\", \"record_id\": 1}',4,NULL),(2,'提醒已安排','random 推播預覽','preview','read','2025-11-17 14:21:58.587751','2025-11-17 14:22:32.088875',NULL,4,NULL),(3,'已記錄 午餐','漢堡 · 500 kcal','meal_record','sent','2025-11-19 23:29:06.908660',NULL,'{\"meal_type\": \"lunch\", \"record_id\": 2}',4,NULL),(4,'提醒已安排','random 推播預覽','preview','sent','2025-11-20 19:54:50.717351',NULL,NULL,5,NULL),(5,'已記錄 午餐','qeh · 1 kcal','meal_record','sent','2025-11-20 20:34:21.379222',NULL,'{\"meal_type\": \"lunch\", \"record_id\": 3}',4,NULL),(6,'已記錄 點心','滷蛋 · 35.00 kcal','meal_record','sent','2025-11-30 17:07:23.989800',NULL,'{\"meal_type\": \"snack\", \"record_id\": 4}',4,NULL);
/*!40000 ALTER TABLE `notification_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `notification_settings`
--

LOCK TABLES `notification_settings` WRITE;
/*!40000 ALTER TABLE `notification_settings` DISABLE KEYS */;
INSERT INTO `notification_settings` VALUES (1,'breakfast','08:30:00.000000',1,'push',NULL,NULL,NULL,'2025-11-17 14:14:59.181810','2025-11-17 14:21:55.358062',4),(2,'lunch','12:30:00.000000',1,'email',NULL,NULL,NULL,'2025-11-17 14:14:59.186343','2025-12-01 15:11:49.481101',4),(3,'dinner','18:30:00.000000',1,'push',NULL,NULL,NULL,'2025-11-17 14:14:59.191400','2025-11-17 14:14:59.191400',4),(4,'snack','15:30:00.000000',1,'push',NULL,NULL,NULL,'2025-11-17 14:14:59.195502','2025-11-17 14:14:59.195502',4),(5,'random',NULL,1,'push',NULL,NULL,NULL,'2025-11-17 14:14:59.199503','2025-11-17 14:14:59.199503',4),(6,'breakfast','08:00:00.000000',1,'push',NULL,NULL,NULL,'2025-11-20 19:47:27.618107','2025-11-20 19:47:27.618107',5),(7,'lunch','12:00:00.000000',1,'push',NULL,NULL,NULL,'2025-11-20 19:47:27.623111','2025-11-20 19:59:30.375695',5),(8,'dinner','18:30:00.000000',1,'push',NULL,NULL,NULL,'2025-11-20 19:47:27.628523','2025-11-20 19:47:27.628523',5),(9,'snack','15:30:00.000000',1,'push',NULL,NULL,NULL,'2025-11-20 19:47:27.632533','2025-11-20 19:47:27.632533',5),(10,'random','19:54:00.000000',1,'push',NULL,NULL,NULL,'2025-11-20 19:47:27.637534','2025-11-20 19:59:46.996995',5);
/*!40000 ALTER TABLE `notification_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `nutrition_info`
--

LOCK TABLES `nutrition_info` WRITE;
/*!40000 ALTER TABLE `nutrition_info` DISABLE KEYS */;
INSERT INTO `nutrition_info` VALUES (4,35.00,20.00,0.00,4.00,0.00,'2025-11-30 16:54:45.864741','2025-11-30 17:39:32.923087',42,'[{\"fat\": null, \"carb\": null, \"name\": \"蛋白質\", \"notes\": \"None\", \"protein\": 20.0, \"calories\": 20.0, \"quantity\": \"1 / 100g\"}, {\"fat\": null, \"carb\": 4.0, \"name\": \"蛋黃\", \"notes\": \"None\", \"protein\": null, \"calories\": 15.0, \"quantity\": \"1 / 100g\"}]');
/*!40000 ALTER TABLE `nutrition_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `recommendation_history`
--

LOCK TABLES `recommendation_history` WRITE;
/*!40000 ALTER TABLE `recommendation_history` DISABLE KEYS */;
INSERT INTO `recommendation_history` VALUES (1,'2025-11-15 22:53:03.960024',1,1,1,NULL),(2,'2025-11-15 22:53:03.960024',0,9,3,NULL),(3,'2025-11-15 22:53:03.960024',1,6,2,NULL),(4,'2025-11-15 22:53:03.960024',0,10,3,NULL),(5,'2025-11-15 22:53:03.960024',1,17,5,NULL),(6,'2025-11-30 17:30:03.071513',1,42,13,4);
/*!40000 ALTER TABLE `recommendation_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `restaurants`
--

LOCK TABLES `restaurants` WRITE;
/*!40000 ALTER TABLE `restaurants` DISABLE KEYS */;
INSERT INTO `restaurants` VALUES (1,'小吃天堂','台北市大安區復興南路一段100號',NULL,NULL,'02-2345-6789','台式','低',4.2,25.0236427,121.5482094,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-1vVQ6V'),(2,'義式風情','台北市信義區信義路五段7號',NULL,NULL,'02-8765-4321','義式','高',4.5,25.0340732,121.5645711,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-j03kQ2'),(3,'日本料理屋','台北市中山區南京東路三段200號',NULL,NULL,'02-2567-8901','日式','中',4.3,25.0518058,121.5429433,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-15DVn6'),(4,'川味館','台北市萬華區昆明街50號',NULL,NULL,'02-2311-2233','川菜','中',4.0,25.0465067,121.5057002,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-WVSFBl'),(5,'素食養生坊','台北市松山區南京東路四段150號',NULL,NULL,'02-2578-9012','素食','中',4.4,25.0514661,121.5559825,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-KWo63n'),(6,'美式漢堡店','台北市大安區仁愛路四段88號',NULL,NULL,'02-2708-1234','美式','低',3.8,25.0370614,121.5483798,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-xsNl17'),(7,'韓式料理','台北市中正區羅斯福路一段30號',NULL,NULL,'02-2395-6789','韓式','中',4.1,25.0315107,121.5189205,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-g49qaM'),(8,'廣東茶樓','台北市大同區迪化街一段120號',NULL,NULL,'02-2555-7788','粵菜','高',4.6,25.0569187,121.5097921,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-Robsmx'),(9,'泰式餐廳','台北市松山區八德路三段50號',NULL,NULL,'02-2570-3456','泰式','中',4.2,25.0482428,121.5522647,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-9hKGP0'),(10,'法式小館','台北市大安區敦化南路二段180號',NULL,NULL,'02-2705-8899','法式','高',4.7,25.0237885,121.5481987,1,'2025-11-15 22:53:03.925238','2025-11-15 22:53:03.925238','restaurant-t21YJ4'),(11,'辣訣-秘藏鍋物-台中逢甲店','台中市西屯區文華路121之30號','台中市','西屯區','04-2452-0023','台式','中',4.5,24.1802394,120.6464016,1,'2024-06-10 10:00:00.000000','2024-06-10 10:00:00.000000','restaurant-2WcfjX'),(12,'星空（逢甲店）','台中市西屯區文華路121號','台中市','西屯區','04-2451-0121','意式','高',4.3,24.1796536,120.6462347,1,'2025-11-10 10:00:00.000000','2025-11-10 10:00:00.000000','restaurant-MOqT1W'),(13,'abcd','台中市西屯區文華路100號','台中市','西屯區','0912345678','台式','中',0.0,24.1793236,120.6467981,1,'2025-11-29 13:34:37.196961','2025-12-01 00:35:48.048285','abcd');
/*!40000 ALTER TABLE `restaurants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (6,5,'讚讚讚','2025-11-18 11:06:01.201261','2025-11-18 11:06:01.201261',14,4,4),(7,4,'good!!','2025-11-20 18:58:00.609881','2025-11-24 13:15:18.020572',1,1,4);
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'人氣','2025-11-15 22:53:03.945633'),(2,'推薦','2025-11-15 22:53:03.945633'),(3,'經濟實惠','2025-11-15 22:53:03.945633'),(4,'高級','2025-11-15 22:53:03.945633'),(5,'健康','2025-11-15 22:53:03.945633'),(6,'快速','2025-11-15 22:53:03.945633'),(7,'家庭聚餐','2025-11-15 22:53:03.945633'),(8,'約會','2025-11-15 22:53:03.945633'),(9,'辣味','2025-11-15 22:53:03.945633'),(10,'清淡','2025-11-15 22:53:03.945633'),(11,'海鮮','2025-11-15 22:53:03.945633'),(12,'肉類','2025-11-15 22:53:03.945633'),(13,'蔬菜','2025-11-15 22:53:03.945633'),(14,'甜點','2025-11-15 22:53:03.945633'),(15,'湯品','2025-11-15 22:53:03.945633'),(16,'米飯','2025-11-15 22:53:03.945633'),(17,'麵食','2025-11-15 22:53:03.945633'),(18,'點心','2025-11-15 22:53:03.945633'),(19,'飲料','2025-11-15 22:53:03.945633'),(20,'素食','2025-11-15 22:53:03.945633');
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user_preferences`
--

LOCK TABLES `user_preferences` WRITE;
/*!40000 ALTER TABLE `user_preferences` DISABLE KEYS */;
INSERT INTO `user_preferences` VALUES (4,'日式','中',1,0,'2025-11-17 15:31:08.048136','2025-11-30 18:24:59.039846',4,'',8),(5,NULL,NULL,0,0,'2025-11-20 19:54:16.401079','2025-11-20 19:54:16.401079',5,NULL,NULL);
/*!40000 ALTER TABLE `user_preferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (4,'test','test@example.com','pbkdf2_sha256$1000000$IkZLWEwlFxx5UHGAxHWKW9$v2S7UjAWSPXsjOgfCSm8WelAcUFPLykHiMk6P+SipFQ=','tester','2025-11-17 10:43:49.923845','2025-11-29 18:39:46.376032','0123456789'),(5,'Tim','test@gmail.com','pbkdf2_sha256$1000000$AqIBU9fOxwDTIlWQHvuPCv$U4TUC4AUQWoPrE0o9gTwn3mtAARsQNdkpFWi6RKUAhk=','hahaha','2025-11-20 19:47:27.363007','2025-11-20 19:47:27.363007',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `weekly_intake_summaries`
--

LOCK TABLES `weekly_intake_summaries` WRITE;
/*!40000 ALTER TABLE `weekly_intake_summaries` DISABLE KEYS */;
INSERT INTO `weekly_intake_summaries` VALUES (1,'2025-11-17',801.00,32.10,33.10,36.10,3,'2025-11-17 14:14:59.170564',4),(2,'2025-11-17',0.00,0.00,0.00,0.00,0,'2025-11-20 19:47:27.608106',5),(3,'2025-11-24',35.00,20.00,4.00,0.00,1,'2025-11-24 10:43:52.114739',4),(4,'2025-12-01',0.00,0.00,0.00,0.00,0,'2025-12-01 00:04:45.053348',4);
/*!40000 ALTER TABLE `weekly_intake_summaries` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-01 16:35:47
