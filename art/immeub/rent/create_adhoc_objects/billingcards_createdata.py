#!/usr/bin/env python3
"""
art/immeub/rent/testdata/billingcards_createdata.py

import datetime
"""
from decimal import Decimal
import art.immeub.rent.create_adhoc_objects.rentcontracts_createdata as rc_create  # rc_create.make_rentcontract_1
import art.immeub.rent.billmodels.billingcard_pydantic as bcard  # bcard.PydtcBillingCard
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch
from lib.dbfs.mngdb.mongo_gen_fetcher import mngfetch_rentcontract_by_contrnumber


def adhoctest1():
  rentcontract = rc_create.make_rentcontract_1()
  print(rentcontract)
  refmonth = rmfs.make_refmonth_or_raise('2024-01')
  billingcard = bcard.PydtcBillingCard(
    refmonth=refmonth,
    rentcontract=rentcontract,
  )
  billingcard.make_n_set_minimum_billingitems()
  paydate = dtfs.make_date_or_raise('2024-2-10')
  payvalue = Decimal(1500)
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate, value=payvalue)
  billingcard.add_payment(payment)
  paydate = dtfs.make_date_or_raise('2024-2-21')
  payvalue = Decimal(1500)
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate, value=payvalue)
  billingcard.add_payment(payment)
  billingcard.process()
  print('as_json_str =>', billingcard)
  json_str = billingcard.to_json()
  print('as_json_str =>', json_str)


def adhoctest2():
  """
  reading it from db
  """
  dbname, collname = 'immeub_db', 'billingcards'
  dbfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {"contrnumber": "CDouto202401"}
  docdict = dbfetcher.find_one_w_querydict_n_collname(querydict)
  print(type(docdict), docdict)
  del docdict['_id']
  obj = bcard.PydtcBillingCard.instantiate_fr_json_dict(docdict)
  print('instantiate_fr_json_str =>', obj)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest2()
