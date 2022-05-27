# Test task with FastAPI, aioredis, aiopg

# Тестовое задание (стек fastapi, aioredis, aiopg, sqlalchemy)

Тестовое приложение должно подключатся к PostgreSQL и Redis и реализовать
следующие API:

1. Проверка анаграммы - принимает две строки, определяет являются ли они анаграммами. Если являются - необходимо увеличить счетчик в Redis. Возвращает JSON - являются ли они анаграммами и счетчик из Redis.

Эндпойнт /check/ принимает GETзапрос вида check?str_1=qwerty&str_2=ytrewq возвращает JSON.

2. Занести в базу данных 10 устройств (таблица devices), тип (dev_type) определяется случайно из списка: emeter, zigbee, lora, gsm. Поле dev_id - случайные 48 бит в hex-формате (MAC-адрес). К пяти устройствам из добавленных необходимо привязать endpoint (таблица endpoints). После записи необходимо возвращать HTTP код состояния 201.

При старте сервера автоматически создается и заполнятеся база - 10 устройств (devices), 5 эндпойнтов (endpoints). Кроме того доступны эндпойнты для ручного заполнения/исправления бд.

4. В базе данных получить список всех устройств, которые не привязаны к endpoint. Вернуть количество, сгруппированное по типам устройств.

GET запрос к /devices/select/ выдает JSON, согласно заданию


Клонирование проекта:

`git clone git@github.com:z00k0/fastapi_test_task.git`

Для запуска проекта необходимо создать файл `.env`
Содержимое файла:
```
REDIS_PASSWORD=Q1w2e3r4
POSTGRES_DB=fastapi_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=db_password
POSTGRES_SERVER=postgres
LOGGING_LEVEL=WARN
```
Запуск проетка

`docker-compose build`

`docker-compose up -d`

Приложение доступно по адресу [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
