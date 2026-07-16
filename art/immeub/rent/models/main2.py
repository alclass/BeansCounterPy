#!/usr/bin/env python3
"""
art/immeub/rent/models/main2.py

For reolading the app when it's changed:
    $ fastapi dev art/immeub/rent/models/main.py
    $ uvicorn main:art.immeub.rent.models.main --reload

Fixing the Code IssuesHere is why your code hit
  those walls and how we are fixing them:i1)
  MotorDatabase TypeError:
  This happens because of a version mismatch between
  Beanie and Motor (or a typo in initialization)
  where Beanie expects a MotorDatabase instance
  but accidentally tries to call metadata append
  methods on the database object instead of the root MotorClient.
  We fix this by extracting the database cleanly using
  client.get_database("db_name") or directly using
  the client attribute client.real_estate_db.
"""
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from beanie import Document, Link, init_beanie
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


# ==========================================
# MODERN LIFESPAN INITIALIZATION (Fixes i2)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
  # Establish local connection
  client = AsyncIOMotorClient("mongodb://localhost:27017")

  # Target database cleanly (Fixes i1 metadata/type error)
  database = client.get_database("real_estate_simplified")

  # Initialize Beanie with our stripped down two models
  await init_beanie(database=database, document_models=[Tenant, Contract])
  yield
  # Cleanup on shutdown (if needed) can go here


app = FastAPI(title="Simplified Real Estate API", lifespan=lifespan)

# Allow JavaScript frontend interaction
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# ==========================================
# MONGO DOCUMENTS (Simplified Models)
# ==========================================
class Tenant(Document):
  name: str
  email: str

  class Settings:
    name = "tenants"


class Contract(Document):
  contract_number: str
  # Relational connection to Tenants
  tenants: List[Link[Tenant]]

  class Settings:
    name = "contracts"


# ==========================================
# PYDANTIC REQ BODIES (No Complex IDs for Client)
# ==========================================
class ContractCreateRequest(BaseModel):
  contract_number: str
  tenant_ids: List[str] = Field(..., description="Array of string hexadecimal IDs")


# ==========================================
# API ROUTING (Endpoints)
# ==========================================

# Seed / Manage Tenants
@app.post("/tenants", response_model=Tenant)
async def create_tenant(tenant: Tenant):
  return await tenant.insert()


@app.get("/tenants")
async def list_tenants():
  return await Tenant.find_all().to_list()


# Contract Core Engine
@app.post("/contracts", status_code=status.HTTP_201_CREATED)
async def create_contract(payload: ContractCreateRequest):
  tenant_documents = []

  for t_id in payload.tenant_ids:
    if not ObjectId.is_valid(t_id):
      raise HTTPException(status_code=400, detail=f"Malformed Hex ID: {t_id}")

    tenant = await Tenant.get(t_id)
    if not tenant:
      raise HTTPException(status_code=404, detail=f"Tenant ID {t_id} missing in DB")

    tenant_documents.append(tenant)

  # Beanie handles turning Document objects into Link wrappers automatically
  new_contract = Contract(
    contract_number=payload.contract_number,
    tenants=tenant_documents
  )
  await new_contract.insert()
  return {"message": "Contract established", "id": str(new_contract.id)}


@app.get("/contracts")
async def list_contracts():
  contracts = await Contract.find_all().to_list()
  for contract in contracts:
    # Resolves Link[Tenant] -> Tenant instances seamlessly
    await contract.fetch_links()
  return contracts


@app.delete("/contracts/{contract_id}")
async def delete_contract(contract_id: str):
  if not ObjectId.is_valid(contract_id):
    raise HTTPException(status_code=400, detail="Malformed contract ID")
  contract = await Contract.get(contract_id)
  if not contract:
    raise HTTPException(status_code=404, detail="Contract not found")
  await contract.delete()
  return {"message": "Contract deleted successfully"}
