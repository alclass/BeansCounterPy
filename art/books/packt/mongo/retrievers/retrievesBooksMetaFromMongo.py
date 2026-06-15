#!/usr/bin/env python3
"""
art/books/packt/mongo/retrievers/retrievesBooksMetaFromMongo.py
  Reads/retrieves (Packt) books' metadata from its MongoDB collection

"""
import json
from pymongo import MongoClient
from art.books.packt import DEFAULT_LOCAL_MONGO_CONN_URL
from art.books.packt import DEFAULT_MONGO_DBNAME
from art.books.packt import DEFAULT_MONGO_COLLNAME
from art.books.packt import BookModel


class MongoDBCollectionRetriever:

  def __init__(self, mongo_dbname=None, mongo_collname=None):
    self.bk_count = 0
    self.mongo_count = 0
    self.mongo_dbname = mongo_dbname or DEFAULT_MONGO_DBNAME
    self.mongo_collname = mongo_collname or DEFAULT_MONGO_COLLNAME
    self.mongo_cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.books = []
    self.open_conn()

  @property
  def total_books(self):
    if self.books is None or len(self.books) == 0:
      return 0
    return len(self.books)

  def open_conn(self):
    self.mongo_cli_conn = MongoClient(DEFAULT_LOCAL_MONGO_CONN_URL)
    self.mongo_db = self.mongo_cli_conn[self.mongo_dbname]
    self.mongo_coll = self.mongo_db[self.mongo_collname]
    # Count documents
    self.mongo_count = self.mongo_coll.count_documents({})
    print(f"Total documents in collection: {self.mongo_count}")

  def retrieve_the_first_n_docs(self, n_first):
    """
    # Show first document
    first_doc = self.mongo_coll.find_one()
    if first_doc:
        print(f"\nFirst document:\n{json.dumps(first_doc, indent=2, default=str)}")
    """
    # Show n_first documents
    scrmsg = f"\tRetrieving the {n_first} first documents:"
    print(scrmsg)
    for doc in self.mongo_coll.find().limit(n_first):
        print(json.dumps(doc, indent=2, default=str))

  def retrieve_all(self):
    # Show first document
    print(f"\tRetrieving all {self.mongo_count} documents:")
    for i, doc in enumerate(self.mongo_coll.find()):
      seq = i + 1
      self.bk_count = seq
      # print(seq, json.dumps(doc, indent=2, default=str))
      bm = BookModel.BookInfoDC.create_instance(doc)
      self.books.append(bm)

  def show_books(self):
    self.books.sort(key=lambda b: b.title)
    for i, bm in enumerate(self.books):
      print(i+1, bm)

  def process(self):
    # self.read_first_5_docs()
    self.retrieve_all()
    self.show_books()
    self.close_conn()

  def close_conn(self):
    if self.mongo_cli_conn is not None:
      self.mongo_cli_conn.close()


def process():
  reader = MongoDBCollectionRetriever()
  reader.process()


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
