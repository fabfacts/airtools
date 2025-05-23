from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Relationship


class SensorOut(BaseModel):
    """
    Custom Sensor API output

    Args:
        BaseModel (_type_): _description_
    """

    uid: str
    name: str
    lon: str
    lat: str
    city: str


class SensorUpdate(BaseModel):
    uid: str


class UserOut(BaseModel):
    """
    Custom User API Output

    Args:
        BaseModel (_type_): _description_
    """

    id: int
    first_name: str
    last_name: str
    username: str
    age: Optional[int] = None
    last_check: Optional[datetime]


class UserSensors(UserOut):
    """
    Custom User API Output with sensors

    Args:
        BaseModel (_type_): _description_
    """

    sensors: list[SensorOut]


class User(SQLModel, table=True):
    """
    User table

    Args:
        SQLModel (_type_): _description_
        table (bool, optional): _description_. Defaults to True.
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


class Sensor(SQLModel, table=True):
    """
    User table

    Args:
        SQLModel (_type_): _description_
        table (bool, optional): _description_. Defaults to True.
    """

    id: int | None = Field(default=None, primary_key=True)
    uid: str = Field(unique=True)
    name: str
    lon: str
    lat: str
    city: str
    user_id: int | None = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="sensors")
