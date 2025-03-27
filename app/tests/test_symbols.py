import pytest
from starlette.testclient import TestClient

TEST_SYMBOLOGY = "TEST_SYMBOLOGY"


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


class TestNewSymbol:
    def test_create_symbol_with_valid_data(self, client: TestClient) -> None:
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
        assert response.status_code == 200

        assert response.json()[0]["ref_data_uuid"].startswith("ref-")
        assert response.json()[0]["message"]

    def test_with_multiple_symbols(self, client: TestClient) -> None:
        spec = [
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [
                        {
                            "symbol": "EURUSD",
                        },
                    ]
                },
            },
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [
                        {
                            "symbol": "GBPUSD",
                        },
                    ]
                },
            },
        ]

        response = client.post("/symbols/", json=spec)
        assert response.status_code == 200

        ref_data_uuids = [x["ref_data_uuid"] for x in response.json()]
        assert all([x.startswith("ref-") for x in ref_data_uuids]), (
            "Each item should complete successfully, i.e. have a ref_data_uuid populated."
        )

        assert len(ref_data_uuids) == 2, "Should have 2 items in the response."
        assert len(set(ref_data_uuids)) == 2, "Should have unique ref_data_uuids."


class TestAllSymbols:
    def test_get_all_empty(self, client: TestClient) -> None:
        response = client.get("/symbols/")
        assert response.status_code == 200

        assert response.json() == [], (
            "Should have an empty list as we have not created any symbols."
        )

    def test_get_all_after_a_symbol_has_been_created(
        self, new_symbol_ref_data_uuid, client: TestClient
    ) -> None:
        response = client.get("/symbols/")
        assert response.status_code == 200

        assert len(response.json()) == 1, "Should have 1 item in the response."
        assert response.json()[0]["ref_data_uuid"].startswith("ref-"), (
            "Should have a ref_data_uuid populated."
        )


class TestGetSymbolsByRefDataUUID:
    def test_get_symbol_by_ref_data_uuid(
        self, new_symbol_ref_data_uuid, client: TestClient
    ) -> None:
        # this fixture creates a symbol and returns the ref_data_uuid
        ref_data_uuid = new_symbol_ref_data_uuid

        # Fetch the symbol by ref_data_uuid
        response = client.get(f"/symbols/{ref_data_uuid}")
        assert response.status_code == 200

        # Validate the response
        assert response.json()["ref_data_uuid"] == ref_data_uuid, (
            "Should return the correct symbol by ref_data_uuid."
        )

    def test_get_symbol_by_ref_data_uuid_any_symbology(
        self, new_symbol_ref_data_uuid, client: TestClient
    ) -> None:
        # this fixture creates a symbol and returns the ref_data_uuid
        ref_data_uuid = new_symbol_ref_data_uuid

        # Fetch the symbol by ref_data_uuid
        response = client.get(f"/symbols/{ref_data_uuid}/symbology/{TEST_SYMBOLOGY}")
        assert response.status_code == 200

        # Validate the response
        assert response.json()["ref_data_uuid"] == ref_data_uuid, (
            "Should return the correct symbol by ref_data_uuid."
        )
