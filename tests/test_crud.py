from src.todo import TodoCRUD, TodoCreate, TodoUpdate


class TestTodoCRUDSimple:

    def test_create_todo(self, db_session):
        crud = TodoCRUD(db_session)
        todo_data = TodoCreate(text="Test todo")
        todo = crud.create(todo_data)

        assert todo.id is not None
        assert todo.text == "Test todo"
        assert todo.completed is False

    def test_get_all_todos(self, db_session):
        crud = TodoCRUD(db_session)

        for i in range(3):
            todo_data = TodoCreate(text=f"Todo {i}")
            crud.create(todo_data)

        todos = crud.get_all()
        assert len(todos) == 3

    def test_get_by_id(self, db_session):
        crud = TodoCRUD(db_session)

        todo_data = TodoCreate(text="Test todo")
        created_todo = crud.create(todo_data)

        found_todo = crud.get_by_id(created_todo.id)
        assert found_todo is not None
        assert found_todo.id == created_todo.id

    def test_update_todo(self, db_session):
        crud = TodoCRUD(db_session)

        todo_data = TodoCreate(text="Original text")
        todo = crud.create(todo_data)

        update_data = TodoUpdate(text="Updated text", completed=True)
        updated_todo = crud.update(todo.id, update_data)

        assert updated_todo is not None
        assert updated_todo.text == "Updated text"
        assert updated_todo.completed is True

    def test_delete_todo(self, db_session):
        crud = TodoCRUD(db_session)

        todo_data = TodoCreate(text="To be deleted")
        todo = crud.create(todo_data)

        result = crud.delete(todo.id)
        assert result is True

        deleted_todo = crud.get_by_id(todo.id)
        assert deleted_todo is None

    def test_get_stats(self, db_session):
        crud = TodoCRUD(db_session)

        todo1 = TodoCreate(text="Todo 1")
        todo2 = TodoCreate(text="Todo 2")
        todo3 = TodoCreate(text="Todo 3")

        crud.create(todo1)
        crud.create(todo2)
        created = crud.create(todo3)

        crud.update(created.id, TodoUpdate(completed=True))

        stats = crud.get_stats()

        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["pending"] == 2
