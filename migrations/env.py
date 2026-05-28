import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine
from alembic import context

# Добавляем корень проекта в sys.path для импорта моделей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base
from app.models import Department, Employee  # обязательно импортируем модели

config = context.config

# Логирование из alembic.ini
fileConfig(config.config_file_name)

# Метаданные для автогенерации миграций
target_metadata = Base.metadata


def run_migrations_offline():
    """Миграция в оффлайн-режиме (без подключения к БД)."""
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Миграция в онлайн-режиме (с живым подключением)."""
    # Берём URL из переменной окружения, если она задана, иначе из alembic.ini
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()