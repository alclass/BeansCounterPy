#!/usr/bin/env python3
"""
lib/osfs/discoverers/dateprefixdisconverers/dateprefix_filefind.py
  Contains monthly and refmonthly date functions.

"""
from dataclasses import dataclass
import datetime
import lib.datesetc.datefs as dtfs  # dtprx.
import lib.datesetc.refmonth_fs as rmfs  # dtprx.
import lib.osfs.discoverers.dateprefixdisconverers.regex_dateprefix_in_files as dtprx  # dtprx.
import lib.osfs.filefolder_retriever_fs as ffretr  # ffretr.gather_all_files_up_from


class DatePrefixedOSFinder:
  """
  In this version, this finder class reads all files from a rootfolder.
  Then, it calls a bootstrap() method that fills in 3 dicts:
    one for year-prefixed files
    one for refmonth-prefixed files
    one for date-prefixed files
  So, to search one of these 3 'dates' (year, refmonth, or 'daydate'), suffice to get the dict by key.
  """

  def __init__(self, rootdir):
    self.rootdir = rootdir
    # self.datadict = {}
    # self.datefilesdict = {}
    self.datesfileszip = []
    # self.refmonthfilesdict = {}
    self.refmonthsfileszip = []
    # self.yearfilesdict = {}
    self.yearsfileszip = []
    self.n_allfiles = None
    self.bootstrap()

  def bootstrap(self):
    remainingfiles = ffretr.gather_all_files_up_from(self.rootdir)
    self.n_allfiles = len(remainingfiles)
    # 1 yearprefix first
    years = map(lambda f: dtprx.match_n_get_yearprefix_in_str(f.name), remainingfiles)
    # years = list(years)
    # 'zipped' needs to 'survive' after the first filter() for the following list-comprehension
    zipped = list(zip(years, remainingfiles))
    # self.yearfilesdict = {key: fp for key, fp in zipped if key is not None}
    self.yearsfileszip = filter(lambda tupl: tupl[0] is not None, zipped)
    # executing list(filter()) now because zipped will 'disapper' later on
    self.yearsfileszip = list(self.yearsfileszip)
    # 'diminish' remainingfiles if anything was 'taken' above
    remainingfiles = [z[1] for z in zipped if z[0] is None]
    # 2 refmonthprefix next
    refmonths = map(lambda f: dtprx.match_n_get_refmonthprefix_in_str(f.name), remainingfiles)
    refmonths = list(refmonths)
    # 'zipped' needs to 'survive' after the first filter() for the following list-comprehension
    zipped = list(zip(refmonths, remainingfiles))
    # self.refmonthfilesdict = {key: fp for key, fp in zipped if key is not None}
    self.refmonthsfileszip = filter(lambda tupl: tupl[0] is not None, zipped)
    # executing list(filter()) now because zipped will 'disapper' later on
    self.refmonthsfileszip = list(self.refmonthsfileszip)
    # diminish files
    remainingfiles = [z[1] for z in zipped if z[0] is None]
    # 3 dateprefix next
    dates = map(lambda f: dtprx.match_n_get_dateprefix_in_str(f.name), remainingfiles)
    # 'zipped' needs to 'survive' after the first filter() for the following list-comprehension
    zipped = list(zip(dates, remainingfiles))
    # self.datefilesdict = {key: fp for key, fp in zipped if key is not None}
    self.datesfileszip = filter(lambda tupl: tupl[0] is not None, zipped)
    # executing list(filter()) now because zipped will 'disapper' later on
    self.datesfileszip = list(self.datesfileszip)

  @property
  def yearlist(self):
    return [tupl[0] for tupl in self.yearsfileszip]

  @property
  def n_uniq_years(self):
    return len(set(self.yearlist))

  @property
  def refmonthlist(self):
    return [tupl[0] for tupl in self.refmonthsfileszip]

  @property
  def n_uniq_refmonths(self):
    return len(set(self.refmonthlist))

  @property
  def dates(self):
    if self.datesfileszip is None or len(self.datesfileszip) == 0:
      return []
    dates = [tupl[0] for tupl in self.datesfileszip]
    return sorted(dates)

  @property
  def n_uniq_dates(self):
    return len(set(self.dates))

  @property
  def uniq_dates_as_str(self):
    """
    reduce(dates, " | ")
    dates = map(str, self.dates)
    ostr = "|".join(dates)  # lambda date: date.strftime("%y%m%d"), dates)
    """
    dates = sorted(list(set(self.dates)))
    ostr = "|".join(map(str, dates))  # lambda date: date.strftime("%y%m%d"), dates)
    return ostr

  @property
  def uniq_years_as_str(self):
    """
    reduce(dates, " | ")
    dates = map(str, self.dates)
    ostr = "|".join(dates)  # lambda date: date.strftime("%y%m%d"), dates)
    """
    years = sorted(list(set(self.yearlist)))
    ostr = "|".join(map(str, years))  # lambda date: date.strftime("%y%m%d"), dates)
    return ostr

  @property
  def uniq_refmonths_as_str(self):
    """
    reduce(dates, " | ")
    dates = map(str, self.dates)
    ostr = "|".join(dates)  # lambda date: date.strftime("%y%m%d"), dates)
    """
    refmonths = sorted(list(set(self.refmonthlist)))
    ostr = "|".join(map(lambda r: f"{r.year}-{r.month:02}", refmonths))  # lambda date: date.strftime("%y%m%d"), dates)
    return ostr

  def get_files_on_refmonth(self, pdate: datetime.date | str):
    pdate = rmfs.make_refmonth_or_none(pdate)
    outlist = []
    try:
      outlist = [tupl[1] for tupl in self.refmonthsfileszip if tupl[0] == pdate]
    except KeyError:
      pass
    return outlist

  def get_files_on_date(self, pdate: datetime.date | str):
    pdate = dtfs.make_date_or_none(pdate)
    outlist = []
    try:
      outlist = [tupl[1] for tupl in self.datesfileszip if tupl[0] == pdate]
    except KeyError:
      pass
    return outlist

  def __str__(self):
    ostr = f"""rootdir={self.rootdir}
    n_allfiles={self.n_allfiles}
    n files in yearszip = {len(self.yearsfileszip)}
    n files in refmonthszip = {len(self.refmonthsfileszip)}
    n files in dateszip = {len(self.datesfileszip)}
    uniq years ({self.n_uniq_years}) = {self.uniq_years_as_str}
    uniq dates ({self.n_uniq_dates}) = {self.uniq_dates_as_str}
    uniq refmonths ({self.n_uniq_refmonths}) = {self.uniq_refmonths_as_str}
    """
    return ostr


@dataclass
class MidPath:

  midpath: str
  only_year: int | None = None
  year_n_month: str | None = None
  pdate: datetime.date | None = None
  contains_prxfiles: bool = False

  def midpath(self):
    return self.midpath


import art.finc.bnk.inst.bb as bbinit
def adhoctest1():
  """
  print('The adhoctests are in its separated module.')
  """
  rootdir = bbinit.BB_CC_EXTR_ANO_A_ANO_BASEFOLDER
  finder = DatePrefixedOSFinder(rootdir=rootdir)
  print(finder)
  strdate = '2022-07-07'
  files = finder.get_files_on_date(strdate)
  scrmsg = f"finder.get_files_on_date('{strdate}')"
  print(scrmsg)
  for i, fp in enumerate(files):
    print(i+1, '->', fp)
  refmonth = '2022-07'
  files = finder.get_files_on_refmonth(refmonth)
  scrmsg = f"finder.get_files_on_refmonth('{refmonth}')"
  print(scrmsg)
  for i, fp in enumerate(files):
    print(i+1, '->', fp)


def process():
  """
  This module contains library functions
  """
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
