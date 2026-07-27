"""
art/immeub/inst/cdutra/credeb_accomp_pkg/fastapi/main.py

my_project/
├── main.py          # FastAPI Backend
└── templates/
    └── index.html   # Frontend Client-side

pip install fastapi uvicorn motor jinja2 pydantic
uvicorn main:app --reload --port 8000

For reolading the app when it's changed:
    $ fastapi dev app/fastapi_main.py
    $ uvicorn main:app.fastapi_main --reload

uvicorn main:art.immeub.inst.cdutra.credeb_accomp_pkg.fastapi --reload
fastapi dev art/immeub/inst/cdutra/credeb_accomp_pkg/fastapi/main.py

Open in Browser:
Go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
  to view and interact with your responsive local CRUD UI.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

app = FastAPI(title="DebCredAccompanier CRUD App")

# MongoDB connection setup (adjust URI/database name as needed for your local setup)
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.get_database("your_database_name")  # Replace with your DB name
collection = database.get_collection("debcred_collection")  # Replace with your Collection name

templates = Jinja2Templates(directory="templates")

# Default constant mirroring DIN_META_MENSAL
DEFAULT_DIN_META_MENSAL = Decimal("5000.00")


# Pydantic Schemas
class DebCredBase(BaseModel):
  refmonth: date
  inivalue_d1: Decimal
  inivalue_d2: Decimal
  inivalue_res: Decimal
  cre_in_tasks: Decimal
  cre_in_pay: Decimal
  cre_in_trnsp_n_frut: Decimal
  deb_giro: Decimal
  valor_meta_no_mes: Decimal = DEFAULT_DIN_META_MENSAL


class DebCredCreate(DebCredBase):
  pass


class DebCredUpdate(BaseModel):
  refmonth: Optional[date] = None
  inivalue_d1: Optional[Decimal] = None
  inivalue_d2: Optional[Decimal] = None
  inivalue_res: Optional[Decimal] = None
  cre_in_tasks: Optional[Decimal] = None
  cre_in_pay: Optional[Decimal] = None
  cre_in_trnsp_n_frut: Optional[Decimal] = None
  deb_giro: Optional[Decimal] = None
  valor_meta_no_mes: Optional[Decimal] = None


class DebCredResponse(DebCredBase):
  id: str
  _corrmone_n_intrst_if_any: Optional[Decimal] = None
  _ipca_dec: Optional[Decimal] = None
  finvalue_d1: Optional[Decimal] = None
  finvalue_d2: Optional[Decimal] = None
  finvalue_res: Optional[Decimal] = None
  updt_saldos_has_run: bool = False
  is_closed_n_in_db: bool = False


def helper_document(doc) -> dict:
  """Transforms MongoDB document to match response schema."""
  doc["id"] = str(doc["_id"])
  del doc["_id"]
  return doc


# --- Frontend Route ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
  return templates.TemplateResponse("index.html", {"request": request})


# --- CRUD Endpoints ---

@app.post("/api/records/", response_model=DebCredResponse)
async def create_record(record: DebCredCreate):
  data = record.dict()
  # Mocking basic backend calculation steps corresponding to __post_init__ logic
  data["finvalue_d1"] = data["inivalue_d1"] + data["cre_in_tasks"]
  data["finvalue_d2"] = data["inivalue_d2"] + data["cre_in_pay"]
  data["finvalue_res"] = data["inivalue_res"] + data["cre_in_trnsp_n_frut"] - data["deb_giro"]
  data["updt_saldos_has_run"] = True
  data["is_closed_n_in_db"] = False

  result = await collection.insert_one(data)
  created_doc = await collection.find_one({"_id": result.inserted_id})
  return helper_document(created_doc)


@app.get("/api/records/", response_model=List[DebCredResponse])
async def get_records():
  records = []
  async for doc in collection.find():
    records.append(helper_document(doc))
  return records


@app.get("/api/records/{id}", response_model=DebCredResponse)
async def get_record(id: str):
  from bson import ObjectId
  doc = await collection.find_one({"_id": ObjectId(id)})
  if doc:
    return helper_document(doc)
  raise HTTPException(status_code=404, detail="Record not found")


@app.put("/api/records/{id}", response_model=DebCredResponse)
async def update_record(id: str, record: DebCredUpdate):
  from bson import ObjectId
  update_data = {k: v for k, v in record.dict(exclude_unset=True).items() if v is not None}

  if not update_data:
    raise HTTPException(status_code=400, detail="No fields provided for update")

  # Recalculate fields if primary components change
  update_data["updt_saldos_has_run"] = True

  result = await collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
  if result.modified_count == 0:
    # Check if document exists even if values didn't change
    existing = await collection.find_one({"_id": ObjectId(id)})
    if not existing:
      raise HTTPException(status_code=404, detail="Record not found")

  updated_doc = await collection.find_one({"_id": ObjectId(id)})
  return helper_document(updated_doc)


@app.delete("/api/records/{id}")
async def delete_record(id: str):
  from bson import ObjectId
  result = await collection.delete_one({"_id": ObjectId(id)})
  if result.deleted_count == 1:
    return {"message": "Record successfully deleted"}
  raise HTTPException(status_code=404, detail="Record not found")
