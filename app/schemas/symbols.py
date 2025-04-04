from typing import TypeAlias

from pydantic import NaiveDatetime, model_validator, BaseModel
from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field

from app.constants import LOWEST_DATETIME, HIGHEST_DATETIME
from app.internal.id_generator import generate_ref_data_uuid


class SymbologySymbolSpec(SQLModel):
    symbol: str = Field(description="Symbol identifier")
    exchange: str | None = Field(default=None, description="Exchange identifier")
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
        default_factory=generate_ref_data_uuid,
        primary_key=True,
        description="Reference data UUID that has been assigned to a security.",
    )
    symbology: str = Field(primary_key=True, description="Symbology name")


SymbologyMaps: TypeAlias = dict[str, list[SymbologySymbolSpec]]


class SymbologySymbolCreate(SQLModel):
    """Create representation of the Symbology Symbol."""

    symbology_map: SymbologyMaps = Field(description="Mapping of symbology to symbols")
    force_duplicates: bool = Field(
        default=False, description="Flag to force duplicate entries"
    )


class SymbologySymbolPublic(SymbologySymbolCreate):
    """Public representation of the Symbology Symbol."""

    ref_data_uuid: str = Field(
        description="Reference data UUID that has been assigned to a security."
    )
    message: str | None = Field(
        None, description="Message related to the new symbol creation."
    )
    error: str | None = Field(
        None, description="Error message if any issue occurred with symbol creation."
    )


class SymbolsToQuery(BaseModel):
    """This is used to find the symbols in the database, given user inputs."""

    symbology: str
    symbol: str
    start_time: NaiveDatetime
    end_time: NaiveDatetime
