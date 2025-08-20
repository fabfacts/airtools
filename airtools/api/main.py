import logging
from typing import Annotated, Any
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import HTTPException, FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.orm import selectinload
from airtools.models.core import (
    User,
    UserOut,
    Sensor,
    SensorData,
    SensorOut,
)

logger = logging.getLogger("uvicorn.error")

sqlite_file_name: str = "database.db"
sqlite_url: str = f"sqlite:///{sqlite_file_name}"

connect_args: dict[str, Any] = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables() -> None:
    """
    Generates database tables
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """
    for tests and production that need a different database

    Yields:
        Session: SQLModel session
    """
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """
    Used to run code before and after requests being consumed

    Args:
        app (FastAPI): FastAPI application
    """
    create_db_and_tables()
    yield
    logger.info("app shutdown")


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


@app.get("/", include_in_schema=False)  # type: ignore
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/users/", response_model=list[UserOut])  # type: ignore
def users_list(
    *,
    session: Session = Depends(get_session),
    # offset: int = 0,
    # limit: int = Query(default=100, le=100),
) -> list[UserOut]:
    users: list[UserOut] = session.exec(
        select(User).options(selectinload(User.sensors))
    ).all()
    return users


@app.get("/sensors/{user_id}", response_model=list[SensorOut])  # type: ignore
def userinfo(
    user_id: int, session: Session = Depends(get_session)
) -> list[SensorOut]:
    """
    Return user sensors

    Args:
        user_id (int): User ID
        session (Session, optional): SQLModel session

    Returns:
        list[SensorOut]: List of sensors
    """
    sensors: list[SensorOut] = session.exec(
        select(Sensor).where(user_id == user_id)
    )
    if not sensors:
        raise HTTPException(status_code=404, detail="User not found")
    return sensors


@app.post("/users/", status_code=201)  # type: ignore
def create_user(
    *, session: Session = Depends(get_session), user: User
) -> User:
    """
    Create user

    Args:
        user (User): User Model
    """
    valid_user: User = User.model_validate(user)
    session.add(valid_user)
    session.commit()
    session.refresh(valid_user)
    return user


@app.put("/addsensor/{user_id}/{sensor_id}", status_code=204)  # type: ignore
def update_user_sensor(
    user_id: int, sensor_id: str, session: Session = Depends(get_session)
) -> None:
    """add existing sensor to existing user

    Args:
        user_id (int): User ID
        sensor_id (str): Sensor ID
    """
    user_obj: User = session.exec(
        select(User).where(User.id == user_id)
    ).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    sensor_obj: Sensor = session.exec(
        select(Sensor).where(Sensor.uid == sensor_id)
    ).first()

    user_obj.sensors.append(sensor_obj)  # type: ignore
    session.add(user_obj)
    session.commit()


@app.post("/sensors/", status_code=201)  # type: ignore
def create_sensor(
    *, session: Session = Depends(get_session), sensor: Sensor
) -> Sensor:
    """
    Create Sensor

    Args:
        sensor (Sensor): Sensor Model
        session (Session, optional): SQLModel session
    """
    valid: Sensor = Sensor.model_validate(sensor)
    session.add(valid)
    session.commit()
    session.refresh(valid)
    return valid


@app.get("/sensordata/{sensor_uid}")  # type: ignore
def get_data_by_date(
    sensor_uid: Annotated[str, "Sensor Uid"],
    start_date: datetime,
    end_date: datetime,
    session: Session = Depends(get_session),
) -> list[SensorData]:
    """
    Return a compressed json containing sensor data

    Args:
        sensor_uid (str): Sensor UID
        start_date (datetime): Start of date range
        end_date (datetime): End of date range

    Raises:
        HTTPException: If end_date < start_date

    Returns:
        list[SensorData]: List of sensor data
    """
    if end_date < start_date:
        raise HTTPException(
            status_code=400, detail="End date must be after start date"
        )

    sensor: Sensor = session.exec(
        select(Sensor).where(Sensor.uid == sensor_uid)
    ).one()
    sensor_data: list[SensorData] = session.exec(
        select(SensorData).where(
            SensorData.sensor_id == sensor.id,
            SensorData.timestamp >= start_date,
            SensorData.timestamp <= end_date,
        )
    ).all()

    print(sensor_data)

    return sensor_data
