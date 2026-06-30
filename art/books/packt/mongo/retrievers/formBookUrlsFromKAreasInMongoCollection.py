#!/usr/bin/env python3
"""
art/books/packt/mongo/retrievers/formBookUrlsFromKAreasInMongoCollection.py
  forms book URL's from the Knowledge Area field in Mongo Collection

import json
from pymongo import MongoClient
from art.books.packt.BookModel import BookInfoDC
"""
from art.books.packt import DEFAULT_MONGO_DBNAME
from art.books.packt import DEFAULT_MONGO_COLLNAME
from art.books.packt.mongo.retrievers.retrievesBooksMetaFromMongo import MongoDBCollectionRetriever

class KAreaURLFormer:

  def __init__(self, database_name=None, collection_name=None):
    """
    self.mongo_db = None
    self.mongo_coll = None
    """
    self.dbretriever = None
    self.count = 0
    self.total_those_not_having_ka = 0
    self.mongo_dbname = database_name or DEFAULT_MONGO_DBNAME
    self.mongo_collname = collection_name or DEFAULT_MONGO_COLLNAME

  def retrieve_mongo_docs(self):
    self.dbretriever = MongoDBCollectionRetriever(
      mongo_collname=self.mongo_collname,
      mongo_dbname=self.mongo_dbname,
    )
    self.dbretriever.fetch_all_n_store()

  def form_each_url(self):
    # Show first document
    print(f"\nAll {self.dbretriever.total_books} documents:")
    for i, bookinfo in enumerate(self.dbretriever.books):
      seq = i + 1
      url = bookinfo.packts_url
      print(seq, bookinfo)
      if url is None:
        self.total_those_not_having_ka += 1
      print('\t', url)

  def process(self):
    self.retrieve_mongo_docs()
    self.dbretriever.close_conn()
    self.form_each_url()
    print(self)

  def __str__(self):
    outstr = f"""{self.__class__.__name__}
      total books in db = {self.dbretriever.total_books}
      total_those_not_having_ka = {self.total_those_not_having_ka}
    """
    return outstr


def process():
  """
  """
  former = KAreaURLFormer()
  former.process()


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
