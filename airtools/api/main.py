import logging

from contextlib import asynccontextmanager
from fastapi import HTTPException
from fastapi import FastAPI, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.orm import selectinload
from airtools.models.core import User, UserOut, Sensor, UserSensors

# from airtools.components.scheduler.core import get_scheduler
logger = logging.getLogger("uvicorn.error")

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
    # start scheduler
    # scheduler = get_scheduler()
    # scheduler.start()
    yield
    logger.info("app shutdown")
    # close the scheduler on exit
    # scheduler.shutdown()


# start FastAPI
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Replace "*" with specific origins for security, e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/users/", response_model=list[UserOut])
def users_list(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    users = session.exec(
        select(User).options(selectinload(User.sensors))
    ).all()

    return users


@app.get("/users/{user_id}", response_model=UserSensors)
def userinfo(user_id: int, session: Session = Depends(get_session)):
    """
    Return user sensors

    Args:
        user_id (int): _description_
        session (Session, optional): _description_. Defaults to Depends(get_session).

    Returns:
        _type_: _description_
    """
    user = session.exec(
        select(User)
        .options(selectinload(User.sensors))
        .where(User.id == user_id)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/users/", status_code=201)
def create_user(*, session: Session = Depends(get_session), user: User):
    """
    Create user

    Args:
        user (User): User Model
    """
    valid_user = User.model_validate(user)
    session.add(valid_user)
    session.commit()
    session.refresh(valid_user)
    return user


@app.put("/addsensor/{user_id}/{sensor_id}", status_code=204)
def update_user_sensor(
    user_id: int, sensor_id: str, session: Session = Depends(get_session)
) -> None:
    """add existing sensor to existing user

    Args:
        user_id (int): _description_
        sensor_id (str): _description_
    """
    user_obj = session.exec(select(User).where(User.id == user_id)).first()
    sensor_obj = session.exec(
        select(Sensor).where(Sensor.uid == sensor_id)
    ).first()
    print(sensor_obj.id)
    # print(user_obj.id)
    user_obj.sensors.append(sensor_obj)

    session.add(user_obj)
    session.commit()


@app.post("/sensors/", status_code=201)
def create_sensor(*, session: Session = Depends(get_session), sensor: Sensor):
    """
    Create Sensor

    Args:
        user (Sensor): _description_
        session (Session, optional): _description_. Defaults to Depends(get_session).
    """
    valid = Sensor.model_validate(sensor)
    session.add(valid)
    session.commit()
    session.refresh(valid)
    return valid
