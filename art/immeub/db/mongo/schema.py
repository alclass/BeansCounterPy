#!/usr/bin/env python3
"""
art/immeub/db/mongo/schema.py

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
contracts_schema = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["immeub_nn", "tenants", "inidate", "curvalue"],
    "properties": {
      "username": {
        "bsonType": "string",
        "description": "must be a string and is required"
      },
      "email": {
        "bsonType": "string",
        "pattern": "^.+@.+$",
        "description": "must be a valid email string and is required"
      },
      "age": {
        "bsonType": "int",
        "minimum": 18,
        "description": "must be an integer greater than or equal to 18"
      }
    }
  }
}

person_schema = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "fullname", "address", "cpf", "id_alt", "immeub_id",
      "email", "email_alt", "profession", "rentcomment", "obs",
    ],
    "properties": {
      "username": {
        "bsonType": "string",
        "description": "must be a string and is required"
      },
      "email": {
        "bsonType": "string",
        "pattern": "^.+@.+$",
        "description": "must be a valid email string and is required"
      },
      "age": {
        "bsonType": "int",
        "minimum": 18,
        "description": "must be an integer greater than or equal to 18"
      }
    }
  }
}

immeub_schema = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["immeub_nn", "address", "physchars", "nonphysdetails"],
    "properties": {
      "username": {
        "bsonType": "string",
        "description": "must be a string and is required"
      },
      "email": {
        "bsonType": "string",
        "pattern": "^.+@.+$",
        "description": "must be a valid email string and is required"
      },
      "age": {
        "bsonType": "int",
        "minimum": 18,
        "description": "must be an integer greater than or equal to 18"
      }
    }
  }
}

cobrancas_schema = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "immeub_nn", "refmonth", "readydate", "duedate",
      "billing_items", "payments", "total", "comments", "closedate",
    ],
    "properties": {
      "username": {
        "bsonType": "string",
        "description": "must be a string and is required"
      },
      "email": {
        "bsonType": "string",
        "pattern": "^.+@.+$",
        "description": "must be a valid email string and is required"
      },
      "age": {
        "bsonType": "int",
        "minimum": 18,
        "description": "must be an integer greater than or equal to 18"
      }
    }
  }
}


def create_colls():
  # Create collection with the schema enforced
  try:
    db.create_collection(cobrancas_coll, validator=cobrancas_schema)
    print("Collection created with schema validation!")
  except Exception as e:
    print(f"Collection might already exist or error occurred: {e}")


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


