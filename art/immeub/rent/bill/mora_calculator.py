#!/usr/bin/env python3
"""
art/immeubroutes/rent/bill/mora_calculator.py
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
import lib.datesetc.datefs as dtfs # dfs.stringify_date
import lib.finfs.dinerofs.dinserial_fs as dinfs # dfs.stringify_date
import art.immeub.rent.bill as init
DEFAULT_FIX_IR_PCT = init.DEFAULT_FIX_IR_PCT
DEFAULT_VAR_IR_PCT = init.DEFAULT_VAR_IR_PCT
stringify_date = dtfs.date_to_str_4y_dash_2m_dash_2d
dinero_serializer = dinfs.dinero_serializer


class MoraMonthCalculator:
  """
  This class has its attributes calculated once,
    and then they should be considered immutable,
    i.e., they should not be recaculated,
    if recalculation is needed (due to updating attributes),
      the "client called" shoula instantiate a new object
  """

  def __init__(
      self, ini_montant, ini_date,
      fin_date=None,fix_ir_pct=None, var_ir_pct=None
  ):
    self.ini_montant = ini_montant
    self.ini_date = ini_date
    self.fin_date = fin_date
    self.fix_ir_pct = fix_ir_pct
    self.var_ir_pct = var_ir_pct
    self.treat_params()
    self._fin_montant = None
    self._inbetween_mora = None
    self._inbetween_days = None
    self._inbetween_months = None
    self._comp_ir_multiplier = None

  def treat_params(self):
    if not isinstance(self.ini_montant, Dinero):
      self.ini_montant = Dinero(str(self.ini_montant), BRL)
    self.ini_date = dtfs.make_date_or_raise(self.ini_date)
    self.fin_date = dtfs.make_date_or_today(self.fin_date)
    # treat self.fix_ir_pct
    try:
      self.fix_ir_pct = float(self.fix_ir_pct)
    except (TypeError, ValueError):
      self.fix_ir_pct = DEFAULT_FIX_IR_PCT
    # treat self.var_ir_pct
    try:
      self.var_ir_pct = float(self.var_ir_pct)
    except (TypeError, ValueError):
      self.var_ir_pct = DEFAULT_VAR_IR_PCT

  @property
  def inbetween_days(self):
    """
    For rent mora, the first day should be counted,
      i.e., if initial day is 1 and final day is 20,
        total is: 20 - 1 + 1 = 20, i.e., 20 days in-between.
    """
    if self._inbetween_days is None:
      datedelta = self.fin_date - self.ini_date
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
    # case 1 ini begins on day 1
    year = self.fin_date.year
    month = self.fin_date.month
    if year == self.ini_date.year and month == self.ini_date.month:
      _, n_of_days_in_month = calendar.monthrange(year, month)
      return self.inbetween_days / n_of_days_in_month
    # case 2 ini begins after day 1
    # case 2 ini and fin are in the same month

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
    return 1.0 + self.multiplier_for_mora

  @property
  def inbetween_mora(self):
    if self._inbetween_mora is None:
      self._inbetween_mora = self.ini_montant * self.multiplier_for_mora
      self._inbetween_mora = Dinero(str(self._inbetween_mora), BRL)
    return self._inbetween_mora

  mora = inbetween_mora

  @property
  def fin_montant(self):
    if self._fin_montant is None:
      self._fin_montant = self.ini_montant + self.inbetween_mora

    return self._fin_montant

  def as_json(self):
    return json.dumps(self.asdict)

  @property
  def asdict(self):
    pditc = {
      'initial montant': dinero_serializer(self.ini_montant),  # , indent=2
      'initial date': stringify_date(self.ini_date),
      'final date': stringify_date(self.fin_date),
      'fix ir pct': self.fix_ir_pct,
      'var ir pct': self.var_ir_pct,
      'number of months': self.inbetween_months,
      'compound multiplier for fm': self.multiplier_for_fm,
      'final montant': dinero_serializer(self.fin_montant),
    }
    return pditc

  def __str__(self):
    fixpct = f"{self.fix_ir_pct:0.2f}"
    varpct = f"{self.var_ir_pct:0.2f}"
    n_months = f"{self.inbetween_months:0.2f}"
    outstr = f"""
    initial montant = {self.ini_montant}
    dateini = {self.ini_date} | fix_ir_pct = {fixpct}%
    datefim = {self.fin_date} | var_ir_pct = {varpct}%
    elapsed: months = {n_months} | days = {self.inbetween_days}
    mora = {self.mora}
    final montant = {self.fin_montant}
    """
    return outstr


def process():
  basevalue = 100
  dateini = datetime.datetime(2026, 1, 1).date()
  datefim = datetime.datetime(2026, 3, 1).date()
  mo = MoraMonthCalculator(basevalue, dateini, datefim)
  print(mo)
  print('json', mo.as_json())
  print('2nd test')
  print('='*40)
  mo = MoraMonthCalculator(basevalue, dateini, datefim, fix_ir_pct=0, var_ir_pct=0)
  print(mo)
  print('json', mo.as_json())


if __name__ == "__main__":
  """
  adhoctest3()
  """
  process()
