from fastapi.testclient import TestClient


def test_create_hero(client: TestClient):
    response = client.get("/")
    data = response.json()

    assert response.status_code == 200
    assert data == {"message": "Hello World"}
