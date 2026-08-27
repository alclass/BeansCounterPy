#!/usr/bin/env python3
"""
art/immeubroutes/pdntcmdls/billing_mod.py
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, field
"""
import locale
import datetime
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable
import pydantic
import lib.datesetc.refmonth_fs as rmfs
from decimal import Decimal
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.PydtcPerson
import art.immeub.rent.create_adhoc_objects.prettytable_bitems as ppbitems  # ppbitems.PrettyTableForBI
DECIMAL_ZERO = Decimal("0")
# from art.immeub.rent.pdntcmdls.schema_bizmodels import BillingCard
# locale.setlocale(locale.LC_NUMERIC, "pt_BR")  # "pt_BR.UTF-8"
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
MONTHS = rmfs.PT_MESES



def make_4_billingitems():
  """
  Instantiates 4 billing items example.
  """
  refmonth = rmfs.make_current_refmonth()
  strprice = '2000'
  ptable = ppbitems.PrettyTableForBI()
  billingitems = []
  payitem = PydtcBillingItem(
    seq=1,
    descr='aluguel mensal',
    refmonth=refmonth,
    value=Decimal(strprice)  # Safe string initialization
  )
  billingitems.append(payitem)
  # payitem.add_mora()
  ptable.add_to_table(payitem)
  # =========================
  payitem = PydtcBillingItem(
    seq=2,
    descr='tarifa mensal condomínio',
    refmonth=refmonth,
    value=Decimal(1258)  # Safe string initialization
  )
  billingitems.append(payitem)
  # payitem.add_mora()
  ptable.add_to_table(payitem)
  # =========================
  payitem = PydtcBillingItem(
    seq=3,
    descr='IPTU prefeitura p/ 2 de 10',
    refmonth=refmonth,
    value=Decimal(550)  # Safe string initialization
  )
  billingitems.append(payitem)
  # payitem.add_mora()
  ptable.add_to_table(payitem)
  # =========================
  morarefmonth = rmfs.make_refmonth_it_minus_n_or_raise(refmonth, 1)
  payitem = PydtcBillingItem(
    seq=4,
    descr='mora aluguel/encargos',
    refmonth=morarefmonth,
    value=Decimal(450),  # Safe string initialization
  )
  billingitems.append(payitem)
  # payitem.add_mora()
  # payitem.printline()
  ptable.add_to_table(payitem)
  print(ptable.table)
  values = [bi.total_item for bi in billingitems]
  total = sum(values)
  print('total', total)
  return billingitems


class PydtcPayment(pydantic.BaseModel):
  """
  @see also a simplified version
    which is a @dataclass with only fields date and value
  """
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
  qtd: int = 1
  comments: str = ""

  @property
  def total_item(self) -> Decimal:
    return self.value * self.qtd

  @property
  def refmmm(self):
    mm = self.refmonth.month
    year = self.refmonth.year
    mmm = MONTHS[mm-1]
    _refmmm = f"{mmm}/{year}"
    return _refmmm

  def asdict(self) -> dict:
    odict = {
      'seq': self.seq,
      'descr': self.descr,
      'refmonth': self.refmonth,
      'value': self.value,
      'mora': self.mora_incr,
      'total_item': self.total_item,
    }
    return odict

  def get_the_4_billingitem_values_as_lst(self):
    fmt_value = locale.format_string("%.2f", self.value, grouping=True)
    values = [self.seq, self.descr, self.refmmm, fmt_value]
    return values

  def printline(self):
    """
    outstr = f"{self.descr} | {self.refmmm} | {fmt_value} | {self.mora} | {self.total_item}"
    """
    table = PrettyTable()
    headers = ["seq",  "descrição", "testdata-ref",  "valor"]
    table.field_names = headers
    values = self.get_the_4_billingitem_values_as_lst()
    table.add_row(values)
    print(table)

  def __str__(self):
    fmt_value = locale.format_string("%.2f", self.value, grouping=True)
    outstr = f"{self.descr} | {self.refmmm} | {fmt_value} | {self.mora_incr} | {self.total_item}"
    return outstr



def adhoctest1():
  scrmsg = "Look at ahdoctest make_4_billingitems() in module [billingitems_createdata.py]."
  print(scrmsg)


def process():
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
  make_4_billingitems()
