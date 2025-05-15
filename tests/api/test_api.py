# pylint: disable=missing-docstring

from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from airtools.models.core import User, Sensor


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
    data = response.json()[0]

    assert response.status_code == 200
    assert data["first_name"] == "foo"
    assert data["last_check"] == last_mod_date.strftime("%Y-%m-%dT%H:%M:%S")
    assert len(data["sensors"]) == 2


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

    assert response.status_code == 204

    statement = select(User).where(User.id == 1)
    assert session.exec(statement).one()


def test_user_sensor_create(session: Session, client: TestClient):
    sensor = Sensor(
        uid="11111",
        name="sensor",
        lon="1.1111",
        lat="1.2222",
        city="Alessandria",
    )
    session.add(sensor)
    session.commit()

    json_data = {
        "first_name": "foo",
        "last_name": "foo",
        "username": "foobar",
        "password": "123456",
        "sensor_id": sensor.id,
    }

    response = client.post(
        "/users/",
        json=json_data,
    )

    assert response.status_code == 204

    statement = select(User).where(User.id == 1)
    user_obj = session.exec(statement).one()
    assert user_obj.id == 1
    assert user_obj.sensor_id == sensor.id


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

    assert response.status_code == 204

    statement = select(Sensor).where(Sensor.id == 1)
    assert session.exec(statement).one()
