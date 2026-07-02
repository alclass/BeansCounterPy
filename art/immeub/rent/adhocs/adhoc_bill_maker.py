#!/usr/bin/env python3
"""
art/immeub/models/adhoc_bill_maker.py

"""
import locale
from art.immeub.rent.bill.billing_mod import PayItem
from dinero import Dinero
from dinero.currencies import BRL  # USD, EUR
import datetime
import lib.datesetc.refmonths_mod as rm
MONTHS = rm.MONTHS
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
# Throws DifferentCurrencyError automatically:
# total + Dinero("5.00", EUR)


def process():
  today = datetime.date.today()
  strprice = '1000'
  payitem = PayItem(
    seq=1,
    descr='aluguel',
    ori_refmont=rm.make_refmonthdate_or_raise(today),
    price=Dinero(strprice, BRL)  # Safe string initialization
  )
  # payitem.add_mora()
  print(payitem)


if __name__ == "__main__":
  """
  adhoctest3()
  """
  process()
