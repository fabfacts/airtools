# pylint: disable=missing-docstring
import csv
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from airtools.models.core import User, Sensor, SensorData


def _load_sensordata(session: Session, sensor_id: str, limit: int = 5) -> None:
    sensor_data_path: str = (
        "tests/test_files/csv/2025-02-07_dht22_sensor_88359.csv"
    )
    data: dict[str, str] = []
    with open(sensor_data_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(
            csvfile.readlines()[: limit + 1], delimiter=";"
        )
        for line in reader:
            data.append(line)

    sensor = session.exec(select(Sensor).where(Sensor.uid == sensor_id)).one()

    for row in data:
        sensor_data = SensorData(
            timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%dT%H:%M:%S"),
            temperature=row["temperature"],
            humidity=row["humidity"],
            sensor_id=sensor.id,
        )
        session.add(sensor_data)

    session.commit()


def test_list_users(session: Session, client: TestClient):
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

    response = client.get("/users/")

    print(response.json())

    data = response.json()[0]

    assert response.status_code == 200
    assert data["first_name"] == "foo"
    assert data["last_check"] == last_mod_date.strftime("%Y-%m-%dT%H:%M:%S")


def test_user_sensors(session: Session, client: TestClient):
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

    response = client.get(f"/users/{testuser.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "foo"
    assert data["last_check"] == last_mod_date.strftime("%Y-%m-%dT%H:%M:%S")
    assert len(data["sensors"]) == 2


def test_sensordata(session: Session, client: TestClient):
    start = datetime(2025, 2, 7, 0, 5, 0)
    end = datetime(2025, 2, 7, 0, 12, 0)
    # number of record to load for testing
    load_limit: int = 5

    sens = Sensor(
        uid="11111",
        name="sens1",
        lon="1.1111",
        lat="1.2222",
        city="Alessandria",
    )
    session.add(sens)
    session.commit()
    session.refresh(sens)

    _load_sensordata(session, sens.uid, limit=load_limit)

    response = client.get(
        f"/sensordata/{sens.uid}",
        params={"start_date": start.isoformat(), "end_date": end.isoformat()},
    )
    assert response.status_code == 200

    sensors_outs = response.json()
    assert len(sensors_outs) == 3


def test_user_create(session: Session, client: TestClient):
    json_data = {
        "first_name": "foo",
        "last_name": "foo",
        "username": "foobar",
        "password": "123456",
    }
    session.commit()
    response = client.post(
        "/users/",
        json=json_data,
    )

    assert response.status_code == 201

    statement = select(User).where(User.id == 1)
    assert session.exec(statement).one()


def test_user_sensor_associate(session: Session, client: TestClient):
    last_mod_date = datetime(2022, 6, 29, 8, 14, 53)

    testuser = User(
        first_name="foo",
        last_name="bar",
        username="foobar",
        password="123456",
        sensors=[],
        last_check=last_mod_date,
    )

    sens1 = Sensor(
        uid="11111",
        name="sensor",
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

    session.add(testuser)
    session.add(sens1)
    session.add(sens2)
    session.commit()

    response = client.put(
        f"/addsensor/{testuser.id}/{sens1.uid}",
    )
    assert response.status_code == 204

    response = client.put(
        f"/addsensor/{testuser.id}/{sens2.uid}",
    )
    assert response.status_code == 204

    statement = select(User).where(User.id == testuser.id)
    user_obj = session.exec(statement).one()
    assert user_obj.username == testuser.username
    assert len(user_obj.sensors) == 2


def test_sensor_create(session: Session, client: TestClient):
    json_data = {
        "uid": "11111",
        "name": "sensor",
        "lon": "0.12222",
        "lat": "0.22222",
        "city": "Ale",
    }
    session.commit()
    response = client.post(
        "/sensors/",
        json=json_data,
    )

    assert response.status_code == 201

    statement = select(Sensor).where(Sensor.id == 1)
    assert session.exec(statement).one()
