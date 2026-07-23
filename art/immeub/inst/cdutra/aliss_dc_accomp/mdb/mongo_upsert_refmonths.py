#!/usr/bin/env python3
"""
art/immeub/inst/cdutra/aliss_dc_accomp/mdb/mongo_upsert_refmonths.py

import pprint
from decimal import Decimal
"""
import immeub.inst.cdutra.aliss_dc_accomp.alssn_deb_cre_accompanying as alssn_db  # .DebCredAccompanier
import json
import art.immeub.inst.cdutra.aliss_dc_accomp.mdb.jsonToMongoUpsertor as mngUp
import art.immeub.inst.cdutra.aliss_dc_accomp as init
IMMEUB_DBNAME = init.IMMEUB_DBNAME
ALIS_DEBT_ACC_COLLNAME = init.ALIS_DEBT_ACC_COLLNAME


def mongo_upsert_refmonths_in_db():
  """
  refmonth
  """
  debcred_acc_objlist = alssn_db.get_months_closings_w_dictdata()
  # olist = []
  mongoup = mngUp.MongoUpsertor(
    mongo_dbname=IMMEUB_DBNAME,
    mongo_collname=ALIS_DEBT_ACC_COLLNAME,
  )
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

    # 2. Define the data to insert or update
    update_operations = {"$set": data}

    # 3. Execute the upsert
    collection.update_one(query_filter, update_operations, upsert=True)


def adhoctest1():
  """
  debcred_acc_objlist = alssn_db.DebCredAccompanier()
  """
  mongo_upsert_refmonths_in_db()


def find_refmonth_in_db(refmonth):
  """
  refmonth = refmonth.upper()

  """
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