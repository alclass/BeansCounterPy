#!/usr/bin/env python3
"""
art/books/packt/dirwalk/chainProcessTowardsMongo.py
    Executes the process chain from dirwalk to MongoDB storing in the two steps below:
      1 dirwalk folders at the same time generating the bookinfo objects
      3 as generation happens (one object at a time), store each one to MongoDB

"""
import art.books.packt.dirwalk.packtInfoDirTreeExtractor as pIDTE
from art.books.packt.dirwalk.jsonToMongoReadWriteFunctions import from_jsondictlist_to_mongodb_advanced
from art.books.packt.dirwalk import DEFAULT_MONGO_DB
from art.books.packt.dirwalk import DEFAULT_MONGO_COLL
from art.books.packt.dirwalk import DEFAULTFALLBACK_LOCAL_BOOKS_ROOTFOLDER
import types


def process():
  rootfolder_ap = pIDTE.get_args() or DEFAULTFALLBACK_LOCAL_BOOKS_ROOTFOLDER
  generator = pIDTE.DirWalkBookInfoExtractor(rootfolder_ap).gen_bookinfolist_as_dicts_via_dirwalk()
  # not to be used: the yielded element below is BookInfoDC which is not dict-iterable for the json functions
  # generator = pIDTE.DirWalkBookInfoExtractor(rootfolder_ap).gen_bookinfolist_via_dirwalk()
  print(isinstance(generator, types.GeneratorType))
  # return
  from_jsondictlist_to_mongodb_advanced(
    generator,
    DEFAULT_MONGO_DB,
    DEFAULT_MONGO_COLL,
  )


if __name__ == '__main__':
  """
  adhoc_test1()
  adhoc_test2()
  process()
  """
  process()
