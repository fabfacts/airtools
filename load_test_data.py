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

    sens3 = Sensor(
        uid="33333",
        name="sens3",
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

    testuser2 = User(
        first_name="foo2",
        last_name="bar2",
        username="foobar2",
        password="123456",
        sensors=[sens3],
        last_check=last_mod_date,
    )

    session.add(testuser)
    session.add(testuser2)
    session.commit()
    session.refresh(testuser)
