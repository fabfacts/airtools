# from typing import Optional
# from datetime import datetime
# from pydantic import BaseModel
# from sqlmodel import Field, SQLModel, Relationship

# from airtools.models.sensors import SensorOut

# class UserOut(BaseModel):
#     """
#     Custom User API Output

#     Args:
#         BaseModel (_type_): _description_
#     """
#     first_name: str
#     last_name: str
#     username: str
#     sensor_id: list[SensorOut]
#     age: Optional[int] = None
#     last_check: Optional[datetime]


# class User(SQLModel, table=True):
#     """
#     User table

#     Args:
#         SQLModel (_type_): _description_
#         table (bool, optional): _description_. Defaults to True.
#     """

#     id: int | None = Field(default=None, primary_key=True)
#     first_name: str
#     last_name: str
#     username: str
#     # password: str
#     sensor_id: int | None = Field(default=None, foreign_key="sensor.id")
#     age: Optional[int] = None
#     last_check: Optional[datetime] = Field(
#         default_factory=datetime.now, nullable=False
#     )

#     sensors: list["Sensor"] | None = Relationship(back_populates="sensors")
