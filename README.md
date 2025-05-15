# Developers

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
