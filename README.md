Project Context Summary:

- Stack & Versions:
  * Python 3.13.5
  * Django 5.1
  * django-tenants 3.8.0 (schema-based multitenancy)
  * django-ninja 1.4.3 (REST API)
  * PostgreSQL 14+ via Docker Compose
  * Ubuntu 24.04 LTS
  * Gunicorn + Uvicorn
  * Docker + Docker Compose
  * Testing: pytest, pytest-django
  * Linters: flake8, bandit, ruff
  * Env vars via .env

- Project Structure (key parts):
  django_saas/
    ├── infra/
    ├── src/
    │   ├── contacts/
    │   ├── core/
    │   ├── tenants/
    │   ├── tests/
    │   ├── users/
    │   ├── Dockerfile
    │   ├── entrypoint.sh
    │   └── manage.py
    ├── tests/
    ├── docker-compose.yaml
    ├── pyproject.toml
    ├── .env
    └── README.md

- Important notes:
  * Tenants are separate PostgreSQL schemas named contact_<schema>
  * Tenant switching via X-SCHEMA HTTP header and middleware
  * Postgres runs as Docker service named 'db'
  * Django connects using PGHOST=db environment variable
  * Tests run inside Docker container or locally with proper env
  * pytest-django configured with DJANGO_SETTINGS_MODULE=core.settings
  * Database test config inside default DB settings TEST dict
  * Use black or ruff --fix to auto-format code

---

Local Running Instructions:

1. Prerequisites:
   - Docker and Docker Compose installed
   - Python 3.13.5 installed locally (optional if running only in Docker)
   - Create a `.env` file with:
     PGDATABASE=django_saas_contacts_dev
     PGUSER=test_user
     POSTGRES_PASSWORD=test_password
     PG_HOST=db
     PG_PORT=5432

2. Start PostgreSQL service:
   docker-compose up -d db

3. Build Django app image:
   docker-compose build core

4. Run Django shell or container:
   docker-compose run --rm core sh
   OR
   docker-compose up -d

5. Apply database migrations:
   poetry run python src/manage.py migrate

6. Run tests (inside container or locally with env):
   poetry run pytest src/tests/
   OR
   docker-compose run --rm core poetry run pytest src/tests/

7. Run linters:
   poetry run flake8 src tests
   poetry run bandit -r src tests

8. Autoformat code:
   poetry run black --line-length 100 src tests
   OR
   poetry run ruff --fix src tests

9. Access app at:
   http://localhost:8000/
   Remember to send X-SCHEMA header with requests

Notes:
- Inside Docker, PGHOST must be 'db' to reach Postgres container
- Locally, PGHOST can be 'localhost' if Postgres runs locally
- Use docker-compose logs and exec commands for troubleshooting
- Run your tenant creation management commands before testing multi-tenancy

---

If needed, I can help prepare automation scripts or Docker Compose examples.
