#!/usr/bin/env python3
"""
art/immeub/rent/bill/mora_calculator.py
  When a mora context happens (incidence),
    a compound interest calculation aims to add
    the contractual 'adjusts' to rent due to its incidence

How to Calculate "Final Montant"
================================

A monthly compound interest "final montant" calculation is as follows:
  fm = im * (1 + ir) ** em
    where:
      fm = final montant
      im = initial montant
      ir = interest rate
      em = number of months in-between
           (time in months elapsed from dates: initial and final)
The '**' operator means 'exponentiation'
"""
import calendar
from dinero import Dinero
from dinero.currencies import BRL  # USD, EUR
import datetime
import json


def stringify_date(pdate):
  """
  """
  try:
    return str(pdate)
  except (TypeError, ValueError):
    pass
  year = pdate.year
  month = pdate.month
  day = pdate.day
  strdate = f"{year}-{month:02d}-{day:02d}"
  return strdate


def dinero_serializer(obj):
  """
  # Serialize to a JSON string
  """
  if isinstance(obj, Dinero):
    return {
      "amount": str(obj.amount),  # Convert Decimal to string
      "currency": obj.currency
    }
  raise TypeError("Type not serializable")


class MoraMonthCalculator:
  """
  This class has its attributes calculated once,
    and then they should be considered immutable,
    i.e., they should not be recaculated,
    if recalculation is needed (due to updating attributes),
      the "client called" shoula instantiate a new object
  """

  def __init__(self, montant_ini, dateini, datefim):
    if not isinstance(montant_ini, Dinero):
      self.montant_ini = Dinero(str(montant_ini), BRL)
    self.dateini = dateini
    self.datefim = datefim
    self._montant_fim = None
    self._inbetween_mora = None
    self._inbetween_days = None
    self._inbetween_months = None
    self._comp_ir_multiplier = None
    self.fix_ir_pct = 10.0
    self.var_ir_pct = 5.0

  @property
  def inbetween_days(self):
    """
    For rent mora, the first day should be counted,
      i.e., if initial day is 1 and final day is 20,
        total is: 20 - 1 + 1 = 20, i.e., 20 days in-between.
    """
    if self._inbetween_days is None:
      datedelta = self.datefim - self.dateini
      self._inbetween_days = datedelta.days + 1
    return self._inbetween_days

  def calc_inbetween_months(self):
    """
    Example of how to calculate number of days in month:
      import calendar
      year = 2024  # Leap year
      month = 2    # February
      # monthrange returns a tuple: (weekday_of_first_day, number_of_days)
      days_in_month = calendar.monthrange(year, month)[1]
      print(days_in_month)  # Output: 29
    """
    year = self.datefim.year
    month = self.datefim.month
    _, n_of_days_in_month = calendar.monthrange(year, month)
    return self.inbetween_days / n_of_days_in_month

  @property
  def inbetween_months(self):
    if self._inbetween_months is None:
      self._inbetween_months = self.calc_inbetween_months()
    return self._inbetween_months

  @property
  def fix_ir_dec(self):
    return self.fix_ir_pct / 100.0

  @property
  def var_ir_dec(self):
    return self.var_ir_pct / 100.0

  @property
  def fixplusvar_ir_pct(self):
    return self.fix_ir_pct + self.var_ir_pct

  @property
  def fixplusvar_ir_dec(self):
    return self.fixplusvar_ir_pct / 100.0

  @property
  def multiplier_for_mora(self):
    if self._comp_ir_multiplier is None:
      self._comp_ir_multiplier = (1 + self.fixplusvar_ir_dec) ** self.inbetween_months
      self._comp_ir_multiplier -= 1  # because it's for mora, not for montant_final
    return self._comp_ir_multiplier

  @property
  def multiplier_for_fm(self):
    """
    'fm' = final montant
    This property is more for explanatory reasons,
      the one used for calculation is multiplier_for_mora above
    """
    return 1 + self.multiplier_for_mora

  @property
  def inbetween_mora(self):
    if self._inbetween_mora is None:
      self._inbetween_mora = self.montant_ini * self.multiplier_for_mora
      self._inbetween_mora = Dinero(str(self._inbetween_mora), BRL)
    return self._inbetween_mora

  mora = inbetween_mora

  @property
  def montant_fim(self):
    if self._montant_fim is None:
      self._montant_fim = self.montant_ini + self.inbetween_mora

    return self._montant_fim

  def as_json(self):
    return json.dumps(self.asdict)

  @property
  def asdict(self):
    pditc = {
      'initial montant': dinero_serializer(self.montant_ini),  # , indent=2
      'initial date': stringify_date(self.dateini),
      'final date': stringify_date(self.datefim),
      'fix ir pct': self.fix_ir_pct,
      'var ir pct': self.var_ir_pct,
      'number of months': self.inbetween_months,
      'compound multiplier for fm': self.multiplier_for_fm,
      'final montant': dinero_serializer(self.montant_fim),
    }
    return pditc

  def __str__(self):
    fixpct = f"{self.fix_ir_pct:0.2f}"
    varpct = f"{self.var_ir_pct:0.2f}"
    n_months = f"{self.inbetween_months:0.2f}"
    outstr = f"""
    initial montant = {self.montant_ini}
    dateini = {self.dateini} | fix_ir_pct = {fixpct}%
    datefim = {self.datefim} | var_ir_pct = {varpct}%
    elapsed: months = {n_months} | days = {self.inbetween_days}
    mora = {self.mora}
    final montant = {self.montant_fim}
    """
    return outstr


def process():
  basevalue = 100
  dateini = datetime.datetime(2026, 1, 1).date()
  datefim = datetime.datetime(2026, 3, 1).date()
  mo = MoraMonthCalculator(basevalue, dateini, datefim)
  print(mo)
  print(mo.asdict)
  print(mo.as_json())


if __name__ == "__main__":
  """
  adhoctest3()
  """
  process()
