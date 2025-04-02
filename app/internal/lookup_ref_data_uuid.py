from collections import defaultdict

from fastapi import Depends
from sqlmodel import Session, select

from app.dependencies import get_session
from app.internal.symbols_helpers import (
    convert_symbology_maps_to_symbology_symbol_date_tuples,
)
from app.schemas import SymbologyMaps, SymbolsToQuery, SymbologySymbolDb


async def lookup_ref_data_uuid_given_symbology_maps(
    *, session: Session = Depends(get_session), symbology_maps: SymbologyMaps
) -> dict[str, set[str]]:
    """
    Lookup reference data UUIDs given symbology maps.

    This function iterates over the provided symbology maps, checks in the database if the symbols already exist,
    and returns a set of unique reference data UUIDs.

    Args:
        session (Session): The database session dependency.
        symbology_maps (SymbologyMaps): The symbology maps to query.

    Returns:
        dict[str, list[str]]: A dict of unique reference data UUIDs, and defined symbologies for this symbol.
    """

    # iterate over symbols provided, and check in database if they already exists
    symbols_to_query: list[SymbolsToQuery] = (
        convert_symbology_maps_to_symbology_symbol_date_tuples(
            symbology_maps=symbology_maps
        )
    )
    unique_ref_data_uuids: dict[str, set[str]] = defaultdict(set)
    for symbol_to_query in symbols_to_query:
        statement = select(SymbologySymbolDb).where(
            SymbologySymbolDb.symbol == symbol_to_query.symbol,
            SymbologySymbolDb.symbology == symbol_to_query.symbology,
            SymbologySymbolDb.start_time >= symbol_to_query.start_time,
            SymbologySymbolDb.end_time <= symbol_to_query.end_time,
        )

        results = session.exec(statement)
        # TODO <MFido> [02/04/2025] we use .all() here with the assumption (to be reviewed) that more than one symbol
        #  can be found, either get rid of this assumption (and replace with .one() or document explicitly
        all_symbols: list[SymbologySymbolDb] = results.all()

        # if we found a symbol / symbols, update the unique_ref_data_uuids dict with the ref_data_uuid as key and symbology as value
        for symbol in all_symbols:
            unique_ref_data_uuids[symbol.ref_data_uuid].add(symbol.symbology)
    return unique_ref_data_uuids
