from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.config import APP_ENVIRONMENT, APP_VERSION
from src.database.database_manager import get_db
from src.todo import TodoCRUD

router = APIRouter(tags=["health"])


@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    try:
        crud = TodoCRUD(db)
        crud.get_stats()

        return {
            "status": "healthy",
            "database": "connected",
            "version": APP_VERSION,
            "environment": APP_ENVIRONMENT
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/live")
async def liveness_probe():
    return {"status": "alive"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_probe(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "database": "connected",
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
    }


@router.get("/startup")
async def startup_probe():
    return {"status": "started"}
