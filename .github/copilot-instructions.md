<!-- Copilot / AI agent instructions for the RandomMealRecommendationSystem repo -->

# Copilot Instructions — RandomMealRecommendationSystem

Purpose: give AI coding agents the minimal, high-value context to be productive in this repository.

**Quick Start (Windows PowerShell)**
- **Create and activate venv:** `python -m venv venv; .\venv\Scripts\Activate.ps1`
- **Install deps:** `pip install -r requirements.txt`
- **Run migrations:** `python RMRS/manage.py migrate`
- **Start dev server:** `python RMRS/manage.py runserver`
- **Run tests (Django):** `python RMRS/manage.py test`

**High-level architecture (what to know first)**
- This is a Django monolith located under `RMRS/` with three key Django apps:
  - `UserSideApp` — user-facing views, templates and static for app users. See `UserSideApp/views/`, `UserSideApp/services.py`, and `UserSideApp/models.py`.
  - `MerchantSideApp` — merchant/admin UI and endpoints. See `MerchantSideApp/views/`, `MerchantSideApp/templates/merchantsideapp/`.
  - `RecommendationSystem` — recommendation/history models and APIs used to suggest meals.
- Django settings: `RMRS/RMRS/settings.py` — important patterns:
  - `.env` is loaded from `env/.env` (see `load_dotenv`). Do not hard-code secrets in commits.
  - Database is MySQL and configured via environment variables: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
  - `TIME_ZONE` is `Asia/Taipei` and `USE_TZ = False` — datetime behavior is local-time.

**Project-specific workflows & files to inspect**
- Database / seed / utilities: `database/` — contains `cli.py`, `db_manager.py`, `schema.sql`, `sample_data.sql`, and `test_database.py` (standalone DB helpers and sample SQL).
- Recommendation engine: `database/recommendation_engine.py` — standalone logic for generating suggestions; may be run directly for experiments.
- Templates and static assets: app-local under `*/templates/*` and `*/static/*`. There is also `all_templates/` with front-end examples for Merchant/User.
- Django management entrypoint: `RMRS/manage.py` — use for migrations, tests, and running server.

**Patterns & conventions (specific to this repo)**
- App organization: each Django app keeps templates under `templates/<appname>/` and static under `static/<appname>/`.
- Services layer: look for `services.py` (e.g., `UserSideApp/services.py`) for business logic separated from views.
- Auth helpers: `UserSideApp/auth_utils.py` contains authentication-related utilities used across views.
- Migrations are tracked in each app under `*/migrations/` — apply and include migrations in PRs when changing models.
- Front-end assets stay separated: HTML templates go under the app’s `templates/`, CSS/JS belongs in `static/<appname>/` (see `all_templates/` for reference layouts) — avoid mixing inline CSS/JS unless needed for Django templating.

**Integration & external dependencies**
- MySQL is the primary DB; local development can point to `localhost` or containerized MySQL. DB credentials come from `env/.env`.
- The repo uses `python-dotenv` to load `env/.env` (see `load_dotenv(Path(BASE_DIR) / 'env/.env')`).
- Static hosting and reverse proxies may use the `ALLOWED_HOSTS` list in `settings.py` — several ngrok/trycloudflare hosts appear there for dev.

**Testing notes & how to run targeted checks**
- Run full Django test suite: `python RMRS/manage.py test`.
- There is a DB-related script `database/test_database.py` you can run directly for DB helpers: `python database/test_database.py` (or `pytest database/test_database.py` if `pytest` is installed).
- Model edits must be followed by `python RMRS/manage.py makemigrations` and `python RMRS/manage.py migrate` before pushing or testing other features.
- Any new method or function needs corresponding tests (e.g., update the relevant `tests.py` under each app or add a focused test module) so CI coverage stays meaningful.

**When editing code, watch for**
- Timezone handling — `USE_TZ = False` means code assumes local datetimes.
- DB connection: many utilities expect a MySQL DB; tests and recommendation scripts can assume schema from `database/schema.sql` or Django migrations.
- Sensitive data: `.env` contains DB credentials — never commit secrets. Use `env/.env` locally and document required keys in PRs.

**Helpful file references / examples**
- Main Django settings: `RMRS/RMRS/settings.py`
- App logic and endpoints: `UserSideApp/views/`, `MerchantSideApp/views/`, `RecommendationSystem/views/`
- Business logic: `UserSideApp/services.py`, `database/recommendation_engine.py`
- DB helpers: `database/db_manager.py`, `database/cli.py`

**PR & agent behaviour guidance**
- Keep changes minimal and focused: update migrations (`makemigrations` + `migrate`) and tests alongside any model or DB behavior change.
- If altering env keys or new config is needed, describe the change and required `env/.env` keys in the PR description.
- Prefer modifying service-layer functions (`services.py`) over embedding complex logic in views.

If anything important is missing, tell me what area to expand (e.g., more examples from `UserSideApp`, DB seeding steps, or testing matrix). Thanks — ready to iterate on this draft.
