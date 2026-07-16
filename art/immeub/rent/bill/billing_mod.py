#!/usr/bin/env python3
"""
art/immeubroutes/models/billing_mod.py

"""
import locale
import datetime
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, field
from lib.datesetc import rmfs
from dinero import Dinero
# locale.setlocale(locale.LC_NUMERIC, "pt_BR")  # "pt_BR.UTF-8"
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
import lib.datesetc.rmfs as rm
MONTHS = rm.MONTHS


@dataclass
class PayItem:
  seq: int
  descr: str
  ori_refmont: datetime.date
  price: Dinero
  mora: Dinero | None = None
  mora_pieces: list[Dinero] = field(default_factory=list)
  moradate: datetime.date | None = None

  @property
  def refmmm(self):
    mm = self.ori_refmont.month
    year = self.ori_refmont.year
    mmm = MONTHS[mm-1]
    _refmmm = f"{mmm}/{year}"
    return _refmmm

  @property
  def total_mora(self):
    _total_mora = 0
    for mora in self.mora_pieces:
      _total_mora += mora.raw_amount
    return _total_mora

  @property
  def total_item(self):
    return self.total_mora + self.price

  def __str__(self):
    price_frm = locale.format_string("%.2f", self.price.raw_amount, grouping=True)
    outstr = f"{self.descr} | {self.refmmm} | {price_frm} | {self.mora} | {self.total_item}"
    return outstr


class Biller:

  def __init__(self, refmonth, immeub):
    self.refmonth = refmonth
    self.immeub = immeub
    self.today = datetime.date.today()
    self.rent_value = None
    self.pay_lines = []

  def process(self):
    self.rent_value = self.immeub.get_current_rent_value()
    self.pay_lines.append(self.rent_value)


def process():
  today = datetime.date.today()
  strprice = '1000'
  payitem = PayItem(
    seq=1,
    descr='aluguel',
    ori_refmont=rm.make_refmonthdate_or_none(today),
    price=Dinero(strprice, BRL)  # Safe string initialization
  )
  # payitem.add_mora()
  print(payitem)


if __name__ == "__main__":
  """
  adhoctest3()
  """
  process()
