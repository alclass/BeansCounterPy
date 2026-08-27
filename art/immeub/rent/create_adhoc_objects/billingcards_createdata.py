#!/usr/bin/env python3
"""
art/immeub/rent/testdata/billingcards_createdata.py

import datetime
"""
import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from sympy import pretty_print

import art.immeub.rent.create_adhoc_objects.rentcontracts_createdata as rc_create  # rc_create.make_rentcontract_1
import art.immeub.rent.billmodels.billingcard_pydantic as bcard  # bcard.PydtcBillingCard
import art.immeub.rent.pdntcmdls.person_pydant as pers  # bcard.PydtcBillingCard
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch
from lib.dbfs.mngdb.mongo_gen_fetcher import mngfetch_rentcontract_by_contrnumber
import art.immeub.rent.htmltemplates.jinja2_adhoctest1 as jj2  # jj2.render_html()


def pickup_recontract_via_make():
  rentcontract = rc_create.make_rentcontract_1()
  # print(rentcontract)
  return rentcontract


def make_billingcard1():
  refmonth = rmfs.make_refmonth_or_raise('2026-04')
  contrnumber = 'CDouto202401'
  billingcard = bcard.PydtcBillingCard(
    refmonth=refmonth,
    # rentcontract=rentcontract,
    contrnumber=contrnumber,
  )
  billingcard.make_n_set_standard_billingitems()
  previousrefmonth = refmonth - relativedelta(months=1)
  billingcard.add_billingitem_w_fields(
    descr="Mora acumulada aluguel/encargos", value=Decimal(1250), refmonth=previousrefmonth,
  )
  paydate1 = billingcard.duedate
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate1, value=Decimal(2500))
  payments = [payment]
  paydate2 = billingcard.duedate + relativedelta(days=11)
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate2, value=Decimal(1500))
  payments.append(payment)
  billingcard.add_payment_lst(payments)
  billingcard.process()
  return billingcard


def print_billingcard_w_dict(dictdoc):
  print(dictdoc)


def fetch_mongo_dictdoc_for_lingcard_w_refmonth_n_contrnumber(
    refmonth: datetime.date, contrnumber: str
  ) -> dict:
  dbname, collname = 'immeub_db', 'billingcards'
  dbfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {"contrnumber": contrnumber, "refmonth": refmonth.strftime("%Y-%m-%d")}
  dictdoc = dbfetcher.find_one_w_querydict_n_collname_as_dict(querydict)
  return dictdoc

def print_billingcard_w_refmonth_n_contrnumber(
    refmonth: datetime.date, contrnumber: str
  ) -> None:
  dictdoc = fetch_mongo_dictdoc_for_lingcard_w_refmonth_n_contrnumber(
    refmonth=refmonth, contrnumber=contrnumber
  )
  print_billingcard_w_dict(dictdoc)


def adhoctest1():
  billingcard = make_billingcard1()
  json_str = billingcard.to_json(is_for_db=True)
  print('as_json_str =>', json_str)


def adhoctest2():
  """
  reading it from db
  """
  dbname, collname = 'immeub_db', 'billingcards'
  dbfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {"contrnumber": "CDouto202401"}
  docdict = dbfetcher.find_one_w_querydict_n_collname_as_dict(querydict)
  print('type(docdict)', type(docdict), 'docdict', docdict)
  if docdict is not None:
    del docdict['_id']
  obj = bcard.PydtcBillingCard.instantiate_fr_json_dict(docdict)
  obj.rentcontract.payee = pers.get_payee_person()
  print('instantiate_fr_json_dict =>', obj)


def adhoctest3():
  contrnumber, refmonth = 'CDouto202401', rmfs.make_refmonth_or_raise('2026-04')
  print_billingcard_w_refmonth_n_contrnumber(contrnumber=contrnumber, refmonth=refmonth)
  dictdoc = fetch_mongo_dictdoc_for_lingcard_w_refmonth_n_contrnumber(contrnumber=contrnumber, refmonth=refmonth)
  pretty_print(dictdoc)
  billingcard = bcard.PydtcBillingCard.instantiate_fr_json_dict(dictdoc)
  return
  payee = pers.get_payee_person()
  billingcard.payee = payee
  jj2.render_html(billingcard=billingcard)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  process()
  adhoctest1()
  """
  # adhoctest1()
  adhoctest2()
