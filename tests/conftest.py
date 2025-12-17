import os
import sys
import pytest
import warnings
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", message="unclosed.*")

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ["DATABASE_URL"] = "sqlite://"

from src.database.models import Base
from src.database.database_manager import get_db
from src.main import app


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_engine, db_session):
    def override_get_db():
        yield db_session

    import unittest.mock as mock

    with mock.patch('src.main.engine', db_engine):
        with mock.patch('src.database.database_manager.engine', db_engine):
            with mock.patch('src.main.Base.metadata.create_all'):
                original_get_db = app.dependency_overrides.get(get_db)

                app.dependency_overrides[get_db] = override_get_db

                try:
                    with TestClient(app) as test_client:
                        yield test_client
                finally:
                    if original_get_db:
                        app.dependency_overrides[get_db] = original_get_db
                    else:
                        app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def test_todo(db_session):
    from src.database.models import Todo

    db_session.query(Todo).delete()
    db_session.commit()

    todo = Todo(text="Test todo item")
    db_session.add(todo)
    db_session.commit()
    db_session.refresh(todo)
    return todo
