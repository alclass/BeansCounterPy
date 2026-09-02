#!/usr/bin/env python3
"""
art/immeub/rent/testdata/billingcards_createdata.py

import datetime
from sympy import pretty_print
from pprint import PrettyPrinter
from lib.dbfs.mngdb.mongo_gen_fetcher import mngfetch_rentcontract_by_contrnumber
import art.immeub.rent.pdntcmdls.person_pydant as pers  # bcard.PydtcBillingCard
import art.immeub.rent.htmltemplates.jinja2_adhoctest1 as jj2  # jj2.render_html()
"""
import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import art.immeub.rent.create_adhoc_objects.rentcontracts_createdata as rc_create  # rc_create.make_rentcontract_1
import art.immeub.rent.billmodels.billingcard_pydantic as bcard  # bcard.PydtcBillingCard
import art.immeub.rent.billmodels.billingitem_pydantic as bitems  # bcard.PydtcBillingCard
import art.immeub.rent.billmodels.payment_pydant as bipydtc  # bipydtc.PydtcPayment
import art.immeub.rent.mdb.objs_finder_from_mongocollections as fndr  # fndr.dbfetch_billingcard_dictdoc_w_refmonth_n_contrnumber
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch
from art.immeub.rent.pdntcmdls.rentcontract_pydant import PydtcRentContract


def pickup_recontract_via_make():
  rentcontract = rc_create.make_rentcontract_1()
  # print(rentcontract)
  return rentcontract


# noinspection argument-list
def make_n_get_billingcard1():
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
  # print(billingcard.to_json(is_for_db=True))
  return billingcard


def make_billingcard_from_db():
  paydate1 = billingcard.duedate
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate1, value=Decimal(2500))
  payments = [payment]
  paydate2 = billingcard.duedate + relativedelta(days=11)
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate2, value=Decimal(1500))
  payments.append(payment)
  billingcard.payment_lst = payments
  billingcard.process_close()
  return billingcard


def print_billingcard_w_dict(dictdoc):
  print(dictdoc)


def print_billingcard_w_refmonth_n_contrnumber(
    refmonth: datetime.date, contrnumber: str
  ) -> None:
  dictdoc = fndr.fetch_billingcard_dictdoc_w_refmonth_n_contrnumber(
    refmonth=refmonth, contrnumber=contrnumber
  )
  print_billingcard_w_dict(dictdoc)


def adhoctest1():
  billingcard = make_n_get_billingcard1()
  json_str = billingcard.to_json(is_for_db=True)
  print('as_json_str =>', json_str)


def make_a_billingcard_fr_a_rencontract_in_db():
  """
  reading it from db
  """
  # build a billingcard from a rentcontract in DB
  dbname, collname = 'immeub_db', 'rentcontracts'
  dbfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {"contrnumber": "CDouto202401"}
  docdict = dbfetcher.find_one_w_querydict_n_collname_as_dict(querydict)
  rentcontract = PydtcRentContract.instantiate_fr_jsondict(docdict)
  refmonth = rmfs.make_refmonth_or_raise('202404')
  billingitems = rentcontract.make_n_get_standard_billingitems(p_refmonth=refmonth)
  # print(rentcontract)
  # print('type(docdict)', type(docdict), 'docdict', docdict)
  billingcard = bcard.PydtcBillingCard(
    refmonth=refmonth,
    rentcontract=rentcontract,
    billingitems=billingitems,
  )
  json_str = billingcard.to_json(is_for_db=True)
  print('billingcard', json_str)

  # print('instantiate_fr_json_dict =>', obj)


def make_billingcard2_w_monthclosing():
  """

  """
  contrnumber = 'CDouto202401'
  print('contrnumber =>', contrnumber)
  refmonth = rmfs.make_refmonth_or_raise('2026-4')
  billingitems = bitems.make_4_billingitems(refmonth)
  # noinspection argument-list
  billingcard = bcard.PydtcBillingCard(
    refmonth=refmonth,
    contrnumber='CDouto202401',
    billingitems=billingitems
  )
  payments = []
  # noinspection bad-argument-type
  # payment = intrfc.PaymentInterfaceDateNValue(date=billingcard.duedate, value=Decimal(1500))
  datahora = dtfs.make_datetime_w_horazero_or_raise(billingcard.duedate)
  payment = bipydtc.PydtcPayment(datahora=datahora, value=Decimal(1500))
  payments.append(payment)
  datahora = datahora + datetime.timedelta(days=11)  # relativedelta(days=11)
  payment = bipydtc.PydtcPayment(datahora=datahora, value=Decimal(1500))
  payments.append(payment)
  # payments = bcard.transpose_payments_via_interface(payments)
  billingcard.payment_lst = payments
  billingcard.ready_for_closing = True
  billingcard.process_close()
  # print('billingcard =>', billingcard)
  json_str = billingcard.to_json(indent=2, is_for_db=True)
  print('json_str for Jinja2 =>', json_str)
  return billingcard


def adhoctest2():
  """
  make_a_billingcard_fr_a_rencontract_in_db()
  """
  make_billingcard2_w_monthclosing()


def adhoctest3():
  contrnumber, refmonth = 'CDouto202401', rmfs.make_refmonth_or_raise('2026-04')
  print_billingcard_w_refmonth_n_contrnumber(contrnumber=contrnumber, refmonth=refmonth)
  dictdoc = dbfetch_billingcard_dictdoc_w_refmonth_n_contrnumber(contrnumber=contrnumber, refmonth=refmonth)
  pretty_print(dictdoc)
  billingcard = bcard.PydtcBillingCard.instantiate_fr_json_dict(dictdoc)
  print(billingcard)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  process()
  adhoctest1()
  make_billingcard2()
  """
  # adhoctest1()
  adhoctest2()
