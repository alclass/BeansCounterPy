#!/usr/bin/env python3
"""
art/immeubroutes/pydantmodels/billing_mod.py

"""
import locale
import datetime
from prettytable import PrettyTable
import pydantic
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, field
import lib.datesetc.refmonth_fs as rmfs
from decimal import Decimal
import art.immeub.rent.pydantmodels.person_pydant as pers  # pers.PydtcPerson

DECIMAL_ZERO = Decimal("0")


# from art.immeub.rent.pydantmodels.schema_bizmodels import BillingCard

# locale.setlocale(locale.LC_NUMERIC, "pt_BR")  # "pt_BR.UTF-8"
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
MONTHS = rmfs.PT_MESES


class PydtcPayment(pydantic.BaseModel):
  date: datetime.date
  value: Decimal
  payor: pers.PydtcPerson = pydantic.Field(default_factory=lambda: None)
  refdoc: str = pydantic.Field(default_factory=lambda: "ref pagamento")
  comment: str = pydantic.Field(default_factory=lambda: "p/ aluguel e encargos")

class PydtcBillingItem(pydantic.BaseModel):
  seq: int
  descr: str
  refmonth: datetime.date
  value: Decimal
  mora: Decimal = pydantic.dataclasses.Field(default_factory=lambda: None)
  mora_pieces: list[Decimal] = pydantic.dataclasses.Field(default_factory=lambda: [])
  moradate: datetime.date = pydantic.dataclasses.Field(default_factory=lambda: None)

  @property
  def refmmm(self):
    mm = self.refmonth.month
    year = self.refmonth.year
    mmm = MONTHS[mm-1]
    _refmmm = f"{mmm}/{year}"
    return _refmmm

  @property
  def total_mora(self) -> Decimal:
    _total_mora = DECIMAL_ZERO
    for moravalue in self.mora_pieces:
      _total_mora += moravalue
    return _total_mora

  @property
  def total_item(self) -> Decimal:
    return self.total_mora + self.value

  def asdict(self) -> dict:
    odict = {
      'seq': self.seq,
      'descr': self.descr,
      'refmonth': self.refmonth,
      'value': self.value,
      'mora': self.mora,
      'total_item': self.total_item,
    }
    return odict

  class MongoJsonRepr(pydantic.BaseModel):
    seq: int
    descr: str
    refmonth: datetime.date
    value: Decimal
    mora: Decimal = pydantic.dataclasses.Field(default_factory=lambda: None)
    total_item: Decimal

  def instantiate_as_mongojsonrepr_class(self):
    pdict = {key: value for key, value in self.asdict().items() if value is not None}
    return self.MongoJsonRepr(**pdict)

  def get_the_6_line_values_as_lst(self):
    if self.mora is not None:
      mora = f"{self.mora:.02f}"
    else:
      mora = "n/a"
    fmt_value = locale.format_string("%.2f", self.value, grouping=True)
    fmt_total = locale.format_string("%.2f", self.total_item, grouping=True)
    values = [self.seq, self.descr, self.refmmm, fmt_value, mora, fmt_total]
    return values

  def printline(self):
    """
    outstr = f"{self.descr} | {self.refmmm} | {fmt_value} | {self.mora} | {self.total_item}"
    """
    table = PrettyTable()
    headers = ["seq",  "descrição", "data-ref",  "valor", "mora", "total"]
    table.field_names = headers
    values = self.get_the_6_line_values_as_lst()
    table.add_row(values)
    print(table)


  def __str__(self):
    fmt_value = locale.format_string("%.2f", self.value, grouping=True)
    outstr = f"{self.descr} | {self.refmmm} | {fmt_value} | {self.mora} | {self.total_item}"
    return outstr


def adhoctest1():
  """

  today = datetime.date.today()
  """
  refmonth = rmfs.make_current_refmonth()
  strprice = '1000'
  payitem = PydtcBillingItem(
    seq=1,
    descr='aluguel mensal',
    refmonth=refmonth,
    value=Decimal(strprice)  # Safe string initialization
  )
  # payitem.add_mora()
  print(payitem)
  payitem.printline()


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
