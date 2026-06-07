#!/usr/bin/env python3
"""
<<<<<<< HEAD
art/books/packt/dirwalk/mongodb_write_functions.py
=======
art/books/packt/dirwalk/jsonToMongoReadWriteFunctions.py
>>>>>>> 91d06ab3b1f9fdb943a436ad7badc16df437feee
  Explanation?
    (...)

"""
from pymongo import MongoClient


def mongo_conn_str():
  return "mongodb://localhost:27017"


class MongoDBUpsertor:

  def __init__(self, jsonlist, mongo_db=None, mongo_coll=None):
    self.jsonlist = jsonlist
    self.mongo_db = mongo_db
    self.mongo_coll = mongo_coll
    self.client = MongoClient(mongo_conn_str())

  def upsert(self, document):
    # Inserts the document only if the email does not exist
    result = self.mongo_coll.update_one(
      document,
      upsert=True
    )
    if result.upserted_id is not None:
      print(f"Inserted new document with ID: {result.upserted_id}")
    else:
      print("Document already existed and was updated.")
