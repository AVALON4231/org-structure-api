# Organizational Structure API

Тестовое задание: REST API для управления оргструктурой (отделы и сотрудники) на FastAPI.

## Запуск
1. Клонируйте репозиторий.
2. Запустите `docker-compose up --build`.
3. Сервис доступен на `http://localhost:8000`.
4. Swagger UI: `http://localhost:8000/docs`.

## Переменные окружения (при необходимости)
- `DATABASE_URL` – строка подключения к PostgreSQL.

## API
- `POST /departments/` – создать отдел
- `POST /departments/{id}/employees/` – создать сотрудника
- `GET /departments/{id}` – детали отдела (дерево, сотрудники)
- `PATCH /departments/{id}` – изменить отдел (имя, родитель)
- `DELETE /departments/{id}?mode=cascade|reassign&reassign_to_department_id=...` – удалить отдел

## Тесты
```bash
pip install -r requirements.txt
pytest