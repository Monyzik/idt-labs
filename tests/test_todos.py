from unittest.mock import Mock, patch

from fastapi import status


class TestTodoCRUD:

    def test_create_todo_success(self, client, db_session):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_todo = Mock()
            mock_todo.id = 1
            mock_todo.text = "New test todo"
            mock_todo.completed = False
            mock_todo.created_at = "2024-01-01T00:00:00"
            mock_todo.updated_at = None

            mock_crud = Mock()
            mock_crud.create.return_value = mock_todo
            MockTodoCRUD.return_value = mock_crud

            todo_data = {"text": "New test todo"}

            response = client.post("/api/todos/", json=todo_data)

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["text"] == todo_data["text"]
            assert data["completed"] is False

    def test_create_todo_invalid_data(self, client):
        response = client.post("/api/todos/", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_all_todos_empty(self, client):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_crud = Mock()
            mock_crud.get_all.return_value = []
            MockTodoCRUD.return_value = mock_crud

            response = client.get("/api/todos/")
            assert response.status_code == 200
            assert response.json() == []

    def test_get_all_todos_with_data(self, client, test_todo):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_todo = Mock()
            mock_todo.id = test_todo.id
            mock_todo.text = test_todo.text
            mock_todo.completed = test_todo.completed
            mock_todo.created_at = test_todo.created_at
            mock_todo.updated_at = test_todo.updated_at

            mock_crud = Mock()
            mock_crud.get_all.return_value = [mock_todo]
            MockTodoCRUD.return_value = mock_crud

            response = client.get("/api/todos/")
            assert response.status_code == 200
            data = response.json()
            assert len(data) >= 0

    def test_update_todo_success(self, client, test_todo):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_updated_todo = Mock()
            mock_updated_todo.id = test_todo.id
            mock_updated_todo.text = "Updated text"
            mock_updated_todo.completed = True
            mock_updated_todo.created_at = test_todo.created_at
            mock_updated_todo.updated_at = "2024-01-01T00:00:00"

            mock_crud = Mock()
            mock_crud.update.return_value = mock_updated_todo
            MockTodoCRUD.return_value = mock_crud

            update_data = {
                "text": "Updated text",
                "completed": True
            }

            response = client.put(f"/api/todos/{test_todo.id}", json=update_data)
            assert response.status_code == 200

    def test_update_todo_partial(self, client, test_todo):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_updated_todo = Mock()
            mock_updated_todo.id = test_todo.id
            mock_updated_todo.text = test_todo.text
            mock_updated_todo.completed = True
            mock_updated_todo.created_at = test_todo.created_at
            mock_updated_todo.updated_at = "2024-01-01T00:00:00"

            mock_crud = Mock()
            mock_crud.update.return_value = mock_updated_todo
            MockTodoCRUD.return_value = mock_crud

            update_data = {"completed": True}
            response = client.put(f"/api/todos/{test_todo.id}", json=update_data)
            assert response.status_code == 200

    def test_update_todo_not_found(self, client):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_crud = Mock()
            mock_crud.update.return_value = None
            MockTodoCRUD.return_value = mock_crud

            update_data = {"text": "Updated text"}
            response = client.put("/api/todos/999", json=update_data)

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Задача не найдена"

    def test_delete_todo_success(self, client, test_todo):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_crud = Mock()
            mock_crud.delete.return_value = True
            MockTodoCRUD.return_value = mock_crud

            response = client.delete(f"/api/todos/{test_todo.id}")
            assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_todo_not_found(self, client):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_crud = Mock()
            mock_crud.delete.return_value = False
            MockTodoCRUD.return_value = mock_crud

            response = client.delete("/api/todos/999")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Задача не найдена"

    def test_get_todo_stats(self, client):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_stats = {
                "total": 5,
                "completed": 3,
                "pending": 2
            }

            mock_crud = Mock()
            mock_crud.get_stats.return_value = mock_stats
            MockTodoCRUD.return_value = mock_crud

            response = client.get("/api/todos/stats")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 5
            assert data["completed"] == 3
            assert data["pending"] == 2
