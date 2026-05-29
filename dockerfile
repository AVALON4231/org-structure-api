FROM python:3.11-slim

WORKDIR /app

# Установка netcat для ожидания доступности БД
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY app/ app/
COPY alembic.ini .
COPY migrations/ migrations/
COPY tests/ tests/

RUN pip install --no-cache-dir .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]