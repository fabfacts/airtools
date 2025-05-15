# from pydantic import BaseModel
# from sqlmodel import Field, SQLModel, Relationship
# from airtools.models.users import User
# class SensorOut(BaseModel):
#     uid: str
#     name: str
#     lon: str
#     lat: str
#     city: str

# class Sensor(SQLModel, table=True):
#     """
#     User table

#     Args:
#         SQLModel (_type_): _description_
#         table (bool, optional): _description_. Defaults to True.
#     """

#     id: int | None = Field(default=None, primary_key=True)
#     uid: str = Field(unique=True)
#     name: str
#     lon: str
#     lat: str
#     city: str

#     user: User | None = Relationship(back_populates="user")
