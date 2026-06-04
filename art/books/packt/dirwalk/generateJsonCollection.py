#!/usr/bin/env python3
"""
art/books/packt/dirwalk/generateJsonCollection.py
  Explanation:
    (...)

  "/home/dados/Books/epub Books"
"""
from pathlib import Path
import json
import os
import sys
import art.books.packt.dirwalk.packtInfoDirTreeExtractor as pIDT
from art.books.packt.dirwalk import DEFAULT_PACKT_JSON_FILENAME
# pIDT.bookinfo_nt


class GenerateJsonCollection:

  def __init__(self, basefolder_ap=None, json_filename=None):
    self.bookinfos = []
    self.store_collection_has_run = None
    self.basefolder_ap = basefolder_ap
    self.treat_basefolder()
    self.json_filename = json_filename or DEFAULT_PACKT_JSON_FILENAME

  def treat_basefolder(self):
    if self.basefolder_ap is None or not os.path.isdir(self.basefolder_ap):
      # default it to running current folder
      self.basefolder_ap = Path(os.path.abspath(os.path.curdir))
      return
    # guarantee that is a Path object
    self.basefolder_ap = Path(self.basefolder_ap)

  def gen_collection_thru_dirs(self):
    extractor = pIDT.InfoExtractor(self.basefolder_ap)
    for i, bookinfo in enumerate(extractor.gen_collection_w_dirwalk()):
      yield bookinfo

  def print_via_gen_collection_thru_dirs(self):
    for i, bookinfo in enumerate(self.gen_collection_thru_dirs()):
      print(i + 1, bookinfo)
      pass

  def get_n_store_collection_thru_dirs(self):
    self.store_collection_has_run = False
    self.bookinfos = []
    for bookinfo in self.gen_collection_thru_dirs():
      self.bookinfos.append(bookinfo)
    self.store_collection_has_run = True

  def create_collection_json_w_generated(self):
    """
    The idea for this method is to write one record at a time
      as each one is "yielded" (by the generator)
    """
    pass

  def stored_bookinfo_dictlist(self):
    if not self.store_collection_has_run:
      self.get_n_store_collection_thru_dirs()
    dicts = map(lambda bi: bi.asdict, self.bookinfos)
    return list(dicts)

  @property
  def json_filepath(self):
    outfile = self.basefolder_ap / self.json_filename
    return outfile

  def writefile_jsoncollection_w_stored(self):
    if not self.store_collection_has_run:
      self.get_n_store_collection_thru_dirs()
    if len(self.bookinfos) == 0:
      scrmsg = "No bookinfos to write to a file."
      print(scrmsg)
      return False
    dictlist = self.stored_bookinfo_dictlist()
    # Writing to a file
    scrmsg = "Writing book info collection to a file"
    print(scrmsg)
    scrmsg = f"Number of books: {len(dictlist)}"
    print(scrmsg)
    basefolder, filename = os.path.split(self.json_filepath)
    scrmsg = f"Folder: [{basefolder}]"
    print(scrmsg)
    scrmsg = f"Filename: [{filename}]"
    print(scrmsg)
    with open(self.json_filepath, "w", encoding="utf-8") as filedescr:
      json.dump(dictlist, filedescr, indent=2)


def get_args():
  rootfolder_ap = None
  if len(sys.argv) > 1:
    rootfolder_ap = sys.argv[1]
  return rootfolder_ap


def process():
  rootfolder_ap = get_args()
  print(rootfolder_ap)
  extractor = GenerateJsonCollection(rootfolder_ap)
  extractor.print_via_gen_collection_thru_dirs()
  extractor.writefile_jsoncollection_w_stored()


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
