import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlmodel import SQLModel, Session

from . import TEST_SYMBOLOGY
from ..main import app
from ..dependencies import get_session


@pytest.fixture(name="session")
def session_fixture():
    """
    Pytest fixture to create an in-memory SQLite database session.

    This fixture sets up an in-memory SQLite database using SQLAlchemy and SQLModel,
    and provides a session for use in tests.

    Yields:
        Session: A SQLModel session connected to the in-memory SQLite database.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Pytest fixture to create a FastAPI TestClient with a database session override.

    This fixture sets up a FastAPI TestClient and overrides the `get_session` dependency
    to use the provided session fixture.

    Args:
        session (Session): The SQLModel session provided by the session_fixture.

    Yields:
        TestClient: A FastAPI TestClient with the session dependency overridden.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def new_symbol_ref_data_uuid(client: TestClient) -> str:
    spec = [
        {
            "symbology_map": {
                TEST_SYMBOLOGY: [
                    {
                        "symbol": "EURUSD",
                    }
                ]
            },
        }
    ]

    response = client.post("/symbols/", json=spec)
    return response.json()[0]["ref_data_uuid"]
