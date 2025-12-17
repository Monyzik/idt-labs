from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Todo(id={self.id}, text='{self.text[:20]}...')>"
