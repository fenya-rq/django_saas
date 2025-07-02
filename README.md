## Project structure
```
django_saas/
├── infra/
│ ├── nginx/
│ │ └── default.conf
│ └── postgressql/
│   └── Dockerfile
├── src/
│ ├── contacnts/
│ │ └── ...
│ ├── core/
│ │ ├── ...
│ │ ├── .env
│ │ ├── .env.example
│ │ └── settings.py
│ ├── tenants/
│ │ └── ...
│ ├── tests/
│ │ └── contact_tests.py
│ ├── users/
│ │ └── ...
│ ├── Dockerfile
│ ├── entrypoint.sh
│ └── manage.py
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