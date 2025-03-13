import pytest
from fastapi.testclient import TestClient

from ..main import app


@pytest.fixture(name="client")
def client_fixture():
    # TODO add session parameter when we have a database
    # # Override the get_session dependency with the fixture session
    # def get_session_override():
    #     return session
    #
    # # Set the override
    # app.dependency_overrides[get_session] = get_session_override

    # create test client
    client = TestClient(app)

    # run tests
    yield client

    # clear the override
    # app.dependency_overrides.clear()
