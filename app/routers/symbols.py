from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from starlette.responses import Response
from starlette.status import (
    HTTP_207_MULTI_STATUS,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)

from app.internal.id_generator import generate_ref_data_uuid
from app.dependencies import get_session
from app.internal.lookup_ref_data_uuid import lookup_ref_data_uuid_given_symbology_maps
from app.internal.symbols_helpers import convert_list_of_db_objects_to_public_objects
from app.schemas import (
    SymbologySymbolCreate,
    SymbologySymbolDb,
    SymbologySymbolPublic,
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


@router.get("/{ref_data_uuid}")
@router.get("/{ref_data_uuid}/symbology/{symbology}")
async def get_symbol_by_ref_data_uuid(
    *,
    session: Session = Depends(get_session),
    ref_data_uuid: str,
    symbology: str | None = None,
) -> SymbologySymbolPublic:
    """
    Retrieve a symbol by its reference data UUID.

    This endpoint fetches a symbol from the database using its reference data UUID and returns it as a SymbologySymbolPublic object.

    Args:
        session (Session): The database session dependency.
        ref_data_uuid (str): The reference data UUID of the symbol.
        symbology (str | None): The symbology of the symbol. Defaults to None.

    Returns:
        SymbologySymbolPublic: The symbol with the specified reference data UUID.
    """

    statement = select(SymbologySymbolDb).where(
        SymbologySymbolDb.ref_data_uuid == ref_data_uuid
    )

    if symbology:
        # filter by symbology if provided
        statement = statement.where(SymbologySymbolDb.symbology == symbology)

    results = session.exec(statement)
    all_symbols = results.all()

    # convert to public version so the output is consistent between endpoints
    all_symbols_public = convert_list_of_db_objects_to_public_objects(all_symbols)

    # given we query by ref_data_uuid, we should only have one result
    return all_symbols_public[0]


@router.post("/", status_code=HTTP_201_CREATED)
async def create_symbol(
    *,
    session: Session = Depends(get_session),
    symbols: list[SymbologySymbolCreate],
    response: Response,
) -> list[SymbologySymbolPublic]:
    """
    Create new symbols in the database.

    This endpoint accepts a list of SymbologySymbolCreate objects, generates unique ref_data_uuid for each symbol,
    and inserts them into the database. It returns the created symbols as a list of SymbologySymbolPublic objects.

    Args:
        session (Session): The database session dependency.
        symbols (list[SymbologySymbolCreate]): A list of symbols to be created.
        response (Response): The response object to set the status code.

    Returns:
        list[SymbologySymbolPublic]: A list of created symbols with their ref_data_uuid and a success message.
    """

    # db objects list
    db_objects: list[SymbologySymbolDb] = []
    outputs: list[SymbologySymbolPublic] = []

    for symbol in symbols:
        # unpack symbology_maps object
        symbology_maps = symbol.symbology_map

        ref_data_uuids = await lookup_ref_data_uuid_given_symbology_maps(
            session=session, symbology_maps=symbology_maps
        )

        if len(ref_data_uuids) == 1:
            # Only one unique ref_data_uuid found, use it
            ref_data_uuid, symbologies_already_in_database = next(
                iter(ref_data_uuids.items())
            )

            if symbology_maps.keys() <= symbologies_already_in_database:
                # All symbologies are already in the database, raise an error
                outputs.append(
                    SymbologySymbolPublic(
                        **symbol.model_dump(),
                        ref_data_uuid=ref_data_uuid,
                        error=(
                            "All symbologies provided for this ref_data_uuid are already in the database. This "
                            "request type can only be used to define new symbologies to an existing ref_data_uuid / "
                            "define new symbol with new ref_data_uuid. Use other method to change existing "
                            "symbologies."
                        ),
                    )
                )

            # filter out symbologies that are already in the database
            symbology_maps = {
                symbology_name: symbology_values
                for symbology_name, symbology_values in symbology_maps.items()
                if symbology_name not in symbologies_already_in_database
            }

        elif len(ref_data_uuids) > 1:
            # Multiple unique ref_data_uuids found, raise an error
            outputs.append(
                SymbologySymbolPublic(
                    **symbol.model_dump(),
                    error=(
                        "Multiple ref_data_uuids have been found for symbols provided, cannot determine which one "
                        "to use. Please verify the request provided."
                    ),
                )
            )
        else:
            # generate new unique ref_data_uuid to each symbol
            ref_data_uuid = generate_ref_data_uuid()

        for symbology_name, symbology_values in symbology_maps.items():
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
    for symbol_create, db_object in zip(symbols, db_objects):
        outputs.append(
            SymbologySymbolPublic(
                **symbol_create.model_dump(),
                ref_data_uuid=db_object.ref_data_uuid,
                message="Symbol created successfully",
            )
        )

    # handle status based on ref_data_uuids / message / error
    if all([x.error is not None for x in outputs]):
        response.status_code = HTTP_400_BAD_REQUEST
    elif any([x.error is not None for x in outputs]):
        response.status_code = HTTP_207_MULTI_STATUS

    return outputs


@router.put("/")
async def change_symbol_history(
    *,
    session: Session = Depends(get_session),
    symbols: list[SymbologySymbolCreate],
    response: Response,
) -> list[SymbologySymbolPublic]:
    raise NotImplementedError
