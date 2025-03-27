from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.internal.id_generator import generate_ref_data_uuid
from app.dependencies import get_session
from app.schemas import (
    SymbologySymbolCreate,
    SymbologySymbolDb,
    SymbologySymbolPublic,
    convert_list_of_db_objects_to_public_objects,
)

router = APIRouter(
    prefix="/symbols",
    tags=["symbols"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_all_symbols(
    *, session: Session = Depends(get_session)
) -> list[SymbologySymbolPublic]:
    """
    Retrieve all symbols from the database.

    This endpoint fetches all symbols from the database and returns them as a list of SymbologySymbolDb objects.

    Args:
        session (Session): The database session dependency.

    Returns:
        list[SymbologySymbolDb]: A list of all symbols in the database.
    """

    statement = select(SymbologySymbolDb)
    results = session.exec(statement)
    all_symbols = results.all()

    # convert to public version so the output is consistent between endpoints
    all_symbols_public = convert_list_of_db_objects_to_public_objects(all_symbols)
    return all_symbols_public


@router.post("/")
async def create_symbol(
    *, session: Session = Depends(get_session), symbols: list[SymbologySymbolCreate]
) -> list[SymbologySymbolPublic]:
    """
    Create new symbols in the database.

    This endpoint accepts a list of SymbologySymbolCreate objects, generates unique ref_data_uuid for each symbol,
    and inserts them into the database. It returns the created symbols as a list of SymbologySymbolPublic objects.

    Args:
        session (Session): The database session dependency.
        symbols (list[SymbologySymbolCreate]): A list of symbols to be created.

    Returns:
        list[SymbologySymbolPublic]: A list of created symbols with their ref_data_uuid and a success message.
    """

    # db objects list
    db_objects: list[SymbologySymbolDb] = []

    for symbol in symbols:
        # unpack symbology_map object
        symbology_map = symbol.symbology_map

        # TODO <MFido> [27/03/2025] iterate over symbols provided, and check in database if they already exists. if so,
        #  handle appropriately, else, for each symbol generate unique ref_data_uuid and insert into database
        # assign unique ref_data_uuid to each symbol
        ref_data_uuid = generate_ref_data_uuid()

        for symbology_name, symbology_values in symbology_map.items():
            # TODO <MFido> [27/03/2025] we should instead iterate over sorted symbology values by start_time
            for symbol_spec_entry in symbology_values:
                db_object = SymbologySymbolDb(
                    **symbol_spec_entry.model_dump(),
                    symbology=symbology_name,
                    ref_data_uuid=ref_data_uuid,
                )

                session.add(db_object)
                db_objects.append(db_object)

    # we commit all transactions
    session.commit()

    # then we should refresh all object to get updated ref_data_uuid
    outputs: list[SymbologySymbolPublic] = []
    for symbol_create, db_object in zip(symbols, db_objects):
        outputs.append(
            SymbologySymbolPublic(
                **symbol_create.model_dump(),
                ref_data_uuid=db_object.ref_data_uuid,
                message="Symbol created successfully",
            )
        )

    return outputs
