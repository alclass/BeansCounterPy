#!/usr/bin/env python3
"""
art/books/packt/folders/chainProcessFolderToMongo.py
    Executes the process-chain from folders to MongoDB storing
        in the two steps below:
      1 dirwalking folders to generate the bookinfo objects from filenames
      2 as each bookinfo is yielded (loop-generated), store each one
        to its corresponding MongoDB collection
        (in fact, the class used is bookinfo_dc which comes up as a dict (for JSON usage))

"""
import art.books.packt.folders.packtInfoDirTreeExtractor as pIDTE
from art.books.packt import DEFAULTFALLBACK_LOCAL_BOOKS_ROOTFOLDER
from art.books.packt.mongo.upsertors.jsonToMongoUpsertor import MongoUpsertor


class FolderToMongoChainer:

  def __init__(self, bk_gen):
    self.upsertor = MongoUpsertor()
    self.bk_gen = bk_gen

  def upsert_books(self):
    for i, bookinfo in enumerate(self.bk_gen):
      print(i, 'upserting', bookinfo)
      self.upsertor.update(bookinfo)
    self.upsertor.close_conn()

  def __str__(self):
    outstr = f"""{self.__class__.__name__})
      upsertor = {self.upsertor} 
    """
    return outstr


def adhoc_test1():
  pass


def process():
  """
  """
  rootfolder_ap = pIDTE.get_args() or DEFAULTFALLBACK_LOCAL_BOOKS_ROOTFOLDER
  generator = pIDTE.DirWalkBookInfoExtractor(rootfolder_ap).gen_bookinfolist_as_bidcdicts_via_dirwalk()
  chainer = FolderToMongoChainer(generator)
  chainer.upsert_books()
  print('chainer', chainer)


if __name__ == '__main__':
  """
  adhoc_test1()
  process()
  """
  process()
