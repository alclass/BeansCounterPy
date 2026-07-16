#!/usr/bin/env python3
"""
art/immeub/rent/apuracao/closemonthmod.py

"""
import locale
import datetime
from dateutil.relativedelta import relativedelta
from dataclasses import asdict, dataclass, field
from dinero import Dinero
# locale.setlocale(locale.LC_NUMERIC, "pt_BR")  # "pt_BR.UTF-8"
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
import lib.datesetc.refmonth_fs as rmfs
MONTHS = rmfs.MONTHS


@dataclass
class FaturaClosedRec:
  """
  The closing may be automatic,
    but for the being, it needs to be made manually
    because of the manual input of payment information or lack of it on date.

  A fatura_closed_rec stores the following data/attributes:
    1 - the unique id of fatura (a link to its register)
        (the unique id informs 'immeub', 'refmonth', and rev_letter)
    2 - datetime (or timestamp) of closing
    3 - comment that may be an autoline informing debt or creait to carry on in the next refmonth

  As a "side effect", the following data will be recorded in the fatura:
    1 - the total paid fatura
    2 - a dictlist for the pay docs (one or more if pay happened)
    3 - the remaining (debt or credit, if any, it will be taken (carried on) in the next refmonth)
        Reminding fatura-codes:
          AE means Aluguel-ou-Encargo
          MO means "mora" (debts become M lines)
          DC means "different of/on credit" (a credit becomes a DC line)
    4 - 1 (true) to flag 'is_closed' (which should 'freeze' the record)
  """
  seq: int
  descr: str
  refmonth: datetime.date
  closedate: datetime.date
  fatura_uniq_id: str  # this is upper(nickname)+"yyyymm"+<rev_letter>
  paid_at_moment: Dinero = None
  remaining_ifany: Dinero = None

  def fetch_last_fatura_in_mongo(self, mongocoll):
    docs = mongocoll.filter({
      'refmonth': self.refmonth,
    })
    if len(docs) == 0:
      return None
    if len(docs) == 1:
      fatura = docs[0]
      return fatura
    uniq_fieldname = 'fat_unique'
    docs.sort(lambda key: docs[uniq_fieldname])
    fatura = docs[-1]
    return fatura

  def to_json_for_mongo(self):
    return asdict(self)

  def save_closed_to_mongo(self, mongocoll):
    mongocoll.upsert(self.to_json_for_mongo())

  def __str__(self):
    price_frm = locale.format_string("%.2f", self.price.raw_amount, grouping=True)
    outstr = f"{self.descr} | {self.refmmm} | {price_frm} | {self.mora} | {self.total_item}"
    return outstr


def adhoctest1():
  pass


def process():
  pass


if __name__ == "__main__":
  """
  adhoctest3()
  """
  process()
