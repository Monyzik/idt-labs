# tests/test_schemas.py
import pytest
from datetime import datetime
from pydantic import ValidationError

from src.todo import TodoCreate, TodoUpdate, TodoResponse, TodoStats


class TestTodoSchemas:

    def test_todo_create_valid(self):
        todo = TodoCreate(text="Valid todo")
        assert todo.text == "Valid todo"

    def test_todo_create_invalid(self):
        with pytest.raises(ValidationError):
            TodoCreate()

    def test_todo_update_partial(self):
        todo = TodoUpdate(completed=True)
        assert todo.completed is True
        assert todo.text is None

        todo = TodoUpdate(text="New text")
        assert todo.text == "New text"
        assert todo.completed is None

        todo = TodoUpdate(text="New text", completed=False)
        assert todo.text == "New text"
        assert todo.completed is False

    def test_todo_update_empty(self):
        todo = TodoUpdate()
        assert todo.text is None
        assert todo.completed is None

    def test_todo_response_valid(self):
        now = datetime.now()
        todo = TodoResponse(
            id=1,
            text="Test todo",
            completed=False,
            created_at=now,
            updated_at=now
        )

        assert todo.id == 1
        assert todo.text == "Test todo"
        assert todo.completed is False
        assert todo.created_at == now
        assert todo.updated_at == now

    def test_todo_stats_valid(self):
        stats = TodoStats(total=10, completed=3, pending=7)
        assert stats.total == 10
        assert stats.completed == 3
        assert stats.pending == 7
