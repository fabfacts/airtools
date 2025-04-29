from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


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
    password: str
    sensor_id: int | None = Field(default=None, foreign_key="sensor.id")
    age: Optional[int] = None
    last_check: Optional[datetime] = Field(
        default_factory=datetime.now, nullable=False
    )


class UserPublic(User):
    """
    Data returned in the response
    """

    id: int
