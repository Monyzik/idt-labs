# Лабораторная работа №5

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
APP_NAME=todo-api
APP_VERSION=1.0.0
APP_ENVIRONMENT=production
LOG_LEVEL=INFO
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.1
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:14318/v1/traces
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

## Observability

Приложение теперь отдает:

- `/metrics` для Prometheus
- `/api/health/` для backward-compatible health check
- `/api/health/live`
- `/api/health/ready`
- `/api/health/startup`

Локальный стек наблюдаемости запускается отдельно:

```shell
cd todo-observability
docker compose up -d
```

Доступные сервисы:

- Prometheus: `http://localhost:19090`
- Grafana: `http://localhost:13001` (`admin` / `admin`)
- Tempo: `http://localhost:13200`
- OTLP HTTP ingest: `http://localhost:14318/v1/traces`

Grafana автоматически подхватывает datasource и базовый dashboard `Todo API Observability`.

#### Остановка приложения

```shell
docker-compose down
```
