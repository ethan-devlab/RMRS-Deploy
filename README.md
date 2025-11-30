# Random Meal Recommendation System (RMRS)

A Django-based web application that helps users discover and track meals from local restaurants through personalized recommendations, nutrition tracking, and health-focused features.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Development](#development)
- [Testing](#testing)
- [API Overview](#api-overview)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### User Features
- **Meal Recommendations** - Get personalized meal suggestions based on preferences
- **Nutrition Tracking** - Log daily meals and track calories, protein, carbs, and fat
- **Weekly Health Reports** - View aggregated nutrition summaries
- **Favorites** - Save and organize preferred meals
- **Reviews & Ratings** - Rate and review meals and restaurants
- **Search** - Find restaurants by cuisine, location, or price range
- **Notifications** - Customizable meal reminders (breakfast, lunch, dinner)

### Merchant Features
- **Restaurant Management** - Manage restaurant profiles with location data
- **Menu Management** - Add, edit, and remove meals with photos
- **Nutrition Info** - Provide detailed nutritional information for meals
- **Analytics Dashboard** - View restaurant performance metrics

### Recommendation System
- Personalized suggestions based on user preferences
- Cooldown system to avoid repetitive recommendations
- Cuisine type, price range, and dietary filters (vegetarian, spicy)

## 🛠 Tech Stack

- **Backend**: Django 5.2.1, Python 3.x
- **Database**: MySQL 5.7+ / MariaDB 10.2+
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS 4.x
- **Maps**: Folium (interactive maps)
- **Image Processing**: Pillow

## 📁 Project Structure

```
RandomMealRecommendationSystem/
├── RMRS/                           # Django project root
│   ├── manage.py                   # Django CLI entrypoint
│   ├── package.json                # Node.js deps (Tailwind CSS)
│   ├── env/                        # Environment files (.env)
│   ├── media/                      # User uploads (meal photos)
│   ├── static/                     # Shared static assets
│   ├── templates/                  # Shared templates
│   ├── RMRS/                       # Django settings module
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── UserSideApp/                # User-facing features
│   │   ├── models.py               # AppUser, Preferences, Reviews, etc.
│   │   ├── services.py             # Business logic layer
│   │   ├── views/                  # View modules (auth, meals, health, etc.)
│   │   ├── templates/              # User UI templates
│   │   └── static/                 # User-specific CSS/JS
│   ├── MerchantSideApp/            # Merchant/admin features
│   │   ├── models.py               # Restaurant, Meal, Nutrition, Tags
│   │   ├── views/                  # Merchant view modules
│   │   ├── templates/              # Merchant UI templates
│   │   └── static/                 # Merchant-specific CSS/JS
│   └── RecommendationSystem/       # Recommendation engine
│       ├── models.py               # RecommendationHistory
│       ├── services.py             # Recommendation algorithms
│       └── views/                  # Recommendation API endpoints
├── database/                       # Standalone DB utilities
│   ├── schema.sql                  # Database schema
│   ├── sample_data.sql             # Test data
│   ├── db_manager.py               # DB helper functions
│   ├── recommendation_engine.py    # Standalone recommendation logic
│   └── cli.py                      # Database CLI tool
├── requirements.txt                # Python dependencies
└── README.md
```

## 📋 Prerequisites

- Python 3.10+
- MySQL 5.7+ or MariaDB 10.2+
- Node.js 18+ (for Tailwind CSS compilation)
- pip (Python package manager)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ethan-devlab/RandomMealRecommendationSystem.git
cd RandomMealRecommendationSystem
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Node.js Dependencies (for Tailwind CSS)

```bash
cd RMRS
npm install
```

## ⚙️ Environment Configuration

Create an environment file at `RMRS/env/.env`:

```env
# Database Configuration
DB_NAME=meal_recommendation
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

## 🗄️ Database Setup

### Initialize the Database
Create the database in MySQL/MariaDB:

```sql
CREATE DATABASE IF NOT EXISTS meal_recommendation;
CREATE USER IF NOT EXISTS 'rmrs_user'@'localhost' IDENTIFIED BY 'rmrs_password';
GRANT ALL PRIVILEGES ON *.* TO 'rmrs_user'@'localhost';
```

### Migrate Database Schema

```bash
cd RMRS
python manage.py migrate
```

### Create a Superuser (Admin Access)

```bash
python RMRS/manage.py createsuperuser
```

**Default Superuser (for development):**
- Username: `rmrs-admin`
- Password: `rmrs-password`

> ⚠️ **Note**: Always use secure credentials in production environments.

## 🏃 Running the Application

### Start the Development Server

```bash
cd RMRS
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000`

### Build Tailwind CSS

**One-time build:**
```bash
npm run css:build
```

**Watch mode (auto-rebuild on changes):**
```bash
npm run css:watch
```

**Production build (minified):**
```bash
npm run css:prod
```

## 🔧 Development

### Making Model Changes

When modifying Django models:

```bash
python RMRS/manage.py makemigrations
python RMRS/manage.py migrate
```

### Code Organization Conventions

- **Views**: Split into modules under `views/` directory (e.g., `auth.py`, `meals.py`)
- **Business Logic**: Keep in `services.py`, not in views
- **Templates**: `templates/<appname>/` within each app
- **Static Files**: `static/<appname>/` within each app
- **Auth Utilities**: Common auth helpers in `auth_utils.py`

### Timezone Handling

The project uses `Asia/Taipei` timezone with `USE_TZ = False`. All datetime operations use local time.

## 🧪 Testing

### Run Django Tests

```bash
python RMRS/manage.py test
```

## 📡 API Overview

### User Endpoints (`/user/`)
- Authentication (login, register, logout)
- Meal search and recommendations
- Favorites management
- Reviews and ratings
- Health tracking (daily meals, weekly summaries)
- Notification settings

### Merchant Endpoints (`/merchant/`)
- Authentication (login, register)
- Restaurant profile management
- Menu/meal CRUD operations
- Nutrition information management
- Dashboard analytics

### Recommendation Endpoints (`/recommendation/`)
- Get personalized meal suggestions
- Recommendation history

## 📄 License

This project is part of a Software Engineering Practice course.

---

**Version:** 1.0  
**Last Updated:** December 2025
