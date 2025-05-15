# pylint: disable=missing-docstring

from datetime import date
from airtools.models.core import User


def test_create_user():

    User(
        first_name="foo",
        last_name="bar",
        username="foobar",
        password="pass",
        sensorid="sensorid",
        lon="1.22222",
        lat="1.34567",
        city="Alessandria",
        last_check=date.today(),
    )
