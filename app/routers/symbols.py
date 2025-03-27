from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.internal.id_generator import generate_ref_data_uuid
from app.dependencies import get_session
from app.schemas import SymbologySymbolCreate, SymbologySymbolDb, SymbologySymbolPublic

router = APIRouter(
    prefix="/symbols",
    tags=["symbols"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_all_symbols():
    return {}


@router.post("/")
async def create_symbol(
    *, session: Session = Depends(get_session), symbols: list[SymbologySymbolCreate]
) -> list[SymbologySymbolPublic]:
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
