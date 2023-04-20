import os

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.orm import sessionmaker

SQLITE_DATABASE_URL = os.getenv("SQLITE_DATABASE_URL", "sqlite:///./metadata-v3.db")

# `check_same_thread` equals to False enables multithreading for SQLite.
connect_args = {"check_same_thread": False}
engine = create_engine(SQLITE_DATABASE_URL, echo=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_db_session():
    """
    Create a new database session and close the session after the operation has ended.
    """
    with Session(engine) as session:
        yield session
