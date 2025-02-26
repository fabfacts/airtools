# pylint: disable=missing-docstring

from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime
from airtools.models.users import User


def test_list_users(session: Session, client: TestClient):
    last_mod_date = datetime(2022, 6, 29, 8, 14, 53)
    testuser = User(
        first_name="foo",
        last_name="bar",
        username="foobar",
        password="123456",
        sensorid="sid",
        lon="1.1111",
        lan="1.2222",
        city="Alessandria",
        last_check=last_mod_date,
    )
    session.add(testuser)
    session.commit()

    response = client.get("/users/")
    data = response.json()[0]

    assert response.status_code == 200
    assert data["first_name"] == "foo"
    assert data["last_check"] == last_mod_date.strftime("%Y-%m-%dT%H:%M:%S")
