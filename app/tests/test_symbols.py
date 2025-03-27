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
