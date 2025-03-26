import datetime

import pytest

from app.constants import HIGHEST_DATETIME, LOWEST_DATETIME
from app.schemas import SymbologySymbolSpec


class TestSymbologySymbolSpec:
    def test_create_simple_symbology_symbol_spec(self):
        # create symbol spec with just symbol, the only mandatory field
        simple_spec = SymbologySymbolSpec(
            symbol="EURUSD",
        )
        assert simple_spec.symbol == "EURUSD"
        assert simple_spec.end_time == HIGHEST_DATETIME

    def test_with_valid_symbol_spec(self):
        spec = SymbologySymbolSpec(
            symbol="AAPL",
            exchange="NASDAQ",
            start_time=LOWEST_DATETIME,
            end_time=HIGHEST_DATETIME,
        )
        assert spec.symbol == "AAPL"
        assert spec.exchange == "NASDAQ"
        assert spec.start_time == LOWEST_DATETIME
        assert spec.end_time == HIGHEST_DATETIME

    def test_with_invalid_date(self):
        with pytest.raises(ValueError):
            SymbologySymbolSpec(
                symbol="AAPL",
                start_time=LOWEST_DATETIME - datetime.timedelta(days=1),
            )

    def test_with_start_time_greater_than_end_time(self):
        with pytest.raises(ValueError):
            SymbologySymbolSpec(
                symbol="AAPL",
                start_time=HIGHEST_DATETIME,
                end_time=LOWEST_DATETIME,
            )
