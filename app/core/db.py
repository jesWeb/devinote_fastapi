from sqlalchemy import engine
from sqlmodel import Session, create_engine, SQLModel
from app.core.config import settings
from typing import Iterator

settings = create_engine(settings.DATABASE_URL, echo=False, connect_args={
                         "check_same_thread"} if "sqlite" in settings.DATABASE_URL else {})

# dev solo


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
