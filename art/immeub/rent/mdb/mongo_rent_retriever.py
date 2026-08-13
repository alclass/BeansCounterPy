"""
art/immeub/rent/mdb/mongo_rent_retriever.py


import art.immeub.rent.mdb.nongo_rent_reader as mng_rent  # mng_rent.billingcards_reader_fr_db

import pprint
# from decimal import Decimal
"""
import json

from pymongo import MongoClient
import re
import art.immeub.rent.pdntcmdls.billingcard_pydantic as bcardpydtc  # bcardpydtc.PydtcBillingCard
import art.immeub.rent.mdb as mdbinit
LOCAL_MONGODB_CONSTR = mdbinit.MONGODB_CON_STR
IMMEUB_DBNAME = mdbinit.IMMEUB_DBNAME
BILLINGCARD_COLLNAME = mdbinit.BILLINGCARD_COLLNAME


def billingcards_reader_fr_db():
  """
  refmonth
  """
  seq = 0
  for debcre_acc_o in debcred_acc_objlist:
    pdict = debcre_acc_o.asdict()
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
  """
  The client_connection and dbname are related to package/module.
  The collection names are parameterized, and the ones in the 'db'.
  """

  def __init__(self, mongo_dbname=None, mongo_collname=None):
    self.collection_count = 0
    self.dbname = mongo_dbname or IMMEUB_DBNAME
    self.collname = mongo_collname or BILLINGCARD_COLLNAME
    self.mng_cli_con = None
    self.mongodb_db = None
    self.mongodb_coll = None

  def set_mongocliconn_n_db(self):
    self.mng_cli_con = MongoClient(LOCAL_MONGODB_CONSTR)
    self.mongodb_db = self.mng_cli_con[self.dbname]

  def set_collname_or_default(self, p_collname: str | None = None):
    self.set_mongocliconn_n_db()
    self.collname = p_collname if p_collname is not None else self.collname
    self.mongodb_coll = self.mongodb_db[self.collname]
    # Count documents
    self.collection_count = self.mongodb_coll.count_documents({})
    ostr = f"""Setting set_collname_or_default()
    mng_cli_con = {self.mng_cli_con} | mongodb_dbname = {self.dbname}
    collname = {self.collname} | {self.collection_count} documents    
    """
    print(ostr)
    # print(f"Total documents in collection: {self.collection_count}")

  def find_by_coll_n_query(self, collname, query):
    self.set_collname_or_default(collname)
    print('collname, query', collname, query)
    docs = self.mongodb_coll.find(query)
    outdocs = [o for o in docs]
    return outdocs

  def fetch_w_1coll_2fieldname_3list(self, collname, fieldname, valuelist):
    query = {fieldname: {"$in": valuelist}}
    return self.find_by_coll_n_query(collname, query)

  def retrieve_all_as_jsons(self, collname: str | None = None) -> list[str]:
    """
    It is not necessary to convert the object to json
      at this point. FastAPI does it "automatically"
      when it returns a list of dict's
    """
    docs = self.find_by_coll_n_query(collname, {})
    json_list = []
    for i, doc in enumerate(docs):
      json_list.append(doc)
    return json_list

  def retrieve_all_as_objs(self, collname, cls):
    jsons = self.retrieve_all_as_jsons(collname)
    objs = [cls.instantiate_from_jsondict(o) for o in jsons]
    return objs

  def rename_fieldname(self, collname: str, from_fieldname: str, to_fieldname: str):
    """
    result = collection.update_many({}, rename_operation)
    # 5. Print the number of documents updated
    print(f"Matched documents: {result.matched_count}")
    print(f"Modified documents: {result.modified_count}")
    """
    rename_operation = {
      "$rename": {
        f"{from_fieldname}": f"{to_fieldname}"
      }
    }
    self.set_collname_or_default(collname)
    result = self.mongodb_coll.update_many({}, rename_operation)
    # print the number of documents updated
    print(f"Matched documents: {result.matched_count}")
    print(f"Modified documents: {result.modified_count}")

  def close_conn(self):
    if self.mng_cli_con is not None:
      self.mng_cli_con.close()


def get_persons_by_cpfs(cpfs: list[str]) -> list:
  retriever = MongoDBCollectionRetriever()
  docs = retriever.fetch_w_1coll_2fieldname_3list('persons', 'cpf', cpfs)
  retriever.close_conn()
  return docs


def adhoctest1():
  """
  refmonths_reader_fr_db()
  """
  pass

def tmp_rename_email_to_emails():
  retriever = MongoDBCollectionRetriever()
  retriever.rename_fieldname(
    collname='persons', from_fieldname='email', to_fieldname='emails'
  )
  retriever.close_conn()


def adhoctest2():
  cpfs = ['12345678909']
  print('cpfs', cpfs)
  persons = get_persons_by_cpfs(cpfs)
  # persons = json.dumps(persons, indent=2)
  print('persons', persons)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest2()