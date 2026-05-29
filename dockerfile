FROM python:3.11-slim

WORKDIR /app

# Копируем файлы проекта
COPY pyproject.toml .
COPY app/ app/
COPY alembic.ini .
COPY migrations/ migrations/
COPY tests/ tests/

# Устанавливаем зависимости
RUN pip install --no-cache-dir .

# При dev-зависимостях (для тестов) можно отдельно установить опциональные
# RUN pip install --no-cache-dir ".[dev]"
# Но чтобы образ был легче, оставим только production-зависимости.

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]