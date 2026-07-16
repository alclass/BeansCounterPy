#!/usr/bin/env python3
"""
art/immeubroutes/rent/models/fatura_maker_w_wo_mora.py
  Contains monthly and refmonthly date functions.

import fs.datefs.introspect_dates as intr
from typing import Union
from dateutil.relativedelta import relativedelta
from patsy import desc
import lib.datesetc.datefs as dfs  # dfs.transform_strdate_to_date
import lib.datesetc.datehilofs as hilo  # dfs.transform_strdate_to_date
# from sqlalchemy.testing import exclude
"""
import calendar
import copy
import datetime
import lib.datesetc.datefs as dtfs
from dinero import Dinero
from dinero.currencies import BRL
import lib.datesetc.refmonth_fs as rmfs  # refmonth_fs.py.fillin_refmonths_fr_ndayslist
import lib.finfs.indices.indices_fetch_n_fs as cmfs  # refmonth_fs.py.fillin_refmonths_fr_ndayslist
from dataclasses import dataclass  # , field
import art.immeub.rent.bill as init  # refmonth_fs.py.fillin_refmonths_fr_ndayslist
DEFAULT_FIX_IR_PCT = init.DEFAULT_FIX_IR_PCT  # this is percentual
DEFAULT_FIX_IR_DEC = DEFAULT_FIX_IR_PCT / 100  # this is decimal


@dataclass
class EachRefmonth:
  """
  This dataclass does not calculate 'mora', it does not receive 'inimontant' (initial montant),
    it aims to 'carry' data for the 'downstream calculator' which calculates 'mora' and contains 'inimontant'
    (this latter comes as the following class)
  """
  oridate: datetime.date
  refmonth: datetime.date
  ndays: int
  is_first_in_monthrange: bool = False
  is_last_in_monthrange: bool = False
  _var_ir_dec: float = None  # to be fetched based on refmonth
  _monthsfraction: float = None
  # these attributes are filled later on in the downstream class 'mounter' (or calculator)
  moraparcel: Dinero = None
  incrfactor: float = None  # increase factor
  fix_ir_dec: float = None  # the fix Interest Rate index that comes in here from the downstream calculator

  @property
  def fix_ir_pct(self):
    return self.fix_ir_dec * 100 if self.fix_ir_dec is not None else None

  @property
  def var_ir_pct(self):
    return self.var_ir_dec * 100 if self.var_ir_dec is not None else None

  @property
  def basemontant(self):
    """
    basemontant is the base value that 'generated' the mora amount
    """
    if self.moraparcel is not None and self.incrfactor is not None:
      return self.moraparcel / self.incrfactor
    return None

  @property
  def baseplusmora(self):
    """
    basemontant is the base value that 'generated' the mora amount
    """
    if self.basevalue is None:
      return None
    if self.moraparcel is None:
      return None
    # noinspection PyUnresolvedReferences
    _baseplusmora = self.basevalue + self.moraparcel
    return _baseplusmora

  @property
  def totalmonthdays(self):
    return calendar.monthrange(self.oridate.year, self.oridate.month)[1]

  @property
  def fraction_days_in_refmonth(self):
    """
    Returns a fraction-number between 0 exclusive and 1 inclusive
    Noting:
      1 if all days in month, return-fraction is 1 (the whole month)
      2 generally, it returns days_available/days_in_month
      3 in this system, it doesn't make sense 0 days available, so 0 is excluded (logically) as return value

    Example:
      In a month with 30 days (April, June, September, November),
      if 15 days were 'taken', fraction is 15/30 or 1/2 or, in decimal, 0.5
    """
    if self._monthsfraction is not None:
      return self._monthsfraction
    if not self.is_first_in_monthrange and not self.is_last_in_monthrange:
      self._monthsfraction = 1.0
      return self._monthsfraction
    t = self.totalmonthdays
    if self.is_first_in_monthrange:
      self._monthsfraction = (t - self.oridate.day + 1) / t
      return self._monthsfraction
    # at this point: self.is_last_in_monthrange is True:
    self._monthsfraction = self.oridate.day / t
    return self._monthsfraction

  @property
  def var_ir_dec(self):
    if self._var_ir_dec is None:
      self._var_ir_dec = cmfs.ipca_for_refmonth(self.refmonth)
    return self._var_ir_dec

  @property
  def incrfactor_pct(self):
    """ increase factor percentual """
    if self.incrfactor is None:
      return None
    _incrfactor_pct = self.incrfactor * 100
    return _incrfactor_pct

  @property
  def multiplier(self):
    """
    multiplier is incrfactor (increase factor) plus 1
    """
    if self.incrfactor is not None:
      return self.incrfactor + 1
    return None

  @property
  def basevalue(self):
    """
    The initial montant (based value) that 'produces' mora
    It is computed (dynamically) by dividing moraparcel by increaser
    """
    if self.moraparcel is not None and self.incrfactor is not None:
      return self.moraparcel / self.incrfactor
    return None

  def itemline(self):
    extmes = rmfs.get_3letter_extmes(self.refmonth.month)
    incrfactor_pct = f"{self.incrfactor_pct:.2f}%" if self.incrfactor_pct is not None else 'n/a'
    line = f"ref {extmes}/{self.refmonth.year} | fatormora={incrfactor_pct} | {self.moraparcel}"
    return line

  def __str__(self):
    monthfraction = self.fraction_days_in_refmonth
    basevalue = self.basevalue or 'n/a'
    baseplusmora = self.baseplusmora or 'n/a'
    multiplier = f"{self.multiplier:.4f}" if self.multiplier is not None else 'n/a'
    incrfactor_pct = f"{self.incrfactor_pct:.2f}%" if self.incrfactor_pct is not None else 'n/a'
    fix_ir_pct = f"{self.fix_ir_pct:.2f}%" if self.fix_ir_pct is not None else 'n/a'
    var_ir_pct = f"{self.var_ir_pct:.2f}%" if self.var_ir_pct is not None else 'n/a'
    outstr = f"""{self.__class__.__name__}  
    refmonth={self.refmonth} | oridate={self.oridate}
    first_in_range={self.is_first_in_monthrange} | last_in_range={self.is_last_in_monthrange}
    ndays={self.ndays} | total={self.totalmonthdays} | monthfraction={monthfraction:.3f}
    var_ir_dec={var_ir_pct} | fix_ir_dec={fix_ir_pct} | increase={incrfactor_pct}  | mult={multiplier}
    moraparcel={self.moraparcel} | base={basevalue} | atual={baseplusmora}
    """
    return outstr


