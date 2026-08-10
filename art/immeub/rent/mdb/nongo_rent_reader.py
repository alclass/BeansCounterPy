"""
art/immeub/rent/mdb/nongo_rent_reader.py

import pprint
# from decima-l import Decimal
"""
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

  def __init__(self, mongo_dbname=None, mongo_collname=None):
    self.bk_count = 0
    self.mongo_count = 0
    self.mongo_dbname = mongo_dbname or IMMEUB_DBNAME
    self.mongo_collname = mongo_collname or BILLINGCARD_COLLNAME
    self.mongo_cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.accomprefmonths: list = []  # to signal for fetch_all_n_store()
    self.has_run_fetch_all_n_store = False
    self.json_accomprefmonths: list = []
    # self.open_conn()

  @property
  def total_cobrancas(self):
    if self.accomprefmonths is None or len(self.accomprefmonths) == 0:
      return 0
    return len(self.accomprefmonths)

  def open_conn(self):
    self.mongo_cli_conn = MongoClient(LOCAL_MONGODB_CONSTR)
    self.mongo_db = self.mongo_cli_conn[self.mongo_dbname]
    self.mongo_coll = self.mongo_db[self.mongo_collname]
    # Count documents
    self.mongo_count = self.mongo_coll.count_documents({})
    # print(f"Total documents in collection: {self.mongo_count}")


  def find_by_immapelido_as_obj(self, imm_nickname):
    pattern = re.compile(r"^"+imm_nickname, re.IGNORECASE)
    query = {"contrnumber": pattern}  # {"$regex": "widget"}; substr = f"^imm_nickname"
    self.open_conn()
    doc = self.mongo_coll.find(query)
    billingcard_o = None
    if doc is not None:
      # pdict = srlz.deserialize_mongo_doc(doc, is_data_from_db=True)
      for i, elem in enumerate(doc):
        _ = elem
        elem = {key: value for key, value in elem.items() if value is not None}
        def remove_nones_fr_billingitems(p_list: list):
          """
          None's must be removed from the testdata
          The outer dict was cleaned up above, now we must remove None's in the billing_items
          (Because billing_items is a dictlist, the dict's are recreated, but the list is used mutably.)
          """
          for ii, supposed_billingitem in enumerate(p_list):
            if not isinstance(supposed_billingitem, dict):
              # there are 2 lists in the outer doc, the address one is not a dict, the 'billingitems' is a dict
              continue
            supposed_billingitem = {key: value for key, value in supposed_billingitem.items() if value is not None}
            # the dict is used immutably (it's recreated), the list is used mutably (the new dict goes back in place)
            p_list[ii] = supposed_billingitem
        for key in elem:
          obj = elem[key]
          if isinstance(obj, list):
            # here we look for lists so that we can look for inner dict's that may contain None's
            alist = obj
            remove_nones_fr_billingitems(alist)
        billingcard_o = bcardpydtc.PydtcBillingCard.MongoJsonRepr(**elem)
    self.close_conn()
    return billingcard_o

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
      json_list.append(credeb_o.asdict())
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
    """
    self.fetch_all_n_store()
    self.cli_show_refmonth_acc()
    self.close_conn()
    """
    pass

  def close_conn(self):
    if self.mongo_cli_conn is not None:
      self.mongo_cli_conn.close()


def adhoctest1():
  """
  refmonths_reader_fr_db()
  """
  retriever = MongoDBCollectionRetriever()
  apelido = 'cdouto'
  print('Finding by apelido', apelido)
  o = retriever.find_by_immapelido_as_obj(apelido)
  if o is not None:
    json_o = o.model_dump_json(indent=2)
    print('Found', json_o)
    print('type', type(o))
  else:
    print('Not found')


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()