from pathlib import Path
import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from airtools.api.main import app, get_session


# def load_testdata(session):
#     last_mod_date = datetime(2022, 6, 29, 8, 14, 53)

#     testuser = User(
#         first_name="foo",
#         last_name="bar",
#         username="foobar",
#         password="123456",
#         sensors=[],
#         last_check=last_mod_date,
#     )

#     sens1 = Sensor(
#         uid="11111",
#         name="sensor",
#         lon="1.1111",
#         lat="1.2222",
#         city="Alessandria",
#     )

#     sens2 = Sensor(
#         uid="22222",
#         name="sens2",
#         lon="1.1111",
#         lat="1.2222",
#         city="Alessandria",
#     )

#     session.add(testuser)
#     session.add(sens1)
#     session.add(sens2)
#     session.commit()


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # load_testdata(session)
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def test_files_path():
    """
    Test files root dir
    """
    return Path(__file__).parent / "test_files"
