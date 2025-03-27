from starlette.testclient import TestClient


class TestNewSymbol:
    def test_create_symbol_with_valid_data(self, client: TestClient) -> None:
        spec = [
            {
                "symbology_map": {
                    "TEST_SYMBOLOGY": [
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
                    "TEST_SYMBOLOGY": [
                        {
                            "symbol": "EURUSD",
                        },
                    ]
                },
            },
            {
                "symbology_map": {
                    "TEST_SYMBOLOGY": [
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
