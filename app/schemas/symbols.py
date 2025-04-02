from typing import TypeAlias

from pydantic import NaiveDatetime, model_validator, BaseModel
from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field

from app.constants import LOWEST_DATETIME, HIGHEST_DATETIME
from app.internal.id_generator import generate_ref_data_uuid


class SymbologySymbolSpec(SQLModel):
    symbol: str
    exchange: str | None = None
    # noinspection PyTypeChecker
    start_time: NaiveDatetime | None = Field(
        default=LOWEST_DATETIME,
        description=f"Start time of the symbol. Should be greater than {LOWEST_DATETIME}.",
        ge=LOWEST_DATETIME,
        sa_type=DateTime,
        primary_key=True,
    )
    # noinspection PyTypeChecker
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
    symbology: str = Field(primary_key=True)


SymbologyMaps: TypeAlias = dict[str, list[SymbologySymbolSpec]]


class SymbologySymbolCreate(SQLModel):
    """Create representation of the Symbology Symbol."""

    symbology_map: SymbologyMaps
    force_duplicates: bool = False


class SymbologySymbolPublic(SymbologySymbolCreate):
    """Public representation of the Symbology Symbol."""

    ref_data_uuid: str
    message: str | None = None
    error: str | None = None


class SymbolsToQuery(BaseModel):
    """This is used to find the symbols in the database, given user inputs."""

    symbology: str
    symbol: str
    start_time: NaiveDatetime
    end_time: NaiveDatetime
