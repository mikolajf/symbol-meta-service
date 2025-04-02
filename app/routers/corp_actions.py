from fastapi import APIRouter, Depends
from sqlmodel import select, Session
from starlette.status import HTTP_201_CREATED

from app.dependencies import get_session
from app.schemas import SymbologySymbolDb
from app.schemas.corp_actions import (
    CorpAction,
    CorpActionCreate,
    CorpActionPublic,
    CorpActionDb,
)

router = APIRouter(
    prefix="/corpActions",
    tags=["corpActions"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_all_corp_actions(
    *, session: Session = Depends(get_session)
) -> list[CorpAction]:
    statement = select(CorpAction)
    results = session.exec(statement)
    all_corp_actions = results.all()

    return all_corp_actions


@router.post("/", status_code=HTTP_201_CREATED)
def create_corp_action(
    *, session: Session = Depends(get_session), corp_action: CorpActionCreate
) -> list[CorpActionPublic]:
    db_objects: list[CorpActionDb] = []
    if corp_action.ref_data_uuid is None:
        # lookup ref_data_uuid using (symbology, symbol) pair
        statement = select(SymbologySymbolDb).where(
            SymbologySymbolDb.symbol == corp_action.symbol,
            SymbologySymbolDb.symbology == corp_action.symbology,
            SymbologySymbolDb.start_time <= corp_action.effective_date,
            SymbologySymbolDb.end_time >= corp_action.effective_date,
        )

        results = session.exec(statement)
        # TODO <MFido> [02/04/2025] we use .all() here with the assumption (to be reviewed) that more than one symbol
        #  can be found, either get rid of this assumption (and replace with .one() or document explicitly
        all_symbols: list[SymbologySymbolDb] = results.all()

        if not all_symbols:
            msg = f"No symbol found for {corp_action.symbology} {corp_action.symbol} on {corp_action.effective_date}"
            return [CorpActionPublic(**corp_action.model_dump(), error=msg)]

        # collect unique ref_data_uuids
        ref_data_uuids = set([symbol.ref_data_uuid for symbol in all_symbols])

        for uuid in ref_data_uuids:
            db_object = CorpActionDb(**corp_action.model_dump(), ref_data_uuid=uuid)

            session.add(db_object)
            db_objects.append(db_object)

    else:
        # TODO <MFido> [02/04/2025] below is wrong. check if such ref_data_uuid exists first
        # in this case there is no need to lookup ref_data_uuid
        # there is only one corp action to create
        db_object = CorpActionDb(**corp_action.model_dump())
        session.add(db_object)
        db_objects.append(db_object)

    session.commit()

    output: list[CorpActionPublic] = []
    # below refreshes the db_objects with the latest db values
    for obj in db_objects:
        session.refresh(obj)
        public_obj = CorpActionPublic(
            **obj.model_dump(), message="Corporate Action created successfully."
        )
        output.append(public_obj)

    return output
