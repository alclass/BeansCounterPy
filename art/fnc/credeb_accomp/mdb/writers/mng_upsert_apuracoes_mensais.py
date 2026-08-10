#!/usr/bin/env python3
"""
art/fnc/credeb_accomp/mdb/writers/mng_upsert_apuracoes_mensais.py

"""
import datetime
import art.fnc.credeb_accomp.credeb_accompanying_mod as credeb_acc  # .DebCredAccompanier
import art.fnc.credeb_accomp.mdb.writers.jsonToMongoUpsertor as mngUp
import art.fnc.credeb_accomp.mdb as init
import pprint
IMMEUB_DBNAME = init.IMMEUB_DBNAME
CREDEB_ACCOMP_COLLNAME = init.CREDEB_ACCOMP_COLLNAME


def mongo_upsert_refmonths_in_db():
  """
  refmonth
  """
  debcred_acc_objlist = credeb_acc.get_months_closings_w_dictdata()
  # olist = []
  mongoup = mngUp.MongoUpsertor(
    mongo_dbname=IMMEUB_DBNAME,
    mongo_collname=CREDEB_ACCOMP_COLLNAME,
  )
  seq = 0
  for debcre_acc_o in debcred_acc_objlist:
    pdict = debcre_acc_o.asdict()
    # pjson = json.dumps(pdict)
    # olist.append(pjson)
    # print(pjson)
    seq += 1
    scrmsg = f"{seq} upserting"
    pprint.pprint(scrmsg, indent=2)
    # print(scrmsg)
    query_filter = {"refmonth": pdict["refmonth"]}
    update_operations = {"$set": pdict}
    mongoup.update(query_filter, update_operations, pdict)
  # print(olist)
  # s = json.dumps(olist)  #
  scrmsg = f"{seq} ended"
  pprint.pprint(scrmsg, indent=2)
  # print(scrmsg)


def example_w_params_filter_n_update():
  """

  """
  # Sample list of JSON objects (without _id)
  json_list = [
    {"email": "alex@example.com", "name": "Alex", "age": 30},
    {"email": "bob@example.com", "name": "Bob", "age": 25}
  ]

  for data in json_list:
    # 1. Define how to find an existing document (e.g., by email)
    query_filter = {"email": data["email"]}

    # 2. Define the testdata to insert or update
    update_operations = {"$set": data}

    # 3. Execute the upsert
    collection.update_one(query_filter, update_operations, upsert=True)


def adhoctest1():
  """
  debcred_acc_objlist = alssn_db.DebCredAccompanier()
  """
  mongo_upsert_refmonths_in_db()


def find_refmonth_in_db(refmonth: datetime.date):
  """
  refmonth = refmonth.upper()

  """
  _ = refmonth
  return False


class Upsertor:
  def __init__(self, refmonth):
    self.refmonth = refmonth
    self.is_it_in_db = find_refmonth_in_db(self.refmonth)


def adhoctest2():
  """
  d = Decimal(1/3)
  # d.remainder_near()
  print(d)
  """
  mongo_upsert_refmonths_in_db()


def process():
  """
  """
  get_months_closings_w_dictdata()


if __name__ == '__main__':
  """
  process()
  """
  adhoctest2()