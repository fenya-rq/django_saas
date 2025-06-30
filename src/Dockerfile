FROM python:3.13.5-slim

# Making container logs displayable and Do not attempt to create .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Creating working directory
WORKDIR /usr/src/app

COPY ../poetry.lock ../pyproject.toml ../src ./

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=2.1.3
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION
# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root

EXPOSE 8000

CMD ["sh", "/usr/src/app/entrypoint.sh"]