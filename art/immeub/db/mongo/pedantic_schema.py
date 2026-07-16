#!/usr/bin/env python3
"""
art/immeub/db/mongo/schema.py

Verification

You can check if your schema uploaded correctly
  by opening your terminal and using the MongoDB Shell (mongosh):
  # ========
  # mongosh
  use my_local_database
  db.getCollectionInfos({name: "users"})
  # ========

"""
from pymongo import MongoClient
import art.immeub.db.mongo.__init__ as init  # .__init__
DEFAULT_MONGO_URL_STR = init.DEFAULT_MONGO_URL_STR
immeub_db = init.DEFAULT_MNG_IMMEUB_DB
cobrancas_coll = init.DEFAULT_MNG_COBRANCACOLL
billingitems_coll = init.DEFAULT_MNG_BILLINGITEMCOLL
contracts_coll = init.DEFAULT_MNG_CONTRACTCOLL
persons_coll = init.DEFAULT_MNG_PERSONCOLL
immeubs_coll = init.DEFAULT_MNG_IMMEUBCOLL
# Connect to local instance
client = MongoClient("mongodb://localhost:27017/")
db = client["immeub_db"]
user_schema = {}
# Define validation rules using JSON schema syntax
import asyncio
from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field, EmailStr


# Define the schema as a Python class
class User(Document):
  username: str
  email: EmailStr
  age: int = Field(ge=18)  # Age must be >= 18

  class Settings:
    name = "users"  # Collection name in MongoDB


async def init_db():
  # Connect to localhost
  iclient = AsyncIOMotorClient("mongodb://localhost:27017")
  # Initialize Beanie with your document models
  await init_beanie(database=iclient.my_local_database, document_models=[User])
  # Upload/Save a document to test it
  new_user = User(username="johndoe", email="john@example.com", age=25)
  await new_user.insert()
  print("User saved successfully!")


# Run the async loop
asyncio.run(init_db())


def adhoctest1():
  print(user_schema)
  pass


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
