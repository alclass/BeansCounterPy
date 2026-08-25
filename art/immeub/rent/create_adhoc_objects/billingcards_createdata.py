#!/usr/bin/env python3
"""
art/immeub/rent/testdata/billingcards_createdata.py

import art.immeub.rent.testdata.billingcards_createdata.py
art.immeub.rent.pdntcmdls.contract_molder.Person
import copy
"""
import datetime
from decimal import Decimal
import art.immeub.rent.create_adhoc_objects.rentcontracts_createdata as rc_create  # rc_create.make_rentcontract_1
import art.immeub.rent.billmodels.billingcard_pydantic as bcard  # bcard.PydtcBillingCard
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs


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
  json_str = billingcard.as_json_str()
  print('as_json_str =>', json_str)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
