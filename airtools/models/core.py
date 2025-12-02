from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Relationship


class SensorOut(BaseModel):
    """
    Output model for sensor API responses.
    Only public sensor attributes are returned to API clients.
    """

    uid: str
    name: str
    lon: float
    lat: float
    city: str


class SensorUpdate(BaseModel):
    """Schema used to update sensor fields (currently only uid)."""

    uid: str


class UserOut(BaseModel):
    """
    Output model for user API responses.
    Contains a subset of User DB model fields returned by the API.
    """

    id: int
    first_name: str
    last_name: str
    username: str
    age: Optional[int] = None
    last_check: Optional[datetime]


class UserSensors(UserOut):
    """User output model extended with a list of sensors."""

    sensors: List[SensorOut]


class User(SQLModel, table=True):  # type: ignore
    """
    Database model representing application users.

    Notes:
      - `table=True` marks this class as a DB table for SQLModel.
      - `id` is the primary key.
      - `sensors` is a relationship populated via SQLModel/SQLAlchemy.
    """

    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    username: str
    # password omitted from public models; stored in DB for auth
    age: Optional[int] = None
    # store last_check timestamp; default provided by Field factory
    last_check: Optional[datetime] = Field(
        default_factory=datetime.now, nullable=False
    )
    # relationship to Sensor objects (many-to-many or one-to-many depending on schema)
    sensors: list["Sensor"] | None = Relationship(back_populates="user")


class Sensor(SQLModel, table=True):  # type: ignore
    """
    Database model for sensors.

    Notes:
      - `uid` is a unique sensor identifier (provided by hardware).
      - `user_id` links a sensor to an owning user (if you use one-to-many).
      - `data` relationship links time-series SensorData rows.
    """

    id: int | None = Field(default=None, primary_key=True)
    uid: str = Field(unique=True)
    name: str
    lon: float = Field(ge=-180.0, le=180.0)
    lat: float = Field(ge=-90.0, le=90.0)
    city: str
    user_id: int | None = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="sensors")
    # time-series measurements for this sensor
    data: list["SensorData"] | None = Relationship(back_populates="sensor")


class SensorData(SQLModel, table=True):  # type: ignore
    """
    Table storing time-series measurements for sensors.

    Fields:
      - timestamp: measurement datetime (unique per dataset here)
      - temperature/humidity/P1/P2: optional numeric fields depending on sensor type
      - sensor_id: foreign key to Sensor table
    """

    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime
    temperature: float
    humidity: float
    sensor_id: int = Field(foreign_key="sensor.id")
    # back-reference to parent Sensor
    sensor: Sensor = Relationship(back_populates="data")
