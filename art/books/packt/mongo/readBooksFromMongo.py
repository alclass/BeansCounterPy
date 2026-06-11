#!/usr/bin/env python3
"""
art/books/packt/mongo/readBooksFromMongo.py
  Reads (Packt) books' metadata from MongoDB (on localhost)
"""
import json
from pymongo import MongoClient
from art.books.packt import DEFAULT_MONGO_DB
from art.books.packt import DEFAULT_MONGO_COLL


class MongoDBCollReader:

  def __init__(self, database_name=None, collection_name=None):
    self.count = 0
    self.mongo_dbname = database_name or DEFAULT_MONGO_DB
    self.mongo_collname = collection_name or DEFAULT_MONGO_COLL
    self.mongo_db = None
    self.mongo_coll = None
    self.cli_conn = None
    self.open_conn()

  def open_conn(self):
    self.cli_conn = MongoClient('mongodb://localhost:27017/')
    self.mongo_db = self.cli_conn[self.mongo_dbname]
    self.mongo_coll = self.mongo_db[self.mongo_collname]
    # Count documents
    self.count = self.mongo_coll.count_documents({})
    print(f"Total documents in collection: {self.count}")

  def read_first_5_docs(self):
    # Show first document
    first_doc = self.mongo_coll.find_one()
    if first_doc:
        print(f"\nFirst document:\n{json.dumps(first_doc, indent=2, default=str)}")
    # Show all documents (limit to 5)
    print(f"\nFirst 5 documents:")
    for doc in self.mongo_coll.find().limit(5):
        print(json.dumps(doc, indent=2, default=str))

  def retrieve_by_isbn13(self, isbn13):
    bookinfodictlist = []
    docs = self.mongo_coll.find({
      'isbn13': isbn13
    })
    for doc in docs:
      bookinfodict = json.dump(doc)
      bookinfodictlist.append(bookinfodict)
    return bookinfodictlist

  def find_by_isbn13(self, isbn13):
    scrmsg = f"Finding 'isbn13 = {isbn13}"
    print(scrmsg)
    found_ifany = self.mongo_coll.find({
      'isbn13': isbn13
    })
    n_found = 0
    for i, doc in enumerate(found_ifany):
      seq = i + 1
      n_found += 1
      print(seq, json.dumps(doc, indent=2, default=str))
    scrmsg = f"Found {n_found} isbn's"
    print(scrmsg)
    return n_found

  def read_printing_all(self):
    # Show first document
    print(f"\nAll {self.count} documents:")
    for i, doc in enumerate(self.mongo_coll.find()):
      seq = i + 1
      print(seq, json.dumps(doc, indent=2, default=str))

  def print_all_records(self):
    """
      client_caller should close_conn from the 'outside'
        client_caller.close_conn()
    """
    # self.read_first_5_docs()
    self.read_printing_all()

  def close_conn(self):
    if self.cli_conn:
      self.cli_conn.close()


def process():
  """
  database_name = DEFAULT_MONGO_DB
  collection_name = DEFAULT_MONGO_COLL
  MongoDBCollReader(database_name, collection_name)

  reader.print_all_records()
  isbn13 = '9781839213069'  # yet to enter db Mastering Functional JS

  """
  reader = MongoDBCollReader()
  isbn13 = '9781785285493'
  reader.find_by_isbn13(isbn13)
  reader.close_conn()


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
