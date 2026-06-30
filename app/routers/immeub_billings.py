# app/routers/immeub_billings.py
from fastapi import APIRouter
router = APIRouter()


@router.get("/")
async def get_all_immeubs():
    return [{"immeub_id": 1, "nickname": "CDutra"}]


@router.get("/{immeub_id}")
async def get_immeub(immeub_id: int):
    return {"immeub_id": immeub_id, "nickname": "CDutra"}


@router.get("/{immeub_nick}/{refmonthdate}")
async def get_immeub_bill_f_month(immeub_nick: str, refmonthdate: str ):
    return {"immeub_nick": immeub_nick, "refmonthdate": refmonthdate}
