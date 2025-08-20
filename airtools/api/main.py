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
    Create database tables from SQLModel models.
    Called at application startup (lifespan).
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """
    Provide a SQLModel Session for request handlers.

    Note: used with FastAPI Depends. This generator yields a session and closes it.
    """
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """
    FastAPI lifespan context: run startup/shutdown code here.
    """
    create_db_and_tables()
    yield
    logger.info("app shutdown")


app = FastAPI(lifespan=lifespan)
# Add basic CORS middleware. For production restrict origins explicitly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)  # type: ignore
def root() -> RedirectResponse:
    """Redirect root requests to the interactive docs page."""
    return RedirectResponse(url="/docs")


@app.get("/users/", response_model=list[UserOut])  # type: ignore
def users_list(
    *,
    session: Session = Depends(get_session),
) -> list[UserOut]:
    """Return list of users with their sensors loaded."""
    users: list[UserOut] = session.exec(
        select(User).options(selectinload(User.sensors))
    ).all()
    return users


@app.get("/sensors/{user_id}", response_model=list[SensorOut])  # type: ignore
def userinfo(
    user_id: int, session: Session = Depends(get_session)
) -> list[SensorOut]:
    """
    Return sensors for a given user id.

    Raises HTTPException(404) if no sensors/user found.
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
    Create a new user record.

    Validation is performed via SQLModel / Pydantic model_validate.
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
    """
    Associate an existing sensor with an existing user.

    Raises 404 if the user is not found.
    """
    user_obj: User = session.exec(
        select(User).where(User.id == user_id)
    ).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    sensor_obj: Sensor = session.exec(
        select(Sensor).where(Sensor.uid == sensor_id)
    ).first()

    # Append relationship and persist
    user_obj.sensors.append(sensor_obj)  # type: ignore
    session.add(user_obj)
    session.commit()


@app.post("/sensors/", status_code=201)  # type: ignore
def create_sensor(
    *, session: Session = Depends(get_session), sensor: Sensor
) -> Sensor:
    """
    Create a sensor record.

    Returns the created Sensor instance.
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
    Return sensor data between start_date and end_date inclusive.

    Validates that end_date is after start_date and returns 400 otherwise.
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

    # Logging/printing for debug during tests
    print(sensor_data)

    return sensor_data
