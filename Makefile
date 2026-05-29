.PHONY: up down build test migrate logs shell

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

migrate:
	docker-compose exec app alembic upgrade head

test:
	docker-compose exec app pytest

logs:
	docker-compose logs -f app

shell:
	docker-compose exec app bash