from unittest.mock import Mock, patch


class TestHealthCheck:

    def test_health_check_success(self, client, db_session):
        with patch('src.api.health.TodoCRUD') as MockTodoCRUD:
            mock_crud = Mock()
            mock_crud.get_stats.return_value = {"total": 0, "completed": 0, "pending": 0}
            MockTodoCRUD.return_value = mock_crud

            response = client.get("/api/health/")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["version"] == "1.0.0"
            assert data["environment"] == "production"

    def test_health_check_database_error(self, client):
        with patch('src.api.health.TodoCRUD') as MockTodoCRUD:
            mock_crud = Mock()
            mock_crud.get_stats.side_effect = Exception("Database connection failed")
            MockTodoCRUD.return_value = mock_crud

            response = client.get("/api/health/")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
            assert "Database connection failed" in data["error"]
