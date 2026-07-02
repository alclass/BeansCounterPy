#!/usr/bin/env python3
"""
art/immeub/models/billing_mod.py

"""
import locale
import datetime
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, field
from dinero import Dinero
from dinero.currencies import BRL  # USD, EUR
import lib.datesetc.refmonths_mod as rm
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
MONTHS = rm.MONTHS


@dataclass
class Mora:
  """
  Models a Mora object.
  Notice that:
   1 - this class, once calculated mora (lazily),
     does not recalculate it a second time
     (a kind of immutability for this class-attribute);
   2 - "val_after" is initialized with -1 in place of None,
     "val_after" is never negative and is, by convention,
     never less than "val_before"
  """
  descr: str
  ori_refmont: datetime.date
  to_date: datetime.date
  val_before: Dinero
  fix_mo_intrst: float = 0.01
  var_mo_intrst: float = 0.0
  comment: str = ""
  _val_after: Dinero = field(default_factory=lambda: Dinero("-1", BRL))

  @property
  def elapsed_months(self):
    delta = relativedelta(self.to_date, self.ori_refmont)
    months = delta.months
    days = delta.days
    days_fraction = days / 30  # conventioned
    months_n_fraction = months + days_fraction
    return months_n_fraction

  @property
  def fix_plus_var(self):
    return self.fix_mo_intrst + self.var_mo_intrst

  def increase_or_one(self):
    mult = (1 + self.fix_plus_var)**self.elapsed_months
    # because value_after is initialized with -1,
    # mult cannot be less than one, and it's also a convention for mora
    # ie, mora is never negative in the underlying convention to this program
    if mult < 1:
      return 1  # this is the point that avoids val_after being less than val_before
    return mult

  def calc_final_mont(self):
    mult = self.increase_or_one()
    raw = float(self.val_before.raw_amount)
    # mult is a real number equals to 1 or above
    final_mont = raw * mult
    return final_mont

  @property
  def val_after(self):
    if self._val_after.raw_amount < 0:
      f_montant = self.calc_final_mont()
      self._val_after = Dinero(str(f_montant), BRL)
    return self._val_after

  @property
  def val_mora(self):
    if self.val_after.raw_amount < 0:
      return Dinero("0.0", BRL)
    return self.val_after - self.val_before

  def __str__(self):
    di = f"de={self.ori_refmont}"
    df = f"p/={self.to_date}"
    dscr = self.descr
    ms_elap = self.elapsed_months
    ms_elap = locale.format_string("%.2f", ms_elap, grouping=True)
    mora = self.val_mora.raw_amount
    mora = locale.format_string("%.2f", mora, grouping=True)
    pcfix = str(self.fix_mo_intrst * 100) + "%"
    pcvar = str(self.var_mo_intrst * 100) + "%"
    prixfrom = locale.format_string("%.2f", self.val_before.raw_amount, grouping=True)
    prixto = locale.format_string("%.2f", self.val_after.raw_amount, grouping=True)
    outstr = f"{di} | {df} | {dscr} | {prixfrom} | {ms_elap} | %fix={pcfix} | %cm={pcvar} | {mora} | {prixto}"
    return outstr


def adhoctest1():
  today = datetime.date.today()
  strprice = '1000'
  noraitem = Mora(
    descr='mora aluguel',
    ori_refmont=rm.calc_refmonth_minus_n(today, 2),
    to_date=today,
    val_before=Dinero(strprice, BRL)  # Safe string initialization
  )
  # payitem.add_mora()
  print(noraitem)


def process():
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  """
  process()
  adhoctest1()
