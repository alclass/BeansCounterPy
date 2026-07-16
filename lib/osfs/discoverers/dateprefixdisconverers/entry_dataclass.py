#!/usr/bin/env python3
"""
lib/osfs/old_w_levels_dateprefixed_filefinder.py
  contains a class-sketch organizing the first ideas
  for an OS discovery class, before writing it.

import lib.osfs.datepathfindfs as pthfind
"""
import datetime
import dataclasses
import os
from pathlib import Path
import lib.osfs.discoverers.dateprefixdisconverers.regex_dateprefix_in_files as dtprfx


@dataclasses.dataclass  # (frozen=True)
class DatePrefixedEntry:
  """
  Because this class needs a __post_init__ (bootstrapping) method,
     the dataclass annotation attribute (frozen=True) cannot be used (frozen does not allow post-changes).
  """
  inpath: str | Path
  # Path is here is a 'composition'
  # basefolderpath is self.path.parent
  # name is self.path.nane
  # is_file() is self.path.is_file()
  # etc
  _year: int = None
  _month: int | None = None
  _day: int | None = None


  def bootstrap(self):
    name = self.path.name
    pdate = dtprfx.match_n_get_dateprefix_in_str(name)
    if pdate is not None:
      self._year = pdate.year
      self._month = pdate.month
      self._day = pdate.day
      return
    refmonth = dtprfx.match_n_get_refmonthprefix_in_str(name)
    if refmonth is not None:
      self._year = refmonth.year
      self._month = refmonth.month
      return
    year = dtprfx.match_n_get_yearprefix_in_str(name)
    if year is not None:
      self._year = refmonth.year
    return

  def __post_init__(self):
    self.bootstrap()

  @property
  def path(self):
    _path = Path(os.path.abspath(str(self.inpath)))
    return _path

  @property
  def date(self):
    if self._month is None or self._day is None:
      return None
    try:
      return datetime.date(self._year, self._month, self._day)
    except ValueError:
      pass
    return None

  @property
  def refmonth_as_str(self):
    if self.refmonth is not None:
      dt = self.refmonth
      str_refmonth = f"{dt.year}-{dt.month:02}"
      return str_refmonth
    return None

  @property
  def year(self):
    return self._year

  @property
  def refmonth(self):
    if self._month is None:
      return None
    try:
      return datetime.date(self._year, self._month, 1)
    except ValueError:
      pass
    return None

  @property
  def date_refmonth_or_year(self) -> datetime.date | str | int | None:
    if self.date is not None:
      return self.date
    if self.refmonth is not None:
      return self.refmonth_as_str
    if self.year is not None:
      return self.year
    return None

  def which_date_attr(self) -> str:
    if self.date is not None:
      return 'date'
    if self.refmonth is not None:
      return 'refmonth'
    if self.year is not None:
      return 'year'
    errmsg = f"Error: date_refmonth_or_year {date_refmonth_or_year} is neither a date, a refmonth nor a year."
    raise ValueError(errmsg)

  def __str__(self):
    fopath = str(self.path.parent)
    fopath = fopath if len(fopath) < 40 else '...' + fopath[-37:]
    path = f"{fopath}/{self.path.name}"
    ostr = f"prefix=[{self.date_refmonth_or_year}] file=[{path}]"
    ostr += f"\n\tis_file=[{self.path.is_file()}] which=[{self.which_date_attr()}]"
    return ostr


import art.finc.bnk.inst.bb as init
def adhoctest1():
  """
  print('The adhoctests are in its separated module.')
  """
  pass
  root = Path(init.BB_CC_EXTR_ANO_A_ANO_BASEFOLDER)
  basefolderpath = root / "2025 Extratos Mensais CC BB"
  fn = "2024-10 CC extrato BB.html"
  fipath = basefolderpath / fn
  entry = DatePrefixedEntry(inpath=fipath)
  print(entry)


def process():
  """
  """
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
