from pydantic import NaiveDatetime, model_validator
from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field

from app.constants import LOWEST_DATETIME, HIGHEST_DATETIME
from app.internal.id_generator import generate_ref_data_uuid


class SymbologySymbolSpec(SQLModel):
    symbol: str
    exchange: str | None = None
    start_time: NaiveDatetime | None = Field(
        default=LOWEST_DATETIME,
        description=f"Start time of the symbol. Should be greater than {LOWEST_DATETIME}.",
        ge=LOWEST_DATETIME,
        sa_type=DateTime,
    )
    end_time: NaiveDatetime | None = Field(
        default=HIGHEST_DATETIME,
        description=f"End time of the symbol. Should be greater than {HIGHEST_DATETIME}.",
        le=HIGHEST_DATETIME,
        sa_type=DateTime,
    )

    @model_validator(mode="after")
    def check_start_time_less_than_end_time(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time should be less than end time.")
        return self


class SymbologySymbolDb(SymbologySymbolSpec, table=True):
    ref_data_uuid: str | None = Field(
        default_factory=generate_ref_data_uuid, primary_key=True
    )
    symbology: str
    seq_no: int


class SymbologySymbolCreate(SQLModel):
    symbology_map: dict[str, list[SymbologySymbolSpec]]
    force_duplicates: bool = False
