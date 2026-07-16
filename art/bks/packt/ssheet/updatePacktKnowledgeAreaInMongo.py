#!/usr/bin/env python3
"""
art/bookroutes/packt/ssheet/extractBooksMetaFromSpreadSheet.py
from dataclasses import dataclass
from art.bookroutes.packt import BookModel
from art.bookroutes.packt import DEFAULTFALLBACK_LOCAL_BOOKS_ROOTFOLDER
"""
from pymongo import MongoClient
from art.bks.packt import DEFAULT_LOCAL_MONGO_CONN_URL
from art.bks.packt import DEFAULT_MONGO_DBNAME
from art.bks.packt import DEFAULT_MONGO_COLLNAME
from art.bks.packt.mongo.retrievers.retrievesBooksMetaFromMongo import MongoDBCollectionRetriever
from art.bks.packt.ssheet.extractBooksMetaFromSpreadSheet import PacktsSpreadSheetReader


class ExtractKnowledgeAreaAndUpsert:

  def __init__(self, mongo_dbname=None, mongo_collname=None):
    self.bk_count = 0
    self._total_books_in_mongo = None
    self.n_update = 0
    self.mongo_count = 0
    self.current_book = None
    self.dbretriever = None
    self.mongo_dbname = mongo_dbname or DEFAULT_MONGO_DBNAME
    self.mongo_collname = mongo_collname or DEFAULT_MONGO_COLLNAME
    self.mongo_cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.books = []
    self.ssheet_books = []
    self.open_conn()

  def open_conn(self):
    self.mongo_cli_conn = MongoClient(DEFAULT_LOCAL_MONGO_CONN_URL)
    self.mongo_db = self.mongo_cli_conn[self.mongo_dbname]
    self.mongo_coll = self.mongo_db[self.mongo_collname]
    # Count documents
    self.mongo_count = self.mongo_coll.count_documents({})
    print(f"Total documents in collection: {self.mongo_count}")

  def mongo_update_packtsknowledgearea(self):
    """
        # This writes ONLY if a new document is inserted
        "$setOnInsert": {
            "account_created": "2026-06-14"
        }
      result = collection.update_one(filter_query, update_query, upsert=True)
    """
    total_bks_in_ss = len(self.ssheet_books)
    self.n_update += 1
    scrmsg = f"upt={self.n_update}/{total_bks_in_ss} | {self.current_book}"
    print(scrmsg)
    # Define the unique identifier filter
    filter_query = {"isbn13": self.current_book.isbn13}
    # Define the update fields
    update_query = {
      # This updates existing documents OR writes on new creations
      "$set": {
        "packts_midurl_ka": self.current_book.packts_midurl_ka,
      },
    }
    # Execute the update
    result = self.mongo_coll.update_one(filter_query, update_query)
    print(f"\tMatched documents: {result.matched_count}")
    print(f"\tModified documents: {result.modified_count}")

  @property
  def total_books_in_mongo(self):
    if self._total_books_in_mongo is not None:
      return self._total_books_in_mongo
    self.count_books_in_mongo()
    if self._total_books_in_mongo is None:
      errmsg = f"MongoDB {self.mongo_dbname} could not be read or collection {self.mongo_collname} is empty;"
      raise IOError(errmsg)
    return self._total_books_in_mongo

  def count_books_in_mongo(self):
    result = self.mongo_coll.filter({})
    self._total_books_in_mongo = result.matched_count

  def update_all_packtsknowledgearea(self):
    for self.current_book in self.ssheet_books:
      if self.current_book is None:
        scrmsg = f"current_book is None. Continuing."
        print(scrmsg)
        continue
      if self.current_book.packts_midurl_ka is None:
        scrmsg = f"packtsknowledgearea is None for book {self.current_book}.\n Continuing."
        print(scrmsg)
        continue
      self.mongo_update_packtsknowledgearea()

  def sshet_retrieve_rows(self):
    ssheet_reader = PacktsSpreadSheetReader()
    # ssheet_reader.generate_all_records()
    self.ssheet_books = ssheet_reader.get_all_records()
    scrmsg = f"Total retrieved from spread sheet: {len(self.ssheet_books)}"
    print(scrmsg)

  def db_retrieve_docs(self):
    self.dbretriever = MongoDBCollectionRetriever(
      mongo_dbname=self.mongo_dbname,
      mongo_collname=self.mongo_collname,
    )
    self.dbretriever.fetch_all_n_store()
    scrmsg = f"Total retrieved from db: {self.dbretriever.total_books}"
    print(scrmsg)

  def process(self):
    """
    sshet_retrieve_rows() retrieves rows from Packt's spreadsheet
    db_retrieve_docs() retrieves docs from db
    """
    self.sshet_retrieve_rows()
    self.update_all_packtsknowledgearea()
    print(self)

  def __str__(self):
    total_bks_in_ss = len(self.ssheet_books)
    outstr = f"""{self.__class__.__name__}:
    mongo_dbname = {self.mongo_dbname}
    mongo_collname = {self.mongo_collname}
    total bookroutes in spread sheet = {total_bks_in_ss}
    total bookroutes in mongo = {total_bks_in_ss}
    """
    return outstr



def process():
  updater = ExtractKnowledgeAreaAndUpsert()
  updater.process()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
