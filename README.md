# SkillFactory API project


Репозиторий с RESTful интерфейсом на базе FastAPI для обработки данных о горных перевалах. Разработан в рамках курса "Профессия Python-разработчик" для итоговой виртуальной стажировки.


## Используемые технологии

* Python
* PostgreSQL - база данных
* psycopg2 - драйвер базы данных
* FastApi - фреймворк
* Pydantic - валидация данных, модели
* Pytest - тестирование функционала


## Установка (Win)

1. Клонирование репозитория:

```bash
git clone https://github.com/btrddd/SprintAPI.git
cd SprintApi
```

2. Виртуальное окружение:

```bash
python.exe -m venv venv
venv\\Scripts\\activate
```

3. Зависимости:

```bash
python.exe -m pip install -r requirements.txt
```

4. Создайте базу данных PostgreSQL и выполните SQL скрипт dump.sql для создания таблиц
5. Переменные окружения:
Создайте файл .env в корне проекта на основе .env.example:

```bash
cp .env.example .env
```

Отредактируйте файл с вашими настройками:

* FSTR_DB_NAME - имя базы данных
* FSTR_DB_LOGIN - логин
* FSTR_DB_PASS - пароль
* FSTR_DB_HOST - хост
* FSTR_DB_PORT - порт


## Использование

### Запуск сервера

```bash
uvicorn src.main:app --reload # Для разработки
uvicorn src.main:app --host 0.0.0.0 --port 8000 # Для продакшена
```

### Использование API

1. POST /submitData - Создание новой записи в БД о перевале (Коды 200, 422, 500)

Пример Curl запроса:

```Curl
curl -X 'POST'   
    'http://localhost:8000/submitData'   
    -H 'accept: application/json'   
    -H 'Content-Type: application/json'   
    -d '{
    "beauty\_title": "Some beauty title",
    "title": "Some common title",
    "other\_titles": "Some other titles",
    "connect": "some connection",
    "add\_time": "2026-07-01 12:00:00",
    "user": {
        "email": "testemail@domain.com",
        "fam": "Surname",
        "name": "Firstname",
        "otc": "Patronymic",
        "phone": "+7 999 999 99 99"
    },
    "coords": {
        "latitude": "99.123",
        "longitude": "123.12321",
        "height": "5544"
    },
        "level": {
        "winter": "1A",
        "autumn": "5B",
        "spring": "2A"
    },
    "images": \[
        {
            "data": "some image",
            "title": "some image title"
        }
    ]
}'
```

Успешный ответ (200):

```json
{
    "status": 200,
    "message": null,
    "id": 13
}
```


2. GET /submitData/{id} - Получение данных о перевале по его id (Коды 200, 404, 500)

Пример Curl запроса:

```Curl
curl -X 'GET' \
    'http://localhost:8000/submitData/11' \
    -H 'accept: application/json'
```

Успешный ответ (200):
```json
{
    "id": 11,
    "beauty_title": "new title value",
    "title": "new_title",
    ...
}
```


3. PATCH /submitData/{id} - Частичное обновление данных перевала по его id (Коды 200, 400, 404, 500)

Пример Curl запроса:
```Curl
curl -X 'PATCH' \
    'http://localhost:8000/submitData/11' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "beauty_title": "new beauty title",
    "title": "new title"
}'
```

Успешный ответ (200):
```json
{
    "state": 1,
    "message": null
}
```


4. GET /submitData/?user_email={email} - Список перевалов, созданных пользователем (Коды 200, 404, 500)

Пример Curl запроса:
```Curl
curl -X 'GET' \
    'http://localhost:8000/submitData/?user_email=qwerty123%40mail.ru' \
    -H 'accept: application/json'
```

Успешный ответ (200):
```json
{
    "1": {
        "id": 12,
        "beauty_title": "пер. ",
        "title": "Пхия",
        ...
    },
    "2": {
        "id": 11,
        "beauty_title": "new title value",
        "title": "new_title",
        ...
    }
}
```


## Структура проекта

* 'main.py': Точка входа приложения
* 'exceptions.py': Кастомные исключения
* '/api/routes.py': Эндпоинты API
* '/db/db_worker.py': Работа с базой данных
* '/models/': Модели Pydantic
* '/tests/': Тесты Pytest


## Документация

После запуска сервера документация будет доступна по адресам:

* Swagger UI: http://your_host:8000/docs
* ReDoc: http://your_host:8000/redoc


## Тестирование

```bash
pytest # Запуск тестов
pytest -v # Запуск с подробным выводом
pytest tests/test_routes.py # Запуск тестов конкретного модуля
```


## Лицензия

Проект распространяется под лицензией MIT.
