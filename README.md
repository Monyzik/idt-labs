# Лабораторная работа №4

## Легкий todo сайт на FastApi

**Для начала работы в корне проекта необходимо создать файл *.env*,
пример его содержания:**

```dotenv
POSTGRES_DB=todo_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=password
DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"
```

#### Сборка и запуск сервиса

```shell
docker-compose up --build
```

Сервис открывается по адресу: 0.0.0.0:8000

PgAdmin открывается по адресу: 0.0.0.0:8080

#### Просмотр логов

```shell
docker-compose logs
```

#### Остановка приложения

```shell
docker-compose down
```