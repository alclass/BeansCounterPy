#!/usr/bin/env python3
"""
art/immeubroutes/rent/bill/discontinued_mora_calc_month_n_list.py
  This module contains functionality
  for calculating month by month 'moras'

This 'chunking' by month is because IR-indices
  may be different month by month, as, for example,
  in the general case happening with (variable) inflation rates.

The main class here should (regex)use the calculing class MoraMonthCalculator
  in art/immeubroutes/rent/bill/mora_calculator.py
  (see also its docstring)

"""
import calendar
from dinero import Dinero
from dinero.currencies import BRL  # USD, EUR
from dataclasses import dataclass
import datetime
import json
import lib.datesetc.datefs as dtfs # dfs.stringify_date
import lib.finfs.dinerofs.dinserial_fs as dinfs # dfs.stringify_date
import art.immeub.rent.bill as init
import art.immeub.rent.bill.mora_calculator as mc  # mc.MoraMonthCalculator
import art.immeub.rent.models.fatura_maker_w_wo_mora as rmcm  # rmcm.MCRefmonth
IPCA = "IPCA"
MoraMonthCalculator = mc.MoraMonthCalculator
DEFAULT_FIX_IR_PCT = init.DEFAULT_FIX_IR_PCT
DEFAULT_VAR_IR_PCT = init.DEFAULT_VAR_IR_PCT
stringify_date = dtfs.date_to_str_4y_dash_2m_dash_2d
dinero_serializer = dinfs.dinero_serializer


class MonthRangeMoraMounter:
  """
  import lib.datesetc.refmonth_classmod as rmcm  # rmcm.MCRefmonth
  """

  def __init__(self, inimontant, inidate, findate, fix_ir_pct=None):
    self.inimontant = inimontant
    self.ongo = inimontant
    self.inidate = inidate
    self.findate = findate
    self.fix_ir_pct = fix_ir_pct or DEFAULT_FIX_IR_PCT
    # var_ir_pct is fetched by an API (depends on index and month)
    self._mcrefmonthrange: rmcm.MCRefmonthRanger = None

  def fetch_refmonths(self) -> rmcm.MCRefmonthRanger:
    if self._mcrefmonthrange is not None:
      return self._mcrefmonthrange
    self._mcrefmonthrange = rmcm.MCRefmonthRanger(
      inidate=self.inidate,
      findate=self.findate,
    )
    return self._mcrefmonthrange

  @property
  def mcrefmonthrange(self):
    if self._mcrefmonthrange is None:
      self.fetch_refmonths()
      return self._mcrefmonthrange
    return self.mcrefmonthrange.get_ndayslist() or []

  @property
  def ndayslist(self):
    return self.mcrefmonthrange.get_ndayslist() or []

  @property
  def refmonths(self) -> list:
    return self.mcrefmonthrange.get_refmonths() or []

  @property
  def n_months(self):
    return len(self.refmonths)

  @property
  def monecorrlist(self):
    return self.mcrefmonthrange.get_monecorrlist() or []

  def get_fraction_for_exponent(self, i):
    if self.n_months == 0:
      errmsg = f"Error: months are empty when asking for exponent fraction."
      raise ValueError(errmsg)
    if i > self.n_months - 1:
      errmsg = f"Error: asked a month (idx={i}) outside range (total={len(self.n_months)})."
      raise ValueError(errmsg)
    if 0 < i < self.n_months - 1:
      return 1  # it's assumed that in-middle months are full
    numerator = self.ndayslist[i]
    refmonth = self.refmonths[i]
    lastdayinmonth = calendar.monthrange(refmonth.year, refmonth.month)[1]
    if i == 0:
      fraction = (lastdayinmonth - numerator) / lastdayinmonth
      return fraction
    # at this point: i == len(self.refmonths) - 1:
    fraction = numerator / lastdayinmonth
    return fraction

  def calc_total(self):
    """
    finmontant = 0
    for i in range(len(self.moralist)):
      finmontant += self.moralist[i]
    return finmontant

    """
    pass

  def __str__(self):
    finmontant = self.calc_total()
    outstr = f"""
    inidate = {self.inidate}
    findate = {self.findate}
    corrmonetlist = {self.monecorrlist}
    moralist = {self.moralist}
    finmontant = {finmontant}
    """
    return outstr


@dataclass
class MoraBillingItem:
  inimontant: Dinero=None
  _finmontant: Dinero=None
  _moravalue: Dinero=None
  fix_ir_pct: float=0.0
  var_ir_pct: float=0.0
  refmonth: datetime.date=None  # when refmonth is set, ini and fin are None
  ndays: int=None
  # _ndayslist: list=None
  # inidate: datetime.date=None
  # findate: datetime.date=None

  @property
  def fixplusvar_ir_pct(self):
    return self.fix_ir_pct + self.var_ir_pct

  @property
  def fixplusvar_ir_dec(self):
    return self.fixplusvar_ir_pct / 100



  def check_dates_consistency_or_raise(self):
    self.inidate = dtfs.make_date_or_none(self.inidate)
    self.refmonth = dtfs.make_refmonthdate_or_none(self.refmonth)
    self.findate = dtfs.make_date_or_today(self.findate)
    if self.refmonth is not None:
      if self.inidate is not None:
        errmsg = f"Error: refmonth={self.refmonth} | inidate={self.inidate} | findate={self.findate}"
        errmsg += "\n\t if refmonth is set, inidate cannot be set."
        raise ValueError(errmsg)
    if self.inidate is None:
      if self.refmonth is None:
        errmsg = f"Error: refmonth={self.refmonth} | inidate={self.inidate} | findate={self.findate}"
        errmsg += "\n\t if refmonth and inidate cannot be both None."
        raise ValueError(errmsg)

  @property
  def moravalue(self):
    if self._moravalue is not None:
      return self._moravalue
    # choose one of two cases
    self.check_dates_consistency_or_raise()
    if self.refmonth is not None:
      self._moravalue = self.inimontant * self.fixplusvar_ir_dec
      return self._moravalue
    elif self.inidate is None:
        errmsg = (f"Error: inidate is None when refmonth is also None."
                  f" \n\t One of them should have been set.")
        raise ValueError(errmsg)
    # okay, though refmonth is None, inidate is set
    mmc = MoraMonthCalculator(
      ini_montant=self.inimontant,
      fix_ir_pct=self.fix_ir_pct,
      var_ir_pct=self.var_ir_pct,
      ini_date=self.inidate,
      fin_date=self.findate,
    )
    self._moravalue = mmc.inbetween_mora
    return self._moravalue

  @property
  def finmontant(self):
    if self._finmontant is not None:
      return self._finmontant
    if self.refmonth:
      self._finmontant = self.ini_montant + self.moravalue
    return self._finmontant


class MoraMonthChunksCalculator:
  """
  This class has its attributes calculated once,
    and then they should be considered immutable,
    i.e., they should not be recaculated,
    if recalculation is needed (due to updating attributes),
      the "client called" shoula instantiate a new object
  """

  def __init__(self, refmonth):
    self.refmonth = refmonth
    self.chargeitems = []  # a list of mora-billing items
    self.treat_params()

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


def adhoctest1():
  mrmm = MonthRangeMoraMounter(
    inidate="2026-01-07",
    findate="2026-04-17",
    inimontant=1000,
    fix_ir_pct=0.02,
  )
  print(mrmm)


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
  adhoctest1()
  process()
  """
  adhoctest1()
