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

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    username: str
    password: str
    sensorid: str
    lon: str
    lan: str
    city: str
    age: Optional[int] = None
    last_check: datetime = Field(default_factory=datetime.now, nullable=False)
