#!/usr/bin/env python3
"""
art/immeub/cdutra/rent/addon_mod.py

"""
from collections import namedtuple
import datetime
from dataclasses import dataclass, field, asdict
from dinero import Dinero
DEFAULT_MUNICIPIONAME = 'Rio de Janeiro - RJ'
reais_baserent = 'reais_baserent'
cond_tariff = 'cond_tariff'
iptu_obj = 'iptu_obj'
fire_comb_obj = 'fire_comb_obj'
monthlyprice_maincomponents_namedtuple = namedtuple(
  'nt_monthlyprice_maincomponents_namedtuple',
  ['reais_baserent', 'cond_tariff', 'iptu_obj', 'fire_comb_obj']
)


@dataclass
class AddOnItem:
  """
  addon_nick: str  # exs ['IPTU', 'TXINC', 'COND']
  ori_refmonth: datetime.date  # in refmonth-dates day is 1 by definition

  m_plus_n: int  # when it's 1 it means 'M+1' (next month)
  """
  addon_nick: str
  # ori_refmonth: datetime.date
  mora_refmonth: datetime.date  # when in mora
  m_plus_n: int  # when it's 1 it means 'M+1' (next month)
  frequency: str  # ex 'mensal'
  this_cota: int  # for IPTU it's 1, 2, 3 ... 10
  cotas_mensais_ano: int  # for IPTU it's 10, for RENT & COND it's 12
  value_if_monthly: Dinero
  value_if_year_once: Dinero  # for IPTU or TXINC
  fix_pc_mora_intrst: float
  var_pc_mora_intrst: float
  acc_mora_ifany: Dinero  # mora is 'recalculated' by dates
  is_it_one_charge_in_year: bool = field(default=False)
  comment: str = ""
  mora_history_ifany: str = ""
  is_closed: bool = field(default=False)  # closed when payment happens
  closed_docnumber: int = None  # it's not designed yet, but it will at some moment

  @property
  def ori_refyear(self):
    try:
      return self.ori_refmonth.year
    except AttributeError:
      pass
    return None

  @property
  def ori_refmonth(self):
    try:
      return self.ori_refmonth.month
    except AttributeError:
      pass
    return None

  def __str__(self):

    outstr = f"""
    {self.addon_nick}
    {self.ori_refmonth}
    {self.mora_refmonth} 
    {self.m_plus_n}
    {self.frequency}
    {self.this_cota}
    {self.cotas_mensais_ano}
    {self.value_if_monthly}
    {self.value_if_year_once}
    {self.fix_pc_mora_intrst}
    {self.var_pc_mora_intrst}
    {self.acc_mora_ifany}
    """
    return outstr


@dataclass
class RentBiller:

  immeub_nick: str
  add_ons: list
  refmonth: datetime.date

  @property
  def asdict(self):
    return asdict(self)

  def add(self, add_on):
    self.add_ons.append(add_on)

  def __str__(self):
    outstr = f"""RentBiller object:
    {self.asdict}
    """
    return outstr


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  adhoctest() was placed in another module
  pass
  """
  process()
