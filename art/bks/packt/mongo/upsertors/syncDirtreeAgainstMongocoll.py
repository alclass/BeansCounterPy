#!/usr/bin/env python3
"""
art/bookroutes/packt/mongo/syncDirtreeAgainstMongocoll.py
  Explanation
    (...)

  "/home/dados/Books/epub Books"

"""
import sys
from pymongo import MongoClient
import art.bks.packt.folders.packtInfoDirTreeExtractor as bkExtr
from art.bks.packt import DEFAULT_MONGO_DBNAME
from art.bks.packt import DEFAULT_MONGO_COLLNAME
from art.bks.packt import DEFAULT_LOCAL_MONGO_CONN_URL


class SyncBookDirTreeWithMongoColl:

  def __init__(self, basefolder_ap=None):
    self.basefolder_ap = basefolder_ap
    self.bookinfo = None
    self.n_inserted = 0
    self.n_deleted = 0
    self.n_books_w_null_isbn = 0
    self.n_books_in_dirtree = 0
    self.n_books_in_db = 0
    self.n_deleted_as_null_isbns = 0
    self.mongo_cli_conn = None
    self.mongodb = None
    self.mongocoll = None
    self.set_mongo_db_n_coll()
    # self.process()

  def set_mongo_db_n_coll(self):
    self.mongo_cli_conn = MongoClient(DEFAULT_LOCAL_MONGO_CONN_URL)
    self.mongodb = self.mongo_cli_conn[DEFAULT_MONGO_DBNAME]
    self.mongocoll = self.mongodb[DEFAULT_MONGO_COLLNAME]

  def is_book_in_db(self, bookinfo):
    """
    The collection involved here has isbn as
      a "strong primary-key", though MongoDB does not enforce it.
    At the same time, some bookroutes did not have an ISBN at
      the time of recording.
    Here is the strategy:
      1a - check if isbn exists in db
      2a - if it exists, check if another record (document)
         exists with the same title and year
      3a - if it does, delete the one without isbn
      1b - if it doesn't have an isbn, treat it as an upsert
    """
    print('@is_book_in_db')
    if bookinfo.isbn13 is not None:
      query = {"isbn": bookinfo.isbn13}
      docs = self.mongocoll.find(query)
      ldocs = list(docs)
      docsize = len(ldocs)
      if docsize == 0:
        # insert it
        self.mongo_insert(bookinfo)
        return
      elif docsize == 1:
        # that is correct, just return
        print('ISBN just one:', bookinfo.isbn13)
        return
      else:
        # oh, oh only one should exist
        self.delete_excess(bookinfo, ldocs, docsize)
        return
    # at this point, isbn is None
    # notice that bookinfo in this script comes from dir
    # because of that, nothing needs to be done
    # another method will delete null-isbn's in db

  def delete_excess(self, bookinfo, ldocs, docsize):
    scrmsg = f"ISBN {docsize} repeats: {bookinfo.isbn13}"
    print(scrmsg)
    scrmsg = f"{bookinfo}"
    print(scrmsg)
    print('-'*40)
    scrmsg = f"docsize {docsize} | {bookinfo.isbn13}"
    print(scrmsg)
    if docsize > 1:
      print('docsize > 1', docsize, 'len =', len(ldocs))
      for doc in ldocs[1:]:
        self.n_deleted += 1
        scrmsg = f"n_deleted {self.n_deleted} | doc => {doc}"
        print(scrmsg)
        self.mongocoll.delete_one({"_id": doc['_id']})
        scrmsg = f"{self.n_deleted}/dc={self.mongocoll.deleted_count} deleting: {doc}"
        print(scrmsg)

  def mongo_insert(self, bookinfo):
    print('@mongo_insert')
    self.n_inserted += 1
    result = self.mongocoll.insert_one(bookinfo.asdict)
    print(f"Inserted document with ID: {result.inserted_id}")

  def count_books_in_db(self):
    self.n_books_in_db = self.mongocoll.count_documents({})
    self.n_books_w_null_isbn = self.mongocoll.count_documents({'isbn':None})

  def delete_null_isbns_in_db(self):
    self.mongocoll.delete_many({'isbn':None})
    self.n_deleted_as_null_isbns = self.mongocoll.deleted_count

  def process(self):
    self.count_books_in_db()
    dw_extractor = bkExtr.DirWalkBookInfoExtractor(self.basefolder_ap)
    for i, bookinfo in enumerate(dw_extractor.gen_bookinfolist_via_dirwalk()):
      seq = i + 1
      self.n_books_in_dirtree = seq
      scrmsg = f"{seq} checking {bookinfo}"
      print(scrmsg)
      self.is_book_in_db(bookinfo)
    self.delete_null_isbns_in_db()
    self.close_mongoclient()
    print(self)

  def close_mongoclient(self):
    if self.mongo_cli_conn:
      self.mongo_cli_conn.close()

  def __str__(self):
    outstr = f"""{self.__class__.__name__}
    number of inserted = {self.n_inserted}
    number of deleted = {self.n_deleted}
    number of bookroutes in folders = {self.n_books_in_dirtree}
    number of bookroutes in db = {self.n_books_in_db}
    number of bookroutes without isbn = {self.n_books_w_null_isbn}
    number of db-deletes without isbn = {self.n_deleted_as_null_isbns}
    """
    return outstr


def adhoc_test2():
  pass


def adhoc_test1():
  pass


def get_args():
  rootfolder_ap = None
  if len(sys.argv) > 1:
    rootfolder_ap = sys.argv[1]
  return rootfolder_ap


def process():
  rootfolder_ap = get_args()
  syncker = SyncBookDirTreeWithMongoColl(rootfolder_ap)
  syncker.process()


if __name__ == '__main__':
  """
  adhoc_test1()
  adhoc_test2()
  """
  process()
