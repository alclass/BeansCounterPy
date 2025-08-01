#!/usr/bin/env python3
"""
models/banks/bb/fi/analyser_monthly_results_fibb_.py
  reads the last daily result file available for a month and tries to aggregate,
  if there are data available, on a monthly basis (instead of on a daily basis)
"""
import datetime
import os.path
import lib.datesetc.datehilofs as hilodt
import models.banks.bb.fi.bbfi_file_find as ffnd  # ffnd.BBFIFileFinder
import models.banks.bankpathfinder as bkfnd  # .BankOSFolderFileFinder
import lib.os.dateprefixed_dirtree_finder as dtprxdt  # dtprxdt.DatePrefixedOSFinder
import pandas as pd
pd.set_option('display.max_columns', None)
BDB_BANK3LETTER = 'bdb'
ReportProps = ffnd.ReportProps


class ResultAnalyser:

  def __init__(self, pdate=None, reporttype=None):
    self.date = hilodt.make_date_or_none(pdate) or datetime.date.today()
    self.reporttype = reporttype
    self.treat_reporttype()
    self.finder = ffnd.BBFIFileFinder(self.date, self.reporttype)
    self.dtprfxd_finder = bkfnd.BankOSFolderFileFinder(
      BDB_BANK3LETTER,
      bkfnd.BankCat.REND_RESULTS_KEY,
      self.reporttype
    )
    self._csv_filepath = None

  def treat_reporttype(self):
    if self.reporttype not in ffnd.ReportProps.RESTYPES:
      self.reporttype = ffnd.ReportProps.RFDI

  @property
  def csv_filepath(self):
    """
     # self._csv_filepath = self.finder.get_csv_filepath_for_date_n_type_or_raise()
      rentabdia_basefolderpath = self.dtprfxd_finder.find_or_create__l2yyyymm_folderpath_by_year_month_typ(
        self.date.year, self.date.month
    """
    if self._csv_filepath is not None:
      return self._csv_filepath
    dot_ext = '.csv'
    substr = self.reporttype  # it's sent from here (to avoid a bug that's probably in dtprfxd_finder)
    ppath = self.dtprfxd_finder.find_l3yyyymmdd_filepath_w_year_month_day_opt_ext_substr(
      self.date.year, self.date.month, self.date.day, dot_ext, substr
    )
    if ppath is None or not os.path.isfile(ppath):
      error_msg = 'CVS file is missing at [%s] ' % str(ppath)
      raise OSError(error_msg)
    self._csv_filepath = ppath
    return self._csv_filepath

  def read_df(self):
    """
    print('head =>', df.head())
    print('columns =>', df .columns)
    """
    print('pd.DataFrame(self.csv_filepath)', self.csv_filepath)
    df = pd.read_csv(self.csv_filepath)
    col_dim = df.shape[1]
    col_int_idx_list = list(range(col_dim))
    df.columns = col_int_idx_list
    col_n_to_del_from = 9
    dropindexlist = [0] + list(range(col_n_to_del_from, col_dim))
    df = df.drop(dropindexlist, axis=1)  # , inplace=True
    print('dropindexlist', dropindexlist)
    print('df.index', df.index)
    print('df.columns', df.columns)
    df.rename(columns={
      1: 'name', 2: 'onday', 3: 'accmonth', 4: 'lastmonth', 5: 'inyear', 6: 'in12m', 7: 'in24m', 8: 'in36m'
    }, inplace=True)
    print('='*40)
    print(df.to_string())
    print('='*40)
    df = df.sort_values("onday", ascending=True)
    print('sorting', '='*40)
    print(df.to_string())
    # se1 = df[['name', 'onday']]
    # print(se1)


def show_stats_per_date(pdate):
  reporttype = ffnd.BBFIFileFinder.Props.RFDI
  # testing ResultAnalyser with its init's parameters
  analyser = ResultAnalyser(pdate, reporttype)
  analyser.read_df()
  # testing get_csv_file
  bkfinder = ffnd.BBFIFileFinder(pdate, reporttype)
  filepath = bkfinder.get_csv_filepath_for_date_n_type_or_raise()
  filename = os.path.split(filepath)[-1]
  print('with finder => filename', filename)
  print(filepath)


def traverse_dates():
  """

  """
  today = datetime.date.today()
  bkfinder = ffnd.BBFIFileFinder(today)
  basefolderpath = bkfinder.get_basefolder_for_daily_results()
  prxdirtree = dtprxdt.DatePrefixedOSFinder(basefolderpath)
  refmonthdates = prxdirtree.find_all_refmonths_l2yyyymmfolder_by_year_opt_substr(year=2023)
  for i, refmonthdate in enumerate(refmonthdates):
    fp = prxdirtree.find_last_l2_or_l3_filepath_by_refmonth_opt_ext_substr(refmonthdate)
    print(i+1, 'refmonth', refmonthdate, 'filepath', fp)
    # show_stats_per_date(pdate)


def adhoctest():
  pass


def process():
  traverse_dates()


if __name__ == '__main__':
  """
  pass
  """
  process()
