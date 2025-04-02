from starlette.status import (
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_207_MULTI_STATUS,
)
from starlette.testclient import TestClient

from app.tests import TEST_SYMBOLOGY


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
        assert response.status_code == HTTP_201_CREATED

        assert response.json()[0]["ref_data_uuid"].startswith("ref-")
        assert response.json()[0]["message"]

    def test_create_symbol_with_start_date(self, client: TestClient) -> None:
        spec = [
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [
                        {
                            "symbol": "EURUSD",
                            "start_time": "2021-01-01T00:00:00",
                        }
                    ]
                },
            }
        ]

        response = client.post("/symbols/", json=spec)
        assert response.status_code == HTTP_201_CREATED

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
        assert response.status_code == HTTP_201_CREATED

        ref_data_uuids = [x["ref_data_uuid"] for x in response.json()]
        assert all([x.startswith("ref-") for x in ref_data_uuids]), (
            "Each item should complete successfully, i.e. have a ref_data_uuid populated."
        )

        assert len(ref_data_uuids) == 2, "Should have 2 items in the response."
        assert len(set(ref_data_uuids)) == 2, "Should have unique ref_data_uuids."

    def test_with_no_symbols(self, client: TestClient) -> None:
        spec = [
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [],
                },
            }
        ]

        response = client.post("/symbols/", json=spec)
        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_try_to_create_same_symbol_twice(self, client: TestClient) -> None:
        spec = [
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [
                        {
                            "symbol": "NEW_SYMBOL",
                        }
                    ]
                },
            }
        ]

        response = client.post("/symbols/", json=spec)
        assert response.status_code == HTTP_201_CREATED, (
            "First symbol should be created successfully."
        )

        response = client.post("/symbols/", json=spec)
        assert response.status_code == HTTP_400_BAD_REQUEST, (
            "Second symbol should fail to be created."
        )

    def test_make_subsequent_request_with_more_symbologies_than_in_the_first_one(
        self, client: TestClient
    ) -> None:
        spec = [
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [
                        {
                            "symbol": "NEW_SYMBOL",
                        }
                    ]
                },
            }
        ]

        response = client.post("/symbols/", json=spec)
        assert response.status_code == HTTP_201_CREATED, (
            "First symbol should be created successfully."
        )

        spec = [
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [
                        {
                            "symbol": "NEW_SYMBOL",
                        },
                    ],
                    "ANOTHER_SYMBOLOGY": [
                        {
                            "symbol": "NEW_SYMBOL",
                        },
                    ],
                },
            }
        ]

        response = client.post("/symbols/", json=spec)
        assert response.status_code == HTTP_201_CREATED, (
            "Second symbol should also be created as creating new symbologies."
        )

    def test_make_subseqent_request_with_more_symbols_than_in_the_first_one(
        self, client: TestClient
    ) -> None:
        spec = [
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [
                        {
                            "symbol": "NEW_SYMBOL",
                        }
                    ]
                },
            }
        ]

        response = client.post("/symbols/", json=spec)
        assert response.status_code == HTTP_201_CREATED, (
            "First symbol should be created successfully."
        )
        first_request_ref_data_uuid = response.json()[0]["ref_data_uuid"]

        spec = [
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [
                        {
                            "symbol": "NEW_SYMBOL",
                        },
                    ],
                },
            },
            {
                "symbology_map": {
                    TEST_SYMBOLOGY: [
                        {
                            "symbol": "ANOTHER_NEW_SYMBOL",
                        },
                    ],
                },
            },
        ]

        response = client.post("/symbols/", json=spec)
        assert response.status_code == HTTP_207_MULTI_STATUS, (
            "One should fail. One should pass."
        )
        assert len(response.json()) == 2, "Should have 2 items in the response."
        assert response.json()[0]["ref_data_uuid"] == first_request_ref_data_uuid, (
            "First item should be the same."
        )
        assert response.json()[0]["error"] != "", (
            "First item should have an error message."
        )
        assert response.json()[1]["ref_data_uuid"] != first_request_ref_data_uuid, (
            "Second item should be different."
        )


class TestAllSymbols:
    def test_get_all_empty(self, client: TestClient) -> None:
        response = client.get("/symbols/")
        assert response.status_code == HTTP_200_OK

        assert response.json() == [], (
            "Should have an empty list as we have not created any symbols."
        )

    def test_get_all_after_a_symbol_has_been_created(
        self, new_symbol_ref_data_uuid, client: TestClient
    ) -> None:
        response = client.get("/symbols/")
        assert response.status_code == HTTP_200_OK

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
        assert response.status_code == HTTP_200_OK

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
        assert response.status_code == HTTP_200_OK

        # Validate the response
        assert response.json()["ref_data_uuid"] == ref_data_uuid, (
            "Should return the correct symbol by ref_data_uuid."
        )
