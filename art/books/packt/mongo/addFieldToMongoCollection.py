#!/usr/bin/env python3
"""
art/books/packt/mongo/addFieldToMongoCollection.py
  Adds a field to a Mongo collection

  For the time being it is hardcoded
  TODO: upgrade this script to allow input parameters in the future

"/home/dados/Books/epub Books"
"""
from pymongo import MongoClient
from art.books.packt import DEFAULT_MONGO_DBNAME
from art.books.packt import DEFAULT_MONGO_COLLNAME
from art.books.packt import DEFAULT_LOCAL_MONGO_CONN_URL
DEFAULT_NEW_FIELDNAME = 'packts_midurl_ka'


class MongoFieldAdder:

  def __init__(self,
      new_fieldname:str|None=None,
      mongo_cli_conn_url:str|None=None,
      mongo_dbname:str|None=None,
      mongo_collname:str|None=None,
  ):
    self.new_fieldname = new_fieldname or DEFAULT_NEW_FIELDNAME
    self.mongo_cli_conn_url = mongo_cli_conn_url or DEFAULT_LOCAL_MONGO_CONN_URL
    self.mongo_dbname = mongo_dbname or DEFAULT_MONGO_DBNAME
    self.mongo_collname = mongo_collname or DEFAULT_MONGO_COLLNAME
    self.mongo_cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.open_conn()

  def open_conn(self):
    self.mongo_cli_conn = MongoClient(self.mongo_cli_conn_url)
    self.mongo_db = self.mongo_cli_conn[self.mongo_dbname]
    self.mongo_coll = self.mongo_db[self.mongo_collname]

  def add_field_to_mongo_collection(self):
    db_addfield_operation = {  # adds the new field with its default value (here an empty string)
      "$set": {
        f"{self.new_fieldname}": ""
      }
    }
    # result = collection.update_many({}, rename_operation)
    result = self.mongo_coll.update_many(
       {}, # Matches all documents in the collection
       db_addfield_operation
    )
    # print the number of documents updated
    print(self)
    print(f"\tMatched documents: {result.matched_count}")
    print(f"\tModified documents: {result.modified_count}")

  def close_conn(self):
    if self.mongo_cli_conn is not None:
      self.mongo_cli_conn.close()

  def __str__(self):
    outstr = f"""
      mongo_cli_conn_url = {self.mongo_cli_conn_url} 
      mongo_dbname = {self.mongo_dbname}
      mongo_collname = {self.mongo_collname}
    """
    return outstr


def process():
  """
  pass
  """
  adder = MongoFieldAdder()  # let all constructor's parameters default
  adder.add_field_to_mongo_collection()
  adder.close_conn()


if __name__ == "__main__":
  """
  """
  process()
