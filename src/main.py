from contextlib import asynccontextmanager
import os

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api import health, todo
from src.config import (
    APP_ENVIRONMENT,
    APP_NAME,
    APP_VERSION,
    LOG_LEVEL,
    OTEL_EXPORTER_OTLP_ENDPOINT,
    SENTRY_DSN,
    SENTRY_TRACES_SAMPLE_RATE,
    STATIC_DIR,
)
from src.database.database_manager import engine
from src.database.models import Base
from src.observability import (
    ObservabilityMiddleware,
    configure_logging,
    configure_sentry,
    configure_tracing,
    get_logger,
    metrics_router,
    setup_database_metrics,
)

api_router = APIRouter()
logger = get_logger(__name__)

api_router.include_router(todo.router, prefix="/todos", tags=["todos"])
api_router.include_router(health.router, prefix="/health", tags=["health"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema verified")
    except Exception as e:
        logger.exception("Database schema verification failed")
    yield
    logger.info("Application shutdown completed")


configure_logging(LOG_LEVEL)
configure_sentry(
    dsn=SENTRY_DSN,
    environment=APP_ENVIRONMENT,
    release=APP_VERSION,
    traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
)
setup_database_metrics(engine)

app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)
app.add_middleware(ObservabilityMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(metrics_router)
configure_tracing(APP_NAME, OTEL_EXPORTER_OTLP_ENDPOINT, app=app, engine=engine)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def read_index():
    if os.path.exists(STATIC_DIR):
        return FileResponse(f"{STATIC_DIR}/index.html")
    return {"message": "Static files not found"}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
