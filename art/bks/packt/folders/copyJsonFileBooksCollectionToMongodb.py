#!/usr/bin/env python3
"""
art/bookroutes/packt/folders/copyJsonFileBooksCollectionToMongodb.py

"/home/dados/Books/epub Books"


Key Points:
    1 MongoDB runs on mongodb://localhost:27017 by default
    2 Use insert_many() for multiple documents, insert_one() for single
    3 MongoDB automatically adds _id if not present
    4 For large files, use the streaming method to avoid memory issues
    5 Use upsert=True with update_one() to avoid duplicates

"""
import os
from pathlib import Path
import sys
<<<<<<< HEAD:art/books/packt/dirwalk/transpose_json_to_mongodb.py
=======
import art.bks.packt.mongo.upsertors.jsonToMongoReadWriteFunctions as mongorwfs
>>>>>>> 91d06ab3b1f9fdb943a436ad7badc16df437feee:art/books/packt/dirwalk/copyJsonFileBooksCollectionToMongodb.py
from art.bks.packt.folders import DEFAULT_PACKT_JSON_FILENAME
from art.bks.packt.folders import DEFAULT_MONGO_DB
from art.bks.packt.folders import DEFAULT_MONGO_COLL


class FromJsonToMongo:

  def __init__(self, basefolder_ap=None, json_filename=None):
    self.basefolder_ap = basefolder_ap
    self.treat_basefolder()
    self.packt_json_filename = json_filename or DEFAULT_PACKT_JSON_FILENAME

  def treat_basefolder(self):
    if self.basefolder_ap is None or not os.path.isdir(self.basefolder_ap):
      # default it to running current folder
      self.basefolder_ap = Path(os.path.abspath(os.path.curdir))
      return
    # guarantee that is a Path object
    self.basefolder_ap = Path(self.basefolder_ap)

  @property
  def json_filepath(self):
    return self.basefolder_ap / self.packt_json_filename

  def upsert_bookinfo_to_mongo(self):
    folderpath, filename = os.path.split(self.json_filepath)
    scrmsg = f"Transposing to MongoDB\n"
    scrmsg += f"\tfolder = [{folderpath}]\n]"
    scrmsg += f"\tfile = [{filename}]"
    scrmsg += f"\tdb = [{DEFAULT_MONGO_DB}]\n]"
    scrmsg += f"\tfile = [{DEFAULT_MONGO_COLL}]"
    print(scrmsg)
    mongorwfs.from_jsonfile_to_mongodb_advanced(
      json_file_path=self.json_filepath,
      db_name=DEFAULT_MONGO_DB,
      coll_name=DEFAULT_MONGO_COLL,
      replace_existing=False,
    )
    print('Finished transposing to MongoDB')


def get_args():
  rootfolder_ap = None
  if len(sys.argv) > 1:
    rootfolder_ap = sys.argv[1]
  return rootfolder_ap


def process():
  rootfolder_ap = get_args()
  print('rootfolder_ap', rootfolder_ap)
  from_json_to_mongo = FromJsonToMongo(rootfolder_ap)
  from_json_to_mongo.upsert_bookinfo_to_mongo()


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
