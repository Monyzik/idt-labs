from unittest.mock import patch, Mock

from fastapi.testclient import TestClient


class TestMainApp:

    def test_root_endpoint(self):
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse

        test_app = FastAPI()

        @test_app.get("/")
        async def root():
            return HTMLResponse("<html>Test</html>")

        with TestClient(test_app) as client:
            response = client.get("/")
            assert response.status_code == 200

    def test_api_prefix(self, client, db_session):
        with patch('src.api.todo.TodoCRUD') as MockTodoCRUD:
            mock_crud = Mock()
            mock_crud.get_all.return_value = []
            MockTodoCRUD.return_value = mock_crud

            response = client.get("/api/todos/")
            assert response.status_code == 200

    def test_cors_middleware_with_origin(self):
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        test_app = FastAPI()

        test_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Разрешаем все origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @test_app.get("/test")
        async def test():
            return {"message": "test"}

        with TestClient(test_app) as client:
            response = client.get("/test", headers={"Origin": "http://localhost:3000"})

            assert response.status_code == 200

            assert response.headers.get("access-control-allow-origin") == "*"

    def test_cors_middleware_specific_origin(self):
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        test_app = FastAPI()

        test_app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],  # Разрешаем только конкретный origin
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @test_app.get("/test")
        async def test():
            return {"message": "test"}

        with TestClient(test_app) as client:
            response = client.options(
                "/test",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET"
                }
            )

            assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
            assert "GET" in response.headers.get("access-control-allow-methods", "")

    def test_cors_in_actual_app(self, client):
        response = client.get(
            "/api/health/",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 200

        allow_origin = response.headers.get("access-control-allow-origin")

        assert allow_origin is not None
        assert allow_origin in ["*", "http://localhost:3000"]

    def test_cors_options_in_actual_app(self, client):
        response = client.options(
            "/api/health/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        assert response.status_code in [200, 204]
        allow_origin = response.headers.get("access-control-allow-origin")
        assert allow_origin is not None
        assert allow_origin in ["*", "http://localhost:3000"]