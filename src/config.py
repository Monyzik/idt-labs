import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL")
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = os.path.join(BASE_DIR, "static")
APP_NAME: str = os.getenv("APP_NAME", "todo-api")
APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
APP_ENVIRONMENT: str = os.getenv("APP_ENVIRONMENT", "production")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
SENTRY_DSN: str | None = os.getenv("SENTRY_DSN")
SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
OTEL_EXPORTER_OTLP_ENDPOINT: str | None = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
