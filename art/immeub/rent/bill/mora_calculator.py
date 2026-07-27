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
      ir = interest rate (may have a fix fraction [the ir itself] and a variable one [the mone_corr])
      em = number of months in-between
           (time in months elapsed from dates: initial and final)

Obs:
  o1 - the '**' operator means 'exponentiation'
  o2 - the measure-unit for the exponent is 'months' as mone_corr is calculated based on 'months' elapsed

Here is an example for an n_months exponent:
==================
  Suppose elapsed 'mora' duration is from '2026-01-01' to '2026-03-01', then n_months = 2.03226;
    the fractional part is due to the inclusive character of date range,
    in this case, March 1st 2026 ('2026-03-01') is included (this one day adds 1/31 to 2),
    the first day, January 1st 2026 ('2026-01-01') is also included.
"""
import copy
from bson.decimal128 import Decimal128
from decimal import Decimal, ROUND_HALF_UP
from dinero import Dinero
from dinero.currencies import BRL  # USD, EUR
import datetime
import lib.datesetc.datefs as dtfs # dfs.stringify_date
import lib.datesetc.refmonth_fs as rmfs # dfs.stringify_date
import lib.finfs.dinerofs.dinserial_fs as dinfs # dfs.stringify_date
import art.immeub.rent.bill as init
DEFAULT_FIX_IR_PCT = init.DEFAULT_FIX_IR_PCT
DEFAULT_VAR_IR_PCT = init.DEFAULT_VAR_IR_PCT
stringify_date = dtfs.date_to_str_4y_dash_2m_dash_2d
dinero_serializer = dinfs.dinero_serializer
CNV_N_DECIMAL_PLACES = 6


def get_cnv_n_decplaces():
  return CNV_N_DECIMAL_PLACES


def get_cnv_n_decplace_mold():
  n_dplaces = get_cnv_n_decplaces()
  decmold = '0.' + '0' * (n_dplaces - 1) + '1'
  decdecmold = Decimal(decmold)
  return decdecmold



class MoraMonthCalculator:
  """
  This class has its attributes calculated once,
    and then they should be considered immutable,

  If a recalculation is needed (due to updating attributes),
    the "client caller" should instantiate a new object.
  """

  def __init__(
      self, initialmontant, inidate,
      findate=None,fix_ir_pct=None, var_ir_pct=None
  ):
    self.initialmontant = initialmontant
    self.inidate = inidate
    self.findate = findate
    self.fix_ir_pct = fix_ir_pct
    self.var_ir_pct = var_ir_pct
    self.treat_params()
    self._finalmontant = None
    self._mora_increment = None
    self._days_elapsed = None
    self._months_elapsed = None
    self._comp_ir_multiplier = None

  def treat_params(self):
    if not isinstance(self.initialmontant, Dinero):
      self.initialmontant = Dinero(str(self.initialmontant), BRL)
    self.inidate = dtfs.make_date_or_raise(self.inidate)
    self.findate = dtfs.make_date_or_today(self.findate)
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
  def days_elapsed(self):
    """
    For rent mora, the first day should be counted (i.e., 'border' days are included),

    Example:
      if initial day is 2 and final day is 23,
      total is: (23 - 2) + 1 = 22 days in-between (not as 23-2=21).
    """
    if self._days_elapsed is None:
      datedelta = self.findate - self.inidate
      self._days_elapsed = datedelta.days + 1
    return self._days_elapsed

  def calc_dec_n_months_between_ini_n_fin(self) -> Decimal:
    """
    @see an example above and also docstr for the library function below.
    """
    n_decplaces = get_cnv_n_decplaces()
    dec_n = rmfs.calc_dec_n_months_inbetween(self.inidate, self.findate, n_decplaces=n_decplaces)
    return dec_n

  @property
  def months_elapsed(self) -> Decimal:
    if self._months_elapsed is None:
      self._months_elapsed = self.calc_dec_n_months_between_ini_n_fin()
    return self._months_elapsed

  @property
  def fix_ir_dec(self) -> Decimal:
    _fix = self.fix_ir_pct / 100.0
    _fix = Decimal(_fix)
    return _fix

  @property
  def var_ir_dec(self) -> Decimal:
    return self.var_ir_pct / 100.0

  @property
  def fixplusvar_ir_pct(self) -> float:
    return self.fix_ir_pct + self.var_ir_pct

  @property
  def fixplusvar_ir_dec(self) -> Decimal:
    fixplusvar = self.fixplusvar_ir_pct / 100.0
    fixplusvar = Decimal(fixplusvar)
    return fixplusvar

  @property
  def multiplier_for_mora(self) -> Decimal:
    if self._comp_ir_multiplier is None:
      expo = Decimal(self.months_elapsed)
      self._comp_ir_multiplier = (1 + self.fixplusvar_ir_dec) ** expo
      self._comp_ir_multiplier -= 1  # because it's for mora, not for montant_final
    return self._comp_ir_multiplier

  @property
  def multiplier_for_fm(self) -> Decimal:
    """
    'fm' = final montant
    This property is more for explanatory reasons,
      the one used for calculation is multiplier_for_mora above
    """
    return Decimal(1.0) + self.multiplier_for_mora

  @property
  def mora_increment(self) -> Dinero:
    if self._mora_increment is None:
      self._mora_increment = self.initialmontant * self.multiplier_for_mora
      self._mora_increment = Dinero(str(self._mora_increment), BRL)
    return self._mora_increment

  mora = mora_increment

  @property
  def fin_montant(self):
    if self._finalmontant is None:
      self._finalmontant = self.initialmontant + self.mora_increment

    return self._finalmontant

  def asdict_for_json(self):
    """

    """
    serialized = copy.copy(self.asdict)
    for key in serialized:
      value = serialized[key]
      if isinstance(value, Decimal):
        n_dplaces = get_cnv_n_decplaces()
        dp_mold = '0.' + '0'*(n_dplaces-1) + '1'
        places_index = Decimal(str(value))
        decplaces_mold = get_cnv_n_decplace_mold()
        rounded_val = value.quantize(decplaces_mold, rounding=ROUND_HALF_UP)
        serialized[key] = Decimal128(rounded_val)
    return serialized

  @property
  def asdict(self):
    pditc = {
      'initial montant': dinero_serializer(self.initialmontant),  # , indent=2
      'initial date': stringify_date(self.inidate),
      'final date': stringify_date(self.findate),
      'fix ir pct': self.fix_ir_pct,
      'var ir pct': self.var_ir_pct,
      'number of months': self.months_elapsed,
      'compound multiplier for fm': self.multiplier_for_fm,
      'final montant': dinero_serializer(self.fin_montant),
    }
    return pditc

  def __str__(self):
    fixpct = f"{self.fix_ir_pct:0.2f}"
    varpct = f"{self.var_ir_pct:0.2f}"
    n_months = f"{self.months_elapsed:0.2f}"
    outstr = f"""{self.__class__.__name__}:
    initial montant = {self.initialmontant} | dateini = {self.inidate} | datefim = {self.findate}
    elapsed: months = {n_months} | days = {self.days_elapsed} | multiplier = {self.multiplier_for_mora:.04f}
    fix_ir_pct = {fixpct}%  | var_ir_pct = {varpct}% | fix_plus_var = {self.fixplusvar_ir_pct}%
    mora increment = {self.mora} | final montant = {self.fin_montant}
    """
    return outstr


def adhoctest1():
  basevalue = 100
  dateini = datetime.datetime(2026, 1, 1).date()
  datefim = datetime.datetime(2026, 3, 1).date()
  mo = MoraMonthCalculator(basevalue, dateini, datefim)
  print(mo)
  print('json', mo.asdict_for_json())
  print('2nd test')
  print('='*40)
  mo = MoraMonthCalculator(basevalue, dateini, datefim, fix_ir_pct=0, var_ir_pct=0)
  print(mo)
  print('json', mo.asdict_for_json())


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
