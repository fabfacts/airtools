import logging
import os
from typing import Annotated, Any
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import HTTPException, FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from airtools.models.core import (
    User,
    UserOut,
    Sensor,
    SensorData,
    SensorOut,
)
from airtools.components.scheduler.core import (
    start_scheduler,
    stop_scheduler,
)

logger = logging.getLogger("uvicorn.error")

sqlite_file_name: str = "database.db"
sqlite_url: str = f"sqlite:///{sqlite_file_name}"

connect_args: dict[str, Any] = {"check_same_thread": False}
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
engine = create_engine(sqlite_url, echo=DEBUG, connect_args=connect_args)


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
    Manages database initialization and background scheduler.
    """
    # === STARTUP ===
    logger.info("Starting application...")
    create_db_and_tables()

    # Start the scheduler
    start_scheduler()

    # Schedule sensor data collection jobs
    # Example: Collect data from sensor 88359 every hour
    # Uncomment and configure as needed
    # add_scheduled_job(
    #     FetchData.collect_sensor_data,
    #     trigger='interval',
    #     hours=1,
    #     kwargs={
    #         'sensor_uid': '88359',
    #         'sensor_type': 'dht22'
    #     },
    #     id='collect_sensor_88359',
    #     replace_existing=True
    # )

    logger.info("Application startup complete")

    # === APPLICATION RUNNING ===
    yield

    # === SHUTDOWN ===
    logger.info("Shutting down application...")
    stop_scheduler()
    logger.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)

# Configure CORS - restrict origins for production
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:8080"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
        select(Sensor).where(Sensor.user_id == user_id)
    ).all()
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
    try:
        session.commit()
        session.refresh(valid_user)
    except IntegrityError as e:
        session.rollback()
        logger.error("Database integrity error: %s", str(e))
        raise HTTPException(
            status_code=409,
            detail="Resource already exists or constraint violation",
        ) from e
    return valid_user


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

    sensor_obj: Sensor | None = session.exec(
        select(Sensor).where(Sensor.uid == sensor_id)
    ).first()

    if not sensor_obj:
        raise HTTPException(
            status_code=404, detail=f"Sensor with uid '{sensor_id}' not found"
        )

    # Append relationship and persist
    user_obj.sensors.append(sensor_obj)  # type: ignore
    session.add(user_obj)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        logger.error("Database integrity error: %s", str(e))
        raise HTTPException(
            status_code=409,
            detail="Resource already exists or constraint violation",
        ) from e


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
    try:
        session.commit()
        session.refresh(valid)
    except IntegrityError as e:
        session.rollback()
        logger.error("Database integrity error: %s", str(e))
        raise HTTPException(
            status_code=409,
            detail="Resource already exists or constraint violation",
        ) from e
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

    sensor: Sensor | None = session.exec(
        select(Sensor).where(Sensor.uid == sensor_uid)
    ).first()

    if not sensor:
        raise HTTPException(
            status_code=404, detail=f"Sensor with uid '{sensor_uid}' not found"
        )

    sensor_data: list[SensorData] = session.exec(
        select(SensorData).where(
            SensorData.sensor_id == sensor.id,
            SensorData.timestamp >= start_date,
            SensorData.timestamp <= end_date,
        )
    ).all()

    logger.debug(
        "Retrieved %d sensor data records for sensor %s",
        len(sensor_data),
        sensor_uid,
    )

    return sensor_data
