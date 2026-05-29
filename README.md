```markdown
# Organizational Structure API

REST API для управления оргструктурой компании: подразделения и сотрудники.  

---

# Чистая архитектура

Реализация тестового задания с полным разделением слоёв:
- **Роутер** – только транспорт, делегирует контроллеру.
- **Контроллер** – вызывает сервисы и формирует HTTP-ответ.
- **Сервис** – бизнес-логика, работает с DTO.
- **Репозиторий** – доступ к БД, возвращает ORM-модели.
- **Валидаторы** – изолированные проверки входящих данных.
- **DTO** – отдельные объекты для передачи между сервисами и контроллерами (одна таблица – один DTO).

---

## 🛠️ Стек

- Python 3.11
- FastAPI
- SQLAlchemy 2.0 (ORM)
- PostgreSQL 14
- Alembic (миграции)
- Pydantic
- Docker / Docker Compose
- pytest

---

## 📦 Зависимости

Управление через `pyproject.toml` (PEP 621). Production‑зависимости:

- `fastapi`
- `uvicorn[standard]`
- `sqlalchemy`
- `psycopg2-binary`
- `alembic`
- `pydantic`

Dev‑зависимости (`pytest`, `httpx`) опциональны.

---

## 🚀 Быстрый старт

### Предварительные требования
- Установленный [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/your-username/org-structure-api.git
cd org-structure-api
```

### 2. Запуск приложения

**Linux / macOS:**
```bash
make up
```
**Windows (CMD / PowerShell):**
```cmd
docker-compose up -d
```

При первом запуске автоматически:
- соберётся образ приложения
- выполнятся миграции Alembic (`alembic upgrade head`)
- поднимется сервер на порту 8000

### 3. Проверка
Откройте в браузере [http://localhost:8000/docs](http://localhost:8000/docs) — интерактивная документация Swagger UI.

---

## 📋 Основные команды

### Linux / macOS (через Makefile)
| Команда        | Описание                           |
|----------------|------------------------------------|
| `make up`      | Запуск в фоновом режиме            |
| `make down`    | Остановка и удаление контейнеров   |
| `make logs`    | Просмотр логов приложения          |
| `make migrate` | Применить миграции внутри контейнера |
| `make test`    | Запустить тесты                    |
| `make build`   | Пересобрать образы                 |
| `make shell`   | Открыть bash в контейнере приложения |

### Windows (CMD / PowerShell)
Замените `make ...` прямыми командами Docker Compose:

| Действие                 | Команда                                  |
|--------------------------|------------------------------------------|
| Запуск                   | `docker-compose up -d`                   |
| Остановка                | `docker-compose down`                    |
| Логи                     | `docker-compose logs -f app`             |
| Миграции                 | `docker-compose exec app alembic upgrade head` |
| Тесты                    | `docker-compose exec app pytest`         |
| Пересборка образов       | `docker-compose build`                   |
| Оболочка в контейнере    | `docker-compose exec app bash`           |

---

## 📡 API Endpoints

### Подразделения

| Метод   | Путь                  | Описание |
|---------|-----------------------|----------|
| `POST`  | `/departments/`       | Создать подразделение |
| `GET`   | `/departments/{id}`   | Получить подразделение (с деревом и сотрудниками) |
| `PATCH` | `/departments/{id}`   | Обновить имя/родителя |
| `DELETE`| `/departments/{id}`   | Удалить (`cascade` или `reassign`) |

### Сотрудники

| Метод   | Путь                              | Описание |
|---------|-----------------------------------|----------|
| `POST`  | `/departments/{id}/employees/`   | Добавить сотрудника в подразделение |

Подробные схемы запросов и ответов доступны в Swagger UI после запуска.

---

## ✅ Тестирование

Тесты используют временную тестовую базу PostgreSQL. Запуск:

**Linux / macOS:**
```bash
make test
```
**Windows:**
```cmd
docker-compose exec app pytest
```

Для локального запуска тестов вне Docker потребуется:
- запущенный PostgreSQL с тестовой БД (см. `tests/conftest.py`)
- установленные dev‑зависимости: `pip install ".[dev]"`

---

## 📁 Структура проекта

```
org-structure-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Точка входа FastAPI
│   ├── database.py                # Подключение к БД
│   ├── models.py                  # SQLAlchemy модели
│   ├── api/
│   │   ├── router.py              # Маршруты (транспортный слой)
│   │   └── schemas.py             # Pydantic-схемы запросов/ответов
│   ├── controllers/               # Контроллеры (обработка HTTP запросов)
│   │   ├── department_controller.py
│   │   └── employee_controller.py
│   ├── services/                  # Бизнес-логика
│   │   ├── department_service.py
│   │   └── employee_service.py
│   ├── repositories/              # Доступ к данным (ORM)
│   │   ├── department_repo.py
│   │   └── employee_repo.py
│   ├── validators/                # Валидация входных данных
│   │   ├── department_validator.py
│   │   └── employee_validator.py
│   └── dto/                       # Data Transfer Objects (внутренние объекты)
│       ├── department.py
│       └── employee.py
├── migrations/                    # Alembic миграции
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── pyproject.toml                 # Зависимости
├── Dockerfile
├── docker-compose.yml
├── Makefile                       # Удобные команды для Linux/macOS
└── README.md
```

---

## 🔒 Валидация и бизнес-правила

- Название отдела: уникально в пределах родительского, длина 1..200, автоматический тримминг пробелов.
- Имя сотрудника и должность: непустые, ≤200 символов, тримминг.
- Запрет создания сотрудника в несуществующем отделе → `404`.
- Запрет перемещения отдела в своё поддерево (цикл) → `409 Conflict`.
- Каскадное удаление подразделений и сотрудников через БД (ondelete CASCADE).
- При режиме `reassign` сотрудники переводятся в указанный отдел, а удаляемое подразделение и его поддерево удаляются.

---

## ⚠️ Примечания для разработчиков

- Для применения новых миграций после изменения моделей используйте `docker-compose exec app alembic revision --autogenerate -m "описание"`.
- При добавлении новых методов API соблюдайте разделение слоёв: маршрут → контроллер → сервис → репозиторий.
- Тесты должны быть независимы и использовать собственную тестовую БД.

---

## 📄 Лицензия

MIT
```