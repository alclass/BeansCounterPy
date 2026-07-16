"""
art/immeub/rent/models/main3.py
  This is the 3rd attempt to roll up a FastAPI server
  This time we replaced Beanie and Motor with mongoengine
  It's working and the async/await systematic was not impacted

"""
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bson import ObjectId  # , errors
from mongoengine import connect, disconnect, Document, StringField, ReferenceField, PULL, ListField
import art.immeub.rent.db as init  #
DEFAULT_MONGO_URLCONNSTR = init.DEFAULT_MONGO_URLCONNSTR
IMMEUB_MNGDBNAME = init.IMMEUB_MNGDBNAME
PERSON_MNGCOLLNAME = init.PERSON_MNGCOLLNAME
CONTRACT_MNGCOLLNAME = init.CONTRACT_MNGCOLLNAME


# ==========================================
# MONGOENGINE ODM LAYOUT (Synchronous)
# ==========================================
class Tenant(Document):
  """
  TODO In fact, Tenant should inherit from Person
  """
  name = StringField(required=True)
  email = StringField(required=True)

  meta = {'collection': PERSON_MNGCOLLNAME}

  # Helper method to match the standard MongoDB/Beanie JSON output
  def to_api_dict(self):
    return {
      "_id": str(self.id),
      "name": self.name,
      "email": self.email
    }


class Contract(Document):
  contract_number = StringField(required=True)
  # ReferenceField handles foreign-key references.
  # reverse_delete_rule=PULL automatically updates the contract if a tenant is deleted.
  tenants = ListField(ReferenceField(Tenant, reverse_delete_rule=PULL))

  meta = {'collection': CONTRACT_MNGCOLLNAME}

  def to_api_dict(self):
    return {
      "_id": str(self.id),
      "contract_number": self.contract_number,
      # Resolves the relational loop into plain objects like fetch_links() did
      "tenants": [tenant.to_api_dict() for tenant in self.tenants if tenant]
    }


# ==========================================
# LIFESPAN MANAGEMENT (Fixes Deprecation Warnings)
# ==========================================
@asynccontextmanager
async def lifespan(p_app: FastAPI):
  # Establish synchronous connection to your local MongoDB
  _ = p_app
  connect(db=IMMEUB_MNGDBNAME, host=DEFAULT_MONGO_URLCONNSTR)
  yield
  # Safely close connection pool on application shutdown
  disconnect()


app = FastAPI(title="FastAPI + MongoEngine Sync API", lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# ==========================================
# PYDANTIC REQ BODIES (Kept exactly identical)
# ==========================================
class ContractCreateRequest(BaseModel):
  contract_number: str
  tenant_ids: List[str] = Field(..., description="Array of string hexadecimal IDs")


# ==========================================
# API ROUTING (Synchronous implementations)
# ==========================================

# Seed / Manage Tenants
@app.post("/tenants", status_code=status.HTTP_201_CREATED)
def create_tenant(payload: BaseModel):
  # Dynamically extract data to avoid Pydantic conflict on MongoEngine objects
  data = payload.model_dump() if hasattr(payload, 'model_dump') else payload.model_dump()
  tenant = Tenant(name=data.get("name"), email=data.get("email")).save()
  return tenant.to_api_dict()


@app.get("/tenants")
def list_tenants():
  # Fetch all tenants from local MongoDB
  return [tenant.to_api_dict() for tenant in Tenant.objects]


# Contract Engine
@app.post("/contracts", status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreateRequest):
  tenant_documents = []

  for t_id in payload.tenant_ids:
    if not ObjectId.is_valid(t_id):
      raise HTTPException(status_code=400, detail=f"Malformed Hex ID: {t_id}")

    # Look up tenant document synchronously
    tenant = Tenant.objects(id=t_id).first()
    if not tenant:
      raise HTTPException(status_code=44, detail=f"Tenant ID {t_id} missing in DB")

    tenant_documents.append(tenant)

  # Instantiate and save contract reference
  new_contract = Contract(
    contract_number=payload.contract_number,
    tenants=tenant_documents
  ).save()

  return {"message": "Contract established", "id": str(new_contract.id)}


@app.get("/contracts")
def list_contracts():
  # Loop over all contracts. Calling `.to_api_dict()` automatically
  # traverses and dereferences linked Tenant profiles.
  return [contract.to_api_dict() for contract in Contract.objects]


@app.delete("/contracts/{contract_id}")
def delete_contract(contract_id: str):
  if not ObjectId.is_valid(contract_id):
    raise HTTPException(status_code=400, detail="Malformed contract ID")

  contract = Contract.objects(id=contract_id).first()
  if not contract:
    raise HTTPException(status_code=404, detail="Contract not found")

  contract.delete()
  return {"message": "Contract deleted successfully"}
