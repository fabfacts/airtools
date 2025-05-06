from sqlmodel import Field, SQLModel


class Sensor(SQLModel, table=True):
    """
    User table

    Args:
        SQLModel (_type_): _description_
        table (bool, optional): _description_. Defaults to True.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    lon: str
    lan: str
    city: str
