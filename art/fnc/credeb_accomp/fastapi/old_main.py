from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel


@app.get("/nonexists", response_class=HTMLResponse)
async def read_root(request: Request):
  return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{refmonth}", response_class=HTMLResponse)
async def read_root(request: Request):
  return templates.TemplateResponse("index.html", {"request": request})


# --- CRUD Endpoints ---

@app.post("/api/records/", response_model=DebCredResponse)
async def create_record(record: DebCredCreate):
  data = record.model_dump()  # formerly record.dict()
  dataclass_o = cd_accomp.DebCredAccompanier.instantiate_fr_dict(data)
  data["ipca_dec"] = dataclass_o.ipca_dec
  data["fix_ir_dec"] = dataclass_o.fix_ir_dec
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
async def get_record(_id: str):
  from bson import ObjectId
  doc = await collection.find_one({"_id": ObjectId(_id)})
  if doc:
    return helper_document(doc)
  raise HTTPException(status_code=404, detail="Record not found")


@app.put("/api/records/{id}", response_model=DebCredResponse)
async def update_record(_id: str, record: DebCredUpdate):
  from bson import ObjectId
  update_data = {k: v for k, v in record.model_dump(exclude_unset=True).items() if v is not None}

  if not update_data:
    raise HTTPException(status_code=400, detail="No fields provided for update")

  # Recalculate fields if primary components change
  update_data["updt_saldos_has_run"] = True

  result = await collection.update_one({"_id": ObjectId(_id)}, {"$set": update_data})
  if result.modified_count == 0:
    # Check if document exists even if values didn't change
    existing = await collection.find_one({"_id": ObjectId(_id)})
    if not existing:
      raise HTTPException(status_code=404, detail="Record not found")

  updated_doc = await collection.find_one({"_id": ObjectId(_id)})
  return helper_document(updated_doc)


@app.delete("/api/records/{id}")
async def delete_record(_id: str):
  from bson import ObjectId
  result = await collection.delete_one({"_id": ObjectId(_id)})
  if result.deleted_count == 1:
    return {"message": "Record successfully deleted"}
  raise HTTPException(status_code=404, detail="Record not found")
