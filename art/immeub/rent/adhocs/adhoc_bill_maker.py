#!/usr/bin/env python3
"""
art/immeubroutes/pydantmodels/adhoc_bill_maker.py

"""
import locale
from art.immeub.rent.bill.billingcard_pydantic import PayItem
from dinero import Decimal
from dinero.currencies import BRL  # USD, EUR
import datetime
import lib.datesetc.rmfs as rm
MONTHS = rm.PT_MESES
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
# Throws DifferentCurrencyError automatically:
# total + Dinero("5.00", EUR)


def process():
  today = datetime.date.today()
  strprice = '1000'
  payitem = PayItem(
    seq=1,
    descr='aluguel',
    refmonth=rm.make_refmonth_or_raise(today),
    price=Decimal(strprice, BRL)  # Safe string initialization
  )
  # payitem.add_mora()
  print(payitem)


if __name__ == "__main__":
  """
  adhoctest3()
  """
  process()
