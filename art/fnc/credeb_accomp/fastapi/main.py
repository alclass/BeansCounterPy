"""
art/fnc/credeb_accomp/fastapi/main.py

my_project/
├── main.py          # FastAPI Backend
└── templates/
    └── index.html   # Frontend Client-side

pip install fastapi uvicorn motor jinja2 pydantic
uvicorn main:app --reload --port 8000

For reolading the app when it's changed:
    $ fastapi dev app/fastapi_main.py
    $ uvicorn main:app.fastapi_main --reload

uvicorn main:art.fnc.credeb_accomp.fastapi --reload
fastapi dev art/fnc/credeb_accomp/fastapi/main.py

Open in Browser:
Go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
  to view and interact with your responsive local CRUD UI.
"""
import pprint
from datetime import date
import datetime
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, FastAPI
router = APIRouter()
import art.fnc.credeb_accomp.mdb as mdb
import art.fnc.credeb_accomp as cd_init
import art.fnc.credeb_accomp.credeb_accompanying_mod as cd_accomp
import art.fnc.credeb_accomp.mdb.readers.mongo_reader_refmonths as mngr  # mngr.MongoDBCollectionRetriever
import lib.datesetc.refmonth_fs as rmfs
# templates = Jinja2Templates(directory="templates")
# Default constant mirroring DIN_META_MENSAL
import art.fnc.credeb_accomp.fastapi.models.credeb_pydanticmodels as pydtc  # pydtc.trnsf_credeb_dataclass_objs_to_pydantic
app = FastAPI(title="DebCredAccompanier CRUD App")


def helper_document(doc) -> dict:
  """Transforms MongoDB document to match response schema."""
  doc["id"] = str(doc["_id"])
  del doc["_id"]
  return doc


# --- Frontend Route ---
@app.get("/")
async def get_all_refmonth_slips():
  mfetcher = mngr.MongoDBCollectionRetriever()
  objs = mfetcher.fetch_all_as_objs()
  pydantics = pydtc.trnsf_credeb_dataclass_objs_to_pydantic(objs)
  return pydantics


@app.get("/{p_refmonth}")
async def get_monthly_slip(p_refmonth: str):
  refmonth = rmfs.make_refmonth_or_none(p_refmonth)
  if refmonth is None:
    return {}
  mfetcher = mngr.MongoDBCollectionRetriever()
  slip = mfetcher.find_by_refmonth_as_obj(refmonth)
  pydantic_obj = pydtc.trnsf_credeb_dataclass_obj_to_pydantic(slip)
  return pydantic_obj


def adhoctest1():
  d = Decimal(0)
  print(d)


def cli_show_records():
  mfetcher = mngr.MongoDBCollectionRetriever()
  objs = mfetcher.fetch_all_as_objs()
  pydantics = pydtc.trnsf_credeb_dataclass_objs_to_pydantic(objs)
  for i, o in enumerate(pydantics):
    seq = i + 1
    print(seq)
    pprint.pprint(o)
  slip = mfetcher.find_by_refmonth_as_obj('2026-5')
  print('slip =>', slip)



def process():
  """
  """
  cli_show_records()


if __name__ == '__main__':
  """
  adhoctest1()
  """
  process()
