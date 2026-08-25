#!/usr/bin/env python3
"""
art/immeub/rent/mdb/mongofs.py
  MongoDB (reading) functions.

import art.immeub.rent.mdb.mongofs as mngfs  # .RentMongo
"""
import json
from pymongo import MongoClient
from art.immeub.rent.mdb import MONGODB_CON_STR
from art.immeub.rent.mdb import IMMEUB_DBNAME
from art.immeub.rent.mdb import BILLINGCARD_COLLNAME


def remove_none_values_fr_dict_recurs(data):
  odata = {}
  for k, v in data.items():
    if v is None:
      continue
    if isinstance(v, dict):
      v = remove_none_values_fr_dict_recurs(v)
    odata[k] = v
  return odata


class RentMongo:

  def __init__(
      self,
      mongo_dbname=None, mongo_collname=None, mongo_constr=None,
    ):
    self.bk_count = 0
    self.mongo_count = 0
    self.mongo_constr = mongo_constr or LOCAL_MONGO_CONSTR
    self.mongo_dbname = mongo_dbname or IMMEUB_MNGDBNAME
    self.mongo_collname = mongo_collname or COBRANCA_MNGCOLLNAME
    self.mongo_cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.books = None  # to signal for fetch_all_n_store()
    # self.open_conn()

  @property
  def total_books(self):
    if self.books is None or len(self.books) == 0:
      return 0
    return len(self.books)

  def open_conn(self):
    self.mongo_cli_conn = MongoClient(self.mongo_constr)
    self.mongo_db = self.mongo_cli_conn[self.mongo_dbname]
    self.mongo_coll = self.mongo_db[self.mongo_collname]
    # Count documents
    self.mongo_count = self.mongo_coll.count_documents({})
    # print(f"Total documents in collection: {self.mongo_count}")

  def retrieve_the_first_n_docs(self, n_first):
    """
    # Show first document
    first_doc = self.mongo_coll.find_one()
    if first_doc:
        print(f"\nFirst document:\n{json.dumps(first_doc, indent=2, default=str)}")
    """
    # Show n_first documents
    self.open_conn()
    scrmsg = f"\tRetrieving the {n_first} first documents:"
    print(scrmsg)
    for doc in self.mongo_coll.find().limit(n_first):
        print(json.dumps(doc, indent=2, default=str))
    self.close_conn()

  def find_by_isbn13(self, isbn13):
    self.open_conn()
    isbn_query = {"isbn13": isbn13}
    doc = self.mongo_coll.find_one(isbn_query)
    bookmeta, bm = None, None
    if doc is not None:
      bm = BookModel.BookInfoDC.create_instance(doc)
      if bm is not None:
        bookmeta = bm.to_json
    self.close_conn()
    return bookmeta or {}

  def retrieve_all_as_json(self):
    """
    It is not necessary to convert the object to json
      at this point. FastAPI does it "automatically"
      when it returns a list of dict's
    """
    if self.books is None:
      self.fetch_all_n_store()
    json_list = []
    self.open_conn()
    for i, bm in enumerate(self.books):
      json_list.append(bm)
    self.open_conn()
    return json_list

  def fetch_all_n_store(self):
    """
    self.bookroutes = []  # initially self.bookroutes is None
    Also this method should not run more than once,
      except if a refreshing scheme is created
    """
    self.books = []  # initially self.bookroutes is None
    # print(f"\tRetrieving all {self.mongo_count} documents:")
    self.open_conn()
    for i, doc in enumerate(self.mongo_coll.find()):
      seq = i + 1
      self.bk_count = seq
      # print(seq, json.dumps(doc, indent=2, default=str))
      bm = BookModel.BookInfoDC.create_instance(doc)
      self.books.append(bm)
    self.close_conn()

  def cli_show_books(self):
    if self.books is None:
      self.fetch_all_n_store()
    if self.books is None or len(self.books) == 0:
      return
    self.books.sort(key=lambda b: b.title)
    for i, bm in enumerate(self.books):
      print(i+1, bm)

  def process(self):
    # self.read_first_5_docs()
    self.fetch_all_n_store()
    self.cli_show_books()
    self.close_conn()

  def close_conn(self):
    if self.mongo_cli_conn is not None:
      self.mongo_cli_conn.close()


def adhoc_test1():
  """
  isbn13 = "9781789532227"
  9781785282355
  """
  isbn13 = "9781785282355"
  reader = MongoDBCollectionRetriever()
  bookmeta = reader.find_by_isbn13(isbn13)
  print(bookmeta)


def process():
  reader = MongoDBCollectionRetriever()
  reader.process()


if __name__ == '__main__':
  """
  adhoc_test1()
  process()
  """
  adhoc_test1()
