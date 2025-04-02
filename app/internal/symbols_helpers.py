from _operator import attrgetter
from itertools import groupby

from app.schemas import (
    SymbologySymbolDb,
    SymbologySymbolPublic,
    SymbologySymbolSpec,
    SymbologyMaps,
    SymbolsToQuery,
)


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
