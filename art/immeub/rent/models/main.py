#!/usr/bin/env python3
"""
art/immeub/rent/models/main.py

For reolading the app when it's changed:
    $ fastapi dev art/immeub/rent/models/main.py
    $ uvicorn main:art.immeub.rent.models.main --reload

Here is the complete implementation for your FastAPI
  application. It includes the API request structures (schemas),
  endpoints for data injection, automatic link resolution,
  and a fully functional, self-contained HTML/JavaScript frontend.

1. Pydantic Request Schemas & FastAPI Routes (main.py)

To keep API users from dealing with complex MongoDB IDs,
  we create Request Schemas that accept simple string representations
  of IDs or data payloads.

For item (c), Beanie handles the conversion automatically:
  when you call await contract.fetch_links(),
  Beanie transforms the Link[Document] wrapper into
  the actual Python object instance dynamically.

"""
import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dinero import Dinero
from typing import List, Optional
from pydantic import BaseModel, Field
from beanie import Document, Link, init_beanie
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI(title="Real Estate Async API")

# Allow CORS for browser frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)








# ==========================================
# PYDANTIC API REQUEST BODIES (Item B)
# ==========================================
class ContractCreateRequest(BaseModel):
    contract_number: str
    location_id: str = Field(..., description="The string hexadecimal ID of the Location")
    tenant_ids: List[str] = Field(..., description="List of string hexadecimal IDs of the People")

# ==========================================
# LIFECYCLE (DB INITIALIZATION)
# ==========================================
@app.on_event("startup")
async def startup_event():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.real_estate_db, document_models=[Person, Location, Contract])

# ==========================================
# API ENDPOINTS (Item A)
# ==========================================

# Helper endpoints to seed background data
@app.post("/persons", response_model=Person)
async def create_person(person: Person):
    return await person.insert()

@app.get("/persons")
async def get_persons():
    return await Person.find_all().to_list()

@app.post("/locations", response_model=Location)
async def create_location(location: Location):
    return await location.insert()

@app.get("/locations")
async def get_locations():
    return await Location.find_all().to_list()

# Contract CRUD
@app.post("/contracts", status_code=status.HTTP_201_CREATED)
async def create_contract(payload: ContractCreateRequest):
    # 1. Verify and fetch the location document
    if not ObjectId.is_valid(payload.location_id):
        raise HTTPException(status_code=400, detail="Invalid location_id format")
    location = await Location.get(payload.location_id)
    if not location:
        raise HTTPException(status_code=44, detail="Location not found")

    # 2. Verify and fetch all tenant documents
    tenant_documents = []
    for t_id in payload.tenant_ids:
        if not ObjectId.is_valid(t_id):
            raise HTTPException(status_code=400, detail=f"Invalid tenant_id format: {t_id}")
        person = await Person.get(t_id)
        if not person:
            raise HTTPException(status_code=404, detail=f"Person with ID {t_id} not found")
        tenant_documents.append(person)

    # 3. Create document (Beanie auto-converts Documents into Links)
    new_contract = Contract(
        contract_number=payload.contract_number,
        location=location,
        tenants=tenant_documents
    )
    await new_contract.insert()
    return {"message": "Contract created successfully", "id": str(new_contract.id)}

@app.get("/contracts")
async def list_contracts():
    contracts = await Contract.find_all().to_list()
    # Item C: Resolving Link wrappers into full model instances
    for contract in contracts:
        await contract.fetch_links()
    return contracts

@app.delete("/contracts/{contract_id}")
async def delete_contract(contract_id: str):
    if not ObjectId.is_valid(contract_id):
        raise HTTPException(status_code=400, detail="Invalid contract ID format")
    contract = await Contract.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    await contract.delete()
    return {"message": "Contract deleted successfully"}
