.PHONY: up down build test migrate logs shell

# Запуск приложения (фоновый режим)
up:
	docker-compose up -d

# Остановка
down:
	docker-compose down

# Сборка образов
build:
	docker-compose build

# Применение миграций (внутри работающего контейнера)
migrate:
	docker-compose exec app alembic upgrade head

# Запуск тестов (через docker-compose exec)
test:
	docker-compose exec app pytest

# Просмотр логов
logs:
	docker-compose logs -f app

# Интерактивная оболочка в контейнере приложения
shell:
	docker-compose exec app bash