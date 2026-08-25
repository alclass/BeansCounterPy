#!/usr/bin/env python3
"""
art/immeub/inst/cdutra/credeb_accomp/mdb/readers/mongo_reader_refmonths.py

import pprint
# from decima-l import Decimal
"""
import datetime
import art.fnc.credeb_accomp.credeb_accompanying_mod as debcred_acc  # .DebCredAccompanier
import art.fnc.credeb_accomp.mdb as init
import art.fnc.credeb_accomp.mdb.serialize_dinero_n_decimal as srlz  # srlz.din_dec_dict_fact
import lib.datesetc.refmonth_fs as rmfs
from pymongo import MongoClient
MONGODB_CON_STR = init.MONGODB_CON_STR
DEFAULT_MONGO_DBNAME = init.IMMEUB_DBNAME
DEFAULT_MONGO_COLLNAME = init.CREDEB_ACCOMP_COLLNAME


def refmonths_reader_fr_db():
  """
  refmonth
  """
  seq = 0
  for debcre_acc_o in debcred_acc_objlist:
    pdict = debcre_acc_o.as_json_str()
    # pjson = json.dumps(pdict)
    # olist.append(pjson)
    # print(pjson)
    seq += 1
    scrmsg = f"{seq} upserting"
    print(scrmsg)
    query_filter = {"refmonth": pdict["refmonth"]}
    update_operations = {"$set": pdict}
    mongoup.update(query_filter, update_operations, pdict)
  # print(olist)
  # s = json.dumps(olist)  #
  scrmsg = f"{seq} ended"
  print(scrmsg)



class MongoDBCollectionRetriever:

  def __init__(self, mongo_dbname=None, mongo_collname=None):
    self.bk_count = 0
    self.mongo_count = 0
    self.mongo_dbname = mongo_dbname or DEFAULT_MONGO_DBNAME
    self.mongo_collname = mongo_collname or DEFAULT_MONGO_COLLNAME
    self.mongo_cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.accomprefmonths: list = []  # to signal for fetch_all_n_store()
    self.has_run_fetch_all_n_store = False
    self.json_accomprefmonths: list = []
    # self.open_conn()

  @property
  def total_refmonths(self):
    if self.accomprefmonths is None or len(self.accomprefmonths) == 0:
      return 0
    return len(self.accomprefmonths)

  def open_conn(self):
    self.mongo_cli_conn = MongoClient(MONGODB_CON_STR)
    self.mongo_db = self.mongo_cli_conn[self.mongo_dbname]
    self.mongo_coll = self.mongo_db[self.mongo_collname]
    # Count documents
    self.mongo_count = self.mongo_coll.count_documents({})
    # print(f"Total documents in collection: {self.mongo_count}")

  def retrieve_the_first_n_docs(self, n_first):
    """
    # Show first document
    first_doc = self.mongo_coll.find_one()
    if first_doc:
        print(f"\nFirst document:\n{json.dumps(first_doc, indent=2, default=str)}")
    """
    # Show n_first documents
    self.open_conn()
    scrmsg = f"\tRetrieving the {n_first} first documents:"
    print(scrmsg)
    for doc in self.mongo_coll.find().limit(n_first):
        print(json.dumps(doc, indent=2, default=str))
    self.close_conn()

  def find_by_refmonth_as_obj(self, p_refmonth):
    self.open_conn()
    refmonth = rmfs.make_refmonth_or_none(p_refmonth)
    if refmonth is None:
      return {}
    refmonth = datetime.datetime.combine(refmonth, datetime.time.min)
    if refmonth is None:
      return {}
    isbn_query = {"refmonth": refmonth}
    doc = self.mongo_coll.find_one(isbn_query)
    credeb_o = None
    if doc is not None:
      pdict = srlz.deserialize_mongo_doc(doc, is_data_from_db=True)
      credeb_o = debcred_acc.DebCredAccompanier.instantiate_fr_dict(pdict)
    self.close_conn()
    return credeb_o

  def find_by_refmonth_as_json(self, p_refmonth):
    credeb_o = self.find_by_refmonth_as_obj(p_refmonth)
    return credeb_o or {}


  def retrieve_all_as_json(self):
    """
    It is not necessary to convert the object to json
      at this point. FastAPI does it "automatically"
      when it returns a list of dict's
    """
    # if self.accomprefmonths is None:
    self.fetch_all_n_store()
    json_list = []
    self.open_conn()
    for i, credeb_o in enumerate(self.accomprefmonths):
      json_list.append(credeb_o.as_json_str())
    self.open_conn()
    return json_list

  def fetch_all_n_store(self):
    """
    self.bookroutes = []  # initially self.bookroutes is None
    Also this method should not run more than once,
      except if a refreshing scheme is created
    """
    if self.has_run_fetch_all_n_store:
      return
    self.has_run_fetch_all_n_store = True
    self.accomprefmonths = []  # initially self.bookroutes is None
    # print(f"\tRetrieving all {self.mongo_count} documents:")
    self.open_conn()
    for i, doc in enumerate(self.mongo_coll.find()):
      seq = i + 1
      self.bk_count = seq
      # print(seq, json.dumps(doc, indent=2, default=str))
      pdict = srlz.deserialize_mongo_doc(doc, is_data_from_db=True)
      credeb_o = debcred_acc.DebCredAccompanier.instantiate_fr_dict(pdict)
      self.accomprefmonths.append(credeb_o)
    self.close_conn()

  def fetch_all_as_objs(self):
    self.fetch_all_n_store()
    return self.accomprefmonths


  def cli_show_refmonth_acc(self):
    if self.accomprefmonths is None:
      self.fetch_all_n_store()
    if self.accomprefmonths is None or len(self.accomprefmonths) == 0:
      return
    self.accomprefmonths.sort(key=lambda b: b.refmonth)
    for i, bm in enumerate(self.accomprefmonths):
      print(i+1, '->', bm)

  def process(self):
    # self.read_first_5_docs()
    self.fetch_all_n_store()
    self.cli_show_refmonth_acc()
    self.close_conn()

  def close_conn(self):
    if self.mongo_cli_conn is not None:
      self.mongo_cli_conn.close()



def adhoctest1():
  """
  refmonths_reader_fr_db()
  """
  retriever = MongoDBCollectionRetriever()
  retriever.process()


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()