@dataclass
class EachRefmonthMora:
  """
  """
  refmonth: datetime.date
  moradinero: Dinero
  multiplier: float


class MCRefmonthRanger:
  """
  MC stands for "Monetary Correction"
  It aims at joining refmonths and their MC indices
  """

  def __init__(self, inidate, findate, inimontant, fix_ir_dec=None, descr=None):
    self.inidate = inidate
    self.findate = findate
    self.inimontant = inimontant
    self.fix_ir_dec = fix_ir_dec or DEFAULT_FIX_IR_DEC  # notice it's "dec" (decimal) not "pct" (percentual)
    self.descr = descr
    self.cmrefmonths: list[EachRefmonth] = []
    self.incrfactors: list[float] = []
    self.fatura_total: Dinero | None = None
    self.treat_attrs()

  def treat_attrs(self):
    self.inidate = dtfs.make_date_or_raise(self.inidate)
    self.findate = dtfs.make_date_or_today(self.findate)
    self.fillindata()
    if not isinstance(self.inimontant, Dinero):
      self.inimontant = Dinero(str(self.inimontant), BRL)

  def fetch_n_store_cmrefmonths(self):
    """
    The 'fetch' verb prefixing the methodname is because EachRefmonth objects
      need to db-fetch (but data may come from files or API's) its refmonth's monetary correction index.
    """
    tuplelist = rmfs.mount_ndays_n_refmonth_tuplelist(
      self.inidate,
      self.findate
    )
    for i in range(len(tuplelist)):
      is_first, is_last = False, False
      refmonth = tuplelist[i][1]
      oridate = copy.copy(refmonth)
      if i == 0:
        is_first = True
        oridate = self.inidate
      if i == len(tuplelist) - 1:
        is_last = True
        oridate = self.findate
      erf = EachRefmonth(
        oridate=oridate,
        refmonth=refmonth,
        ndays=tuplelist[i][0],
        is_first_in_monthrange=is_first,
        is_last_in_monthrange=is_last,
      )
      self.cmrefmonths.append(erf)

  def fillindata(self):
    self.fetch_n_store_cmrefmonths()

  def get_ndayslist(self):
    ndayslist = map(lambda o: o.ndayslist, self.cmrefmonths)
    return list(ndayslist)

  def get_refmonths(self):
    refmonths = map(lambda o: o.refmonth, self.cmrefmonths)
    return list(refmonths)

  def get_monecorrlist(self):
    monecorrlist = map(lambda o: o.var_ir_dec, self.cmrefmonths)
    return list(monecorrlist)

  def get_moraparcels(self):
    moraparcels = map(lambda o: o.moraparcel, self.cmrefmonths)
    return list(moraparcels)

  def calculate_moraparcels(self):
    """
    moralist means "moral list"
    """
    _moraparcels = []
    faturatotal = self.inimontant
    fix_idx = self.fix_ir_dec
    for cmrm in self.cmrefmonths:
      var_idx = cmrm.var_ir_dec
      fixplusvar = fix_idx + var_idx
      exponent = cmrm.fraction_days_in_refmonth
      moraincrfactor = cmfs.get_ir_incrfactor_for_mora_w_iridx_n_expo(
        ir_idx=fixplusvar, exponent=exponent
      )
      self.incrfactors.append(moraincrfactor)  # multiplier is increaser plus 1
      moraparcel = faturatotal * moraincrfactor
      cmrm.moraparcel = moraparcel
      cmrm.incrfactor = moraincrfactor
      cmrm.fix_ir_dec = self.fix_ir_dec
      faturatotal += moraparcel
    self.fatura_total = faturatotal

  def calculate(self):
    self.fetch_n_store_cmrefmonths()
    self.calculate_moraparcels()

  def __str__(self):
    outstr = ""
    for i, erf in enumerate(self.cmrefmonths):
      seq = i + 1
      outstr += "\n" + str(seq) + " => " + str(erf)
      outstr += "\n" + erf.itemline()
    return outstr


def adhoctest1():
  inidate = "2026-01-10"
  findate = "2026-04-07"
  inimontant = Dinero("1000", BRL)
  mcr = MCRefmonthRanger(
    inidate=inidate,
    findate=findate,
    inimontant=inimontant,
    descr="aluguel base & mora")
  mcr.calculate()
  print(mcr)
  print('fatura_total', mcr.fatura_total)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
