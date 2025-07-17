### Task Description:

**Backend‑разработчик SaaS CRM** (schema‑based мультиарендность)

---
### 1. ТЗ в одном абзаце
> Сделайте сервис **Contacts** для SaaS‑CRM: каждая организация (арендатор) живёт в собственной схеме PostgreSQL. По REST API можно создавать, читать, обновлять и удалять контакты **только** внутри активной схемы. Смена арендатора идёт по HTTP‑заголовку X-SCHEMA. Добавьте unit‑тесты, минимальный CI, оформите в Docker‑образ или опишите локальный запуск.
---
### 2. Стек и ограничения

| Обязательно | Версия | Комментарий |
|----|----|----|
| Python | 3.11+ | venv/poetry на ваше усмотрение |
| Django Ninja | ≥ 1.4.3 | Или DRF 3.15+ |
| PostgreSQL | 14+ | Локально допускается Docker‑контейнер |
| Мультиарендность | schema‑based | Использовать django‑tenants **или** django‑pgschemas **или** кастомную middleware, но каждая схема: contact_<schema> |
| Тесты | pytest | Coverage ≥ 80 % по models/views |
| CI | GitHub Actions | Шаги: pytest, flake8, bandit |
---
## 3. Функциональные требования

### 3.1 Модель
* id  UUID (PK)
* name  str, required
* email str, unique внутри схемы
* phone str, optional
* date_created  auto‑now

### 3.2 Мультиарендность
* При старте создаётся **public** схема с моделью Tenant (*schema_name*, *name*).
* CLI‑команда python manage.py create_tenant <schema> <name> генерирует схему и применяет миграции.
* Каждый HTTP‑запрос должен включать заголовок X-SCHEMA: <schema_name>.
* Middleware переключает search_path до выполнения view.
* Если схема не найдена → 404 TENANT_NOT_FOUND.

### 3.3 API (Django Ninja)
| Метод | URI | Описание | Код |
|----|----|----|----|
| POST | /contacts | Создать контакт | 201 |
| GET | /contacts | Список (optional paginate) | 200 |
| GET | /contacts/{id} | Получить | 200 |
| PUT | /contacts/{id} | Обновить | 200 |
| DELETE | /contacts/{id} | Удалить | 204 |

### 3.4 Тесты
1. Создание 2 арендаторов, по 1 контакту в каждом, запросы перекрёстно → возвращают 404.
2. Запрос без X-SCHEMA → 400.
3. Email уникален **внутри** схемы, но может повторяться в другой.
___
### <p align="center">Start instruction</p>
Pre-requests: docker latest version

1. `git clone https://github.com/fenya-rq/django_saas.git`
2. `cp .env.example .env; cp src/core/.env.example src/core/.env`
3. Adjust your .env files to your credentials
4. Run project from django_saas directory `docker compose up -d`