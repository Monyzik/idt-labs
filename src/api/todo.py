from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.database_manager import get_db
from src.todo import TodoCRUD
from src.todo import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoStats
)

router = APIRouter(tags=["todos"])


@router.get("/", response_model=List[TodoResponse])
async def get_todos(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Получить все задачи"""
    crud = TodoCRUD(db)
    todos = crud.get_all(skip=skip, limit=limit)
    return todos


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
        todo: TodoCreate,
        db: Session = Depends(get_db)
):
    """Создать новую задачу"""
    crud = TodoCRUD(db)
    return crud.create(todo)


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
        todo_id: int,
        todo_update: TodoUpdate,
        db: Session = Depends(get_db)
):
    crud = TodoCRUD(db)
    updated_todo = crud.update(todo_id, todo_update)

    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    return updated_todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
        todo_id: int,
        db: Session = Depends(get_db)
):
    crud = TodoCRUD(db)
    success = crud.delete(todo_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )


@router.get("/stats", response_model=TodoStats)
async def get_todos_stats(db: Session = Depends(get_db)):
    crud = TodoCRUD(db)
    return crud.get_stats()
