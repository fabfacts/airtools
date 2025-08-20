# Developers

Sensors Data can be downloaded in CSV format from https://archive.sensor.community/

Start environment

    $ hatch shell

Start api test server

    $ fastapi dev main.py

go to: http://127.0.0.1:8000/docs

Run tests

    $ hatch run test:pytest

Run Database migrations

Generate migration

    $ alembic revision --autogenerate -m "message"

OPTIONAL mark migration without transaction

    $ alembic stamp head

Apply migration

    $  alembic upgrade head

Testing with curl

    $ curl -X GET http://localhost:8000/sensordata/<sensor_uid>?start_date=2025-02-07T00:05:00&end_date=2025-02-07T00:12:00

## Data

To load custom data in the database you can use this script

    $ python load_test_data.py
