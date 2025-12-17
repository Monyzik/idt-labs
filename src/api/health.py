from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.database_manager import get_db_session
from src.todo import TodoCRUD

router = APIRouter(tags=["health"])


@router.get("/")
async def health_check(db: Session = Depends(get_db_session)):
    try:
        crud = TodoCRUD(db)
        stats = crud.get_stats()

        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0",
            "environment": "production"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }