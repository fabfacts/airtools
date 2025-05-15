from datetime import datetime
from sqlmodel import Session, SQLModel
from sqlmodel import create_engine

from airtools.models.core import User, Sensor

FILE_NAME = "database.db"
DATABASE_URL = f"sqlite:///{FILE_NAME}"

engine = create_engine(DATABASE_URL, echo=True)

# Create the tables if not already present
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    last_mod_date = datetime(2022, 6, 29, 8, 14, 53)

    sens1 = Sensor(
        uid="11111",
        name="sens1",
        lon="1.1111",
        lat="1.2222",
        city="Alessandria",
    )

    sens2 = Sensor(
        uid="22222",
        name="sens2",
        lon="1.1111",
        lat="1.2222",
        city="Alessandria",
    )

    testuser = User(
        first_name="foo",
        last_name="bar",
        username="foobar",
        password="123456",
        sensors=[sens1, sens2],
        last_check=last_mod_date,
    )

    session.add(testuser)
    session.commit()
    session.refresh(testuser)
