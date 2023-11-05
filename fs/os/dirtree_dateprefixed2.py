#!/usr/bin/env python3
"""
"""
import datetime
import fs.os.oshilofunctions as hilo
import settings as sett


class FolderNodeForDatePrefixTree:

  def __init__(self, rootpath):
    self.rootpath = rootpath
    self._year_ini = None
    self._year_fim = None
    self._yearmonth_ini = None
    self._yearmonth_fim = None

  @property
  def year_ini(self):
    if self._year_ini is None:
      self.init_years_ini_n_fim()
    return self._year_ini

  def init_years_ini_n_fim(self):
    foldernames = self.find_foldernames_that_starts_with_a_yearplusblank()
    year_ini = 99999
    year_fim = -99999
    for foldername in foldernames:
      year = hilo.extract_year_from_yearprefix_str(foldername)
      if year < year_ini:
        year_ini = year
      if year > year_fim:
        year_fim = year
    self._year_ini = year_ini
    self._year_fim = year_fim

  def find_foldernames_that_starts_with_a_yearplusblank(self):
    foldernames = hilo.find_foldernames_that_starts_with_a_yearplusblank_via_re_in_basefolder(self.rootpath)
    if foldernames is None or len(foldernames) == 0:
      return []
    return foldernames

  def find_1stlevel_yearprefix_folderpaths(self):
    return hilo.find_folderpaths_whose_foldernames_starts_with_a_yearplusblank_via_re_in_basefolder(self.rootpath)

  def find_1stlevel_yearprefix_folderpath_for(self, year):
    """
    If not found, it returns None
    If more than one folder are found, a ValueError exception is raised from the calling function
      (This should be considered an inconsistent data directory and it's ok for the exception to be raised.)
    """
    return hilo.find_foldername_that_starts_with_a_spec_year_via_re_in_basefolder(self.rootpath, year)

  def find_1stlevel_yearfolderpath_for(self, year):
    return hilo.find_folderpath_that_starts_with_a_spec_year_via_re_in_basefolder(self.rootpath, year)

  def find_2ndlevel_yearmonth_folderpath_for(self, year, month):
    refmonthdate = datetime.date(year=year, month=month, day=1)
    yearfolderpath = self.find_1stlevel_yearfolderpath_for(year)
    return hilo.find_yearmonthfolderpath_from(yearfolderpath, refmonthdate)

  def get_filepaths_by_year_month(self, year, month):
    refmonthdate = datetime.date(year=year, month=month, day=1)
    yearfolderpath = self.find_1stlevel_yearfolderpath_for(year)
    # attention here with the order of parameters: first is refmonthdate then yearfolderpath
    return hilo.find_filepaths_w_year_month_ext_in_folderpath(refmonthdate, yearfolderpath)


def adhoctest():
  pass


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
