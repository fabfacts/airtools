from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Relationship


class SensorOut(BaseModel):
    """
    Output model for Sensor API responses.

    Attributes:
        uid (str): Unique identifier for the sensor.
        name (str): Name of the sensor.
        lon (str): Longitude of the sensor location.
        lat (str): Latitude of the sensor location.
        city (str): City where the sensor is located.
    """

    uid: str
    name: str
    lon: str
    lat: str
    city: str


class SensorUpdate(BaseModel):
    """
    Model for updating a sensor.

    Attributes:
        uid (str): Unique identifier for the sensor.
    """

    uid: str


class UserOut(BaseModel):
    """
    Output model for User API responses.

    Attributes:
        id (int): User ID.
        first_name (str): User's first name.
        last_name (str): User's last name.
        username (str): User's username.
        age (Optional[int]): User's age.
        last_check (Optional[datetime]): Last check timestamp.
    """

    id: int
    first_name: str
    last_name: str
    username: str
    age: Optional[int] = None
    last_check: Optional[datetime]


class UserSensors(UserOut):
    """
    Output model for User API responses including sensors.

    Attributes:
        sensors (List[SensorOut]): List of sensors associated with the user.
    """

    sensors: List[SensorOut]


class User(SQLModel, table=True):  # type: ignore
    """
    Database model for users.

    Attributes:
        id (Optional[int]): User ID, primary key.
        first_name (str): User's first name.
        last_name (str): User's last name.
        username (str): User's username.
        age (Optional[int]): User's age.
        last_check (Optional[datetime]): Last check timestamp.
        sensors (List["Sensor"] | None): List of sensors associated with the user.
    """

    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    username: str
    # password: str
    # sensor_id: int | None = Field(default=None, foreign_key="sensor.id")
    age: Optional[int] = None
    last_check: Optional[datetime] = Field(
        default_factory=datetime.now, nullable=False
    )
    sensors: list["Sensor"] | None = Relationship(back_populates="user")


class Sensor(SQLModel, table=True):  # type: ignore
    """
    Database model for sensors.

    Attributes:
        id (Optional[int]): Sensor ID, primary key.
        uid (str): Unique identifier for the sensor.
        name (str): Name of the sensor.
        lon (str): Longitude of the sensor location.
        lat (str): Latitude of the sensor location.
        city (str): City where the sensor is located.
        user_id (Optional[int]): User ID, foreign key to the User table.
        data (List["SensorData"] | None): List of sensor data associated with the sensor.
    """

    id: int | None = Field(default=None, primary_key=True)
    uid: str = Field(unique=True)
    name: str
    lon: str
    lat: str
    city: str
    user_id: int | None = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="sensors")
    # sensor data
    data: list["SensorData"] | None = Relationship(back_populates="sensor")


class SensorData(SQLModel, table=True):  # type: ignore
    """
    Sensor Data table

    Args:
        SqlModel (_type_): _description_
        table (bool, optional): _description_. Defaults to True.
    """

    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(unique=True)
    temperature: float
    humidity: float
    sensor_id: int = Field(foreign_key="sensor.id")
    sensor: Sensor = Relationship(back_populates="data")
