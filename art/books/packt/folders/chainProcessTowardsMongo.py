#!/usr/bin/env python3
"""
art/books/packt/folders/chainProcessTowardsMongo.py
    Executes the process-chain from folders to MongoDB storing
      in the two steps below:
      1 dirwalking folders generate the bookinfo objects from filenames
      2 as each bookinfo is yield (loop-generation), store each one to MongoDB

"""
import art.books.packt.folders.packtInfoDirTreeExtractor as pIDTE
from art.books.packt import DEFAULTFALLBACK_LOCAL_BOOKS_ROOTFOLDER
import types


def process():
  rootfolder_ap = pIDTE.get_args() or DEFAULTFALLBACK_LOCAL_BOOKS_ROOTFOLDER
  generator = pIDTE.DirWalkBookInfoExtractor(rootfolder_ap).gen_bookinfolist_as_dicts_via_dirwalk()
  # not to be used: the yielded element below is BookInfoDC which is not dict-iterable for the json functions
  # generator = pIDTE.DirWalkBookInfoExtractor(rootfolder_ap).gen_bookinfolist_via_dirwalk()
  print(isinstance(generator, types.GeneratorType))


if __name__ == '__main__':
  """
  adhoc_test1()
  adhoc_test2()
  process()
  """
  process()
