import pytest
from app.schemas import (
    SymbologySymbolSpec,
    SymbologySymbolDb,
    convert_list_of_db_objects_to_public_objects,
)
from app.constants import LOWEST_DATETIME, HIGHEST_DATETIME


@pytest.fixture
def symbol_spec() -> SymbologySymbolSpec:
    return SymbologySymbolSpec(
        symbol="AAPL",
        exchange="NASDAQ",
        start_time=LOWEST_DATETIME,
        end_time=HIGHEST_DATETIME,
    )


@pytest.fixture
def symbol_db() -> SymbologySymbolDb:
    return SymbologySymbolDb(
        symbol="AAPL",
        exchange="NASDAQ",
        start_time=LOWEST_DATETIME,
        end_time=HIGHEST_DATETIME,
        ref_data_uuid="uuid-1234",
        symbology="symbology-1",
    )


class TestConvertSymbolsDbToPublic:
    def test_convert_db_objects_to_public_objects(self, symbol_db: SymbologySymbolDb):
        db_objects = [symbol_db]
        public_objects = convert_list_of_db_objects_to_public_objects(db_objects)
        assert len(public_objects) == 1
        assert public_objects[0].ref_data_uuid == "uuid-1234"
        assert public_objects[0].symbology_map["symbology-1"][0].symbol == "AAPL"

    def test_convert_empty_db_objects_to_public_objects(self):
        db_objects = []
        public_objects = convert_list_of_db_objects_to_public_objects(db_objects)
        assert public_objects == []

    def test_convert_db_objects_with_multiple_symbologies(
        self, symbol_db: SymbologySymbolDb
    ):
        db_objects = [
            symbol_db,
            SymbologySymbolDb(
                symbol="ALTERNATIVE_NAME",
                exchange="ALTERNATIVE_EXCHANGE",
                start_time=LOWEST_DATETIME,
                end_time=HIGHEST_DATETIME,
                ref_data_uuid="uuid-1234",
                symbology="symbology-2",
            ),
        ]
        public_objects = convert_list_of_db_objects_to_public_objects(db_objects)
        assert len(public_objects) == 1
        assert len(public_objects[0].symbology_map) == 2
        assert public_objects[0].symbology_map["symbology-1"][0].symbol == "AAPL"
        assert (
            public_objects[0].symbology_map["symbology-2"][0].symbol
            == "ALTERNATIVE_NAME"
        )
        assert (
            public_objects[0].symbology_map["symbology-2"][0].exchange
            == "ALTERNATIVE_EXCHANGE"
        )
