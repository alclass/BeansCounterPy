#!/usr/bin/env python3
"""
art/immeub/inst/cdutra/aliss_dc_accomp/mdb/writers/renameMongoFields.py
  Renames some fields in a MongoDB collection.
    At this time, it's a run-once script.

"""
import sys
from pymongo import MongoClient
from art.immeub.inst.cdutra.aliss_dc_accomp import IMMEUB_DBNAME
from art.immeub.inst.cdutra.aliss_dc_accomp import ALIS_DEBT_ACC_COLLNAME
from art.immeub.inst.cdutra.aliss_dc_accomp import LOCAL_MONGODB_URI_STR
ren_field_tuplelist = []
ren_field_tuple = ("_finvalue_d2", "finvalue_d2")
ren_field_tuplelist.append(ren_field_tuple)
ren_field_tuple = ("_inivalue_d2", "inivalue_d2")
ren_field_tuplelist.append(ren_field_tuple)
ren_field_tuple = ("_finvalue_res", "finvalue_res")
ren_field_tuplelist.append(ren_field_tuple)
ren_field_tuple = ("_inivalue_res", "inivalue_res")
ren_field_tuplelist.append(ren_field_tuple)


def rename_fields():
  # 1. Connect to your MongoDB deployment
  client = MongoClient(LOCAL_MONGODB_URI_STR)
  # 2. Select your database and collection
  db = client[IMMEUB_DBNAME]
  collection = db[ALIS_DEBT_ACC_COLLNAME]
  # 3. Define the rename operation using the $rename operator
  # Format: {"$rename": {"old_field_name": "new_field_name"}}
  for i_ren_field_tuple in ren_field_tuplelist:
    from_field, to_field = i_ren_field_tuple
    rename_operation = {
        "$rename": {
            f"{from_field}": f"{to_field}"
        }
    }
    # 4. Apply the change to all documents in the collection
    # The empty curly braces {} match every document in the collection
    result = collection.update_many({}, rename_operation)
    # 5. Print the number of documents updated
    print("rename_operation", rename_operation)
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
  rename_fields()


if __name__ == "__main__":
  # Simple usage
  process()
