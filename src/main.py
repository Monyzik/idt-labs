from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.api import health, todo
from src.config import STATIC_DIR
from src.database.database_manager import engine
from src.database.models import Base
import os

api_router = APIRouter()

api_router.include_router(todo.router, prefix="/todos", tags=["todos"])
api_router.include_router(health.router, prefix="/health", tags=["health"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Запуск приложения...")
    try:
        # Создаем таблицы при запуске приложения
        Base.metadata.create_all(bind=engine)
        print("Таблицы базы данных созданы/проверены")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
    yield
    print("Остановка приложения...")


app = FastAPI(lifespan=lifespan)  # Используем lifespan manager

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

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
