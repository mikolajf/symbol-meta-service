from fastapi import APIRouter

from app.schemas import SymbologySymbolCreate

router = APIRouter(
    prefix="/symbols",
    tags=["symbols"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_all_symbols():
    return {}


@router.post("/")
async def create_symbol(symbol: SymbologySymbolCreate):
    return symbol
