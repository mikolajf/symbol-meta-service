import datetime

from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from starlette.testclient import TestClient

from app.constants import LOWEST_DATETIME


def test_get_all_corp_actions_returns_empty_list(client: TestClient) -> None:
    response = client.get("/corpActions/")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == []


def test_create_corp_action_given_ref_data_uuid(
    client: TestClient, new_symbol_ref_data_uuid: str
) -> None:
    corp_action = {
        "ref_data_uuid": new_symbol_ref_data_uuid,
        "action_type": "STOCK_SPLIT",
        "effective_time": datetime.datetime.now().isoformat(),
        "additive_adjustment": 1.0,
    }

    response = client.post("/corpActions/", json=corp_action)
    assert response.status_code == HTTP_201_CREATED
    assert response.json()[0]["ref_data_uuid"] == new_symbol_ref_data_uuid
    assert response.json()[0]["action_type"] == "STOCK_SPLIT"
    assert response.json()[0]["additive_adjustment"] == 1.0
    assert response.json()[0]["effective_time"] == corp_action["effective_time"]


def test_create_corp_action_with_invalid_date(
    client: TestClient, new_symbol_ref_data_uuid: str
) -> None:
    corp_action = {
        "ref_data_uuid": new_symbol_ref_data_uuid,
        "action_type": "STOCK_SPLIT",
        "effective_time": (LOWEST_DATETIME - datetime.timedelta(days=1)).isoformat(),
        "additive_adjustment": 1.0,
    }

    response = client.post("/corpActions/", json=corp_action)
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
