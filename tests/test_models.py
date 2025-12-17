import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.database.models import Todo, Base


@pytest.fixture
def in_memory_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


class TestTodoModel:

    def test_create_todo(self, in_memory_db):
        todo = Todo(text="Test todo")

        in_memory_db.add(todo)
        in_memory_db.commit()
        in_memory_db.refresh(todo)

        assert todo.id is not None
        assert todo.text == "Test todo"
        assert todo.completed is False
        assert isinstance(todo.created_at, datetime)
        assert todo.updated_at is None

    def test_todo_repr(self, in_memory_db):
        todo = Todo(text="This is a very long todo item that should be truncated")
        in_memory_db.add(todo)
        in_memory_db.commit()
        in_memory_db.refresh(todo)

        repr_str = repr(todo)
        assert f"id={todo.id}" in repr_str
        assert "text='This is a very long ...'" in repr_str

    def test_todo_without_text(self, in_memory_db):
        todo = Todo()

        in_memory_db.add(todo)
        with pytest.raises(IntegrityError):
            in_memory_db.commit()

    def test_update_todo_timestamp(self, in_memory_db):
        todo = Todo(text="Original text")
        in_memory_db.add(todo)
        in_memory_db.commit()
        in_memory_db.refresh(todo)

        original_updated_at = todo.updated_at

        todo.text = "Updated text"
        in_memory_db.commit()
        in_memory_db.refresh(todo)

        assert todo.updated_at is not None
        if original_updated_at is not None:
            assert todo.updated_at != original_updated_at
