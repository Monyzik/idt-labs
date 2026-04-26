from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.database.models import Todo


class TodoBase(BaseModel):
    text: str


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None


class TodoInDB(TodoBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TodoResponse(TodoInDB):
    pass


class TodoStats(BaseModel):
    total: int
    completed: int
    pending: int


class TodoCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[type[Todo]]:
        return self.db.query(Todo) \
            .order_by(desc(Todo.created_at)) \
            .offset(skip) \
            .limit(limit) \
            .all()

    def get_by_id(self, todo_id: int) -> type[Todo] | None:
        return self.db.query(Todo).filter(Todo.id == todo_id).first()

    def create(self, todo_in: TodoCreate) -> Todo:
        todo = Todo(**todo_in.dict())
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def update(self, todo_id: int, todo_in: TodoUpdate) -> Optional[Todo]:
        todo = self.get_by_id(todo_id)
        if not todo:
            return None

        update_data = todo_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)

        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, todo_id: int) -> bool:
        todo = self.get_by_id(todo_id)
        if not todo:
            return False

        self.db.delete(todo)
        self.db.commit()
        return True

    def get_stats(self) -> dict:
        total = self.db.query(Todo).count()
        completed = self.db.query(Todo).filter(Todo.completed == True).count()
        pending = total - completed

        return {
            "total": total,
            "completed": completed,
            "pending": pending
        }
