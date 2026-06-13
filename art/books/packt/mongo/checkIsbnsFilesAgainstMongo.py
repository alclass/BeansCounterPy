#!/usr/bin/env python3
"""
art/books/packt/mongo/checkIsbnsFilesAgainstMongo.py

  via bash:
    grep -rl <isbn13>

"/home/dados/Books/epub Books"
"""
import art.books.packt.mongo.readBooksFromMongo as rBFM  # rbfm.MongoDBCollReader
import art.books.packt.folders.packtInfoDirTreeExtractor as pIDTE  # pIDTE.DirWalkBookInfoExtractor


class PacktIsbnMongoRoller:

  def __init__(self, database_name=None, collection_name=None):
    self.n_found = 0
    self.n_not_found = 0
    self.missing_isbns = []
    self.dbreader = rBFM.MongoDBCollReader()
    self.results = []
    self.seq = 0
    self.database_name = database_name
    self.collection_name = collection_name

  @property
  def total(self):
    return self.n_found + self.n_not_found

  def find(self, isbn13):
    self.seq += 1
    scrmsg = f"{self.seq} finding isbn = {isbn13}"
    print(scrmsg)
    n_found = self.dbreader.find_by_isbn13(isbn13)
    self.n_found += n_found
    n_not_found = 1 if n_found == 0 else 0
    self.n_not_found += n_not_found
    if n_not_found > 0:
      self.missing_isbns.append(isbn13)

    return n_found

  def find_various(self, isbn13_list: list):
    self.n_found = 0
    for isbn13 in isbn13_list:
      # accumulators found and not_found are updated in find()
      _ = self.find(isbn13)

  def close_conn(self):
    self.dbreader.close_conn()

  def __str__(self):
    missings = []
    for isbn13 in self.missing_isbns:
      missings += self.dbreader.retrieve_by_isbn13(isbn13)
    outstr = f"""{self.__class__.__name__}
      n_found = {self.n_found}
      n_not_found = {self.n_not_found}
      total = {self.total}
      missing_isbns = {missings}
    """
    return outstr


def get_isbns_by_files():
  basefolder_ap = "/home/dados/Books/epub Books"
  dirwalker = pIDTE.DirWalkBookInfoExtractor(basefolder_ap=basefolder_ap)
  for bookinfo in dirwalker.gen_bookinfolist_as_dicts_via_dirwalk():
    yield bookinfo


def process():
  """
  """
  roller = PacktIsbnMongoRoller()
  for bookinfo in get_isbns_by_files():
    isbn13 = bookinfo['isbn13']
    roller.find(isbn13)
  print(roller)
  roller.close_conn()


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
