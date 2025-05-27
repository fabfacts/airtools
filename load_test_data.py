from csv import DictReader
from datetime import datetime
from sqlmodel import Session, SQLModel
from sqlmodel import create_engine, select

from airtools.models.core import User, Sensor, SensorData

FILE_NAME = "database.db"
SENSOR_ID = "88359"
SENSOR_DATA_PATH = "tests/test_files/csv/2025-02-07_dht22_sensor_88359.csv"
DATABASE_URL = f"sqlite:///{FILE_NAME}"

engine = create_engine(DATABASE_URL, echo=True)

# Create the tables if not already present
SQLModel.metadata.create_all(engine)


def load_sensor_data() -> DictReader:
    """
    Read example data

    Returns:
        _type_: _description_
    """
    data: dict[str, str] = []
    with open(SENSOR_DATA_PATH, newline="", encoding="utf-8") as csvfile:
        reader = DictReader(csvfile, delimiter=";")
        # print(reader)
        for line in reader:
            data.append(line)

    return data


with Session(engine) as session:
    last_mod_date = datetime(2022, 6, 29, 8, 14, 53)

    sens1 = Sensor(
        uid="88359",
        name="dht22",
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

    for row in load_sensor_data():
        sensor = session.exec(
            select(Sensor).where(Sensor.uid == row["sensor_id"])
        ).one()

        sensor_data = SensorData(
            timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%dT%H:%M:%S"),
            temperature=row["temperature"],
            humidity=row["humidity"],
            sensor_id=sensor.id,
        )

        session.add(sensor_data)

    session.commit()
