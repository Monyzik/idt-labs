from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_size=200)

session_maker = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def get_db_session() -> Generator[Session, None, None]:
    db = session_maker()
    try:
        yield db
    finally:
        db.close()
