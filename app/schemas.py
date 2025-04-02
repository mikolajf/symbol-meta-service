from itertools import groupby
from operator import attrgetter
from typing import TypeAlias

from pydantic import NaiveDatetime, model_validator, BaseModel
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
        primary_key=True,
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


def convert_list_of_db_objects_to_public_objects(
    db_objects: list[SymbologySymbolDb],
) -> list[SymbologySymbolPublic]:
    """
    Convert a list of symbols database objects to public objects.

    Args:
        db_objects (list[SymbologySymbolDb]): The list of database objects to convert.

    Returns:
        list[SymbologySymbolPublic]: The list of converted public objects.
    """
    # we need to group-by ref_data_uuid

    # we need to group-by ref_data_uuid
    grouped_by_uuid: list[SymbologySymbolPublic] = []

    # TODO <MFido> [27/03/2025] find a way how can i get away from using hard-coded strings here and instead
    #  rely on schema names

    for ref_data_uuid, group in groupby(db_objects, key=attrgetter("ref_data_uuid")):
        temp_group = {
            "ref_data_uuid": ref_data_uuid,
            "symbology_map": {},
        }

        # here again we need to group-by symbology
        for symbology, symbology_group in groupby(group, key=attrgetter("symbology")):
            temp_group["symbology_map"][symbology] = list(
                SymbologySymbolSpec.model_validate(s, strict=False)
                for s in symbology_group
            )

        grouped_by_uuid.append(SymbologySymbolPublic(**temp_group))

    return grouped_by_uuid


class SymbolsToQuery(BaseModel):
    """This is used to find the symbols in the database, given user inputs."""

    symbology: str
    symbol: str
    start_time: NaiveDatetime
    end_time: NaiveDatetime


def convert_symbology_maps_to_symbology_symbol_date_tuples(
    symbology_maps: SymbologyMaps,
) -> list[SymbolsToQuery]:
    """
    Convert a symbology map to a list of symbols to query.

    Args:
        symbology_maps (SymbologyMaps): The symbology map to convert.

    Returns:
        list[SymbolsToQuery]: The list of symbols to query.
    """
    symbols_to_query = []
    for symbology, symbols in symbology_maps.items():
        for symbol in symbols:
            symbols_to_query.append(
                SymbolsToQuery(
                    symbology=symbology,
                    symbol=symbol.symbol,
                    start_time=symbol.start_time,
                    end_time=symbol.end_time,
                )
            )
    return symbols_to_query
