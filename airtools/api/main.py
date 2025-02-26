from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query
from sqlmodel import create_engine, SQLModel, Session, select
from airtools.models.users import User

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    """
    Generates database tables
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    for tests and production that need a different database

    Yields:
        _type_: _description_
    """
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Used to run code before and after requests being consumed

    Args:
        app (FastAPI): _description_
    """
    create_db_and_tables()


# start FastAPI
app = FastAPI(lifespan=lifespan)


@app.get("/users/", response_model=list[User])
def users_list(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users
