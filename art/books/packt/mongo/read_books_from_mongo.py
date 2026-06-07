#!/usr/bin/env python3
"""
art/books/packt/dirwalk/readBooksMetaFromMongo.py
  Reads (Packt) books' metadata from MongoDB

  previously: art/books/packt/mongo/read_books_from_mongo.py
"""
import json
from pymongo import MongoClient
from art.books.packt.dirwalk import DEFAULT_MONGO_DB
from art.books.packt.dirwalk import DEFAULT_MONGO_COLL


class MongoDBCollReader:

  def __init__(self, database_name=None, collection_name=None):
    self.mongo_db = database_name or DEFAULT_MONGO_DB
    self.mongo_coll = collection_name or DEFAULT_MONGO_COLL
    self.cli_conn = None
    self.db = None
    self.collection = None
    self.count = 0
    self.open_conn()

  def open_conn(self):
    self.cli_conn = MongoClient('mongodb://localhost:27017/')
    self.db = self.cli_conn[self.mongo_db]
    self.collection = self.db[self.mongo_coll]
    # Count documents
    self.count = self.collection.count_documents({})
    print(f"Total documents in collection: {self.count}")

  def read_first_5_docs(self):
    # Show first document
    first_doc = self.collection.find_one()
    if first_doc:
        print(f"\nFirst document:\n{json.dumps(first_doc, indent=2, default=str)}")
    # Show all documents (limit to 5)
    print(f"\nFirst 5 documents:")
    for doc in self.collection.find().limit(5):
        print(json.dumps(doc, indent=2, default=str))

  def read_printing_all(self):
    # Show first document
    print(f"\nAll {self.count} documents:")
    for i, doc in enumerate(self.collection.find()):
      seq = i + 1
      print(seq, json.dumps(doc, indent=2, default=str))

  def print_all_records(self):
    # self.read_first_5_docs()
    self.read_printing_all()
    self.close_conn()


  def close_conn(self):
    if self.cli_conn:
      self.cli_conn.close()


def process():
  database_name = DEFAULT_MONGO_DB
  collection_name = DEFAULT_MONGO_COLL
  reader = MongoDBCollReader(database_name, collection_name)
  reader.print_all_records()


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
