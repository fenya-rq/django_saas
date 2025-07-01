## Project structure
```
django_saas/
├── src/
│ ├── core/
│ │ ├── ...
│ │ ├── .env
│ │ ├── .env.example
│ │ └── settings.py
│ ├── tests/
│ │ └── contact_tests.py
│ ├── Dockerfile
│ ├── entrypoint.sh
│ └── manage.py
├── infra/
│ ├── nginx/
│ │ └── default.conf
│ └── postgressql/
│   └── Dockerfile
├── tests/
│ └── __init__.py
├── .env
├── .env.example
├── .dockerignore
├── .gitignore
├── docker-compose.yaml
├── poetry.lock
├── pyproject.toml
└── README.md
```