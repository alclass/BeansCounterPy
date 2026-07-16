#!/usr/bin/env python3
"""
art/bookroutes/packt/mongo/upsertors/renameMongoFields.py
  Given the two CLI (*) parameters 'from_field' and 'to_field',
    this script renames the first field (column) to the second
    in a MongoDB collection.

(*) This script CLI-runs,
    but can also be from a non-CLI caller.

The three parameters below:
  a) MongoDB connection URL
  b) Mongo DB name
  c) Mongo collection name
are config-based.

DEFAULT_FROM_FIELD = 'isbn'
DEFAULT_TO_FIELD = 'isbn13'
"""
import sys
from pymongo import MongoClient
from art.bks.packt import DEFAULT_MONGO_DBNAME
from art.bks.packt import DEFAULT_MONGO_COLLNAME
from art.bks.packt import DEFAULT_LOCAL_MONGO_CONN_URL
DEFAULT_FROM_FIELD = 'author'
DEFAULT_TO_FIELD = 'authors'


def rename_field_from_to(from_field: str, to_field: str):
  # 1. Connect to your MongoDB deployment
  client = MongoClient(DEFAULT_LOCAL_MONGO_CONN_URL)
  # 2. Select your database and collection
  db = client[DEFAULT_MONGO_DBNAME]
  collection = db[DEFAULT_MONGO_COLLNAME]
  # 3. Define the rename operation using the $rename operator
  # Format: {"$rename": {"old_field_name": "new_field_name"}}
  rename_operation = {
      "$rename": {
          f"{from_field}": f"{to_field}"
      }
  }
  # 4. Apply the change to all documents in the collection
  # The empty curly braces {} match every document in the collection
  result = collection.update_many({}, rename_operation)
  # 5. Print the number of documents updated
  print(f"Matched documents: {result.matched_count}")
  print(f"Modified documents: {result.modified_count}")


def get_args():
  from_field, to_field = None, None
  for arg in sys.argv[1:]:
    if arg == "-h" or arg == "--help":
      print(__doc__)
      sys.exit(0)
    elif arg.startswith("-from="):
      from_field = arg[len("-from="):]
    elif arg.startswith("-to="):
      to_field = arg[len("-to="):]
  return from_field, to_field


def process():
  from_field, to_field = get_args()
  if from_field is None:
    from_field = DEFAULT_FROM_FIELD
  if to_field is None:
    to_field = DEFAULT_TO_FIELD
  scrmsg = f"Parameters: from_field = {from_field} | to_field = {to_field}"
  print(scrmsg)
  rename_field_from_to(from_field, to_field)


if __name__ == "__main__":
  # Simple usage
  process()
