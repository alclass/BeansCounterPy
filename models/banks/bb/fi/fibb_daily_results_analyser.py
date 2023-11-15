#!/usr/bin/env python3
"""
commands/download/fibb_daily_results_numbers_comma_to_point_convert.py

"""
import datetime
import os.path
import fs.datesetc.datehilofs as hilodt
import models.banks.bb.fi.bbfi_file_find as ffnd  # ffnd.BBFIFileFinder
import models.banks.bankpathfinder as bkfnd  # .BankOSFolderFileFinder
import pandas as pd
pd.set_option('display.max_columns', None)
BDB_BANK3LETTER = 'bdb'
ReportProps = ffnd.ReportProps


class ResultAnalyser:

  def __init__(self, pdate=None, typ=None):
    self.date = hilodt.try_make_date_with(pdate) or datetime.date.today()
    self.typ = typ
    self.treat_typ()
    self.finder = ffnd.BBFIFileFinder(self.date, self.typ)
    self.dtprfxd_finder = bkfnd.BankOSFolderFileFinder(BDB_BANK3LETTER, bkfnd.BankCat.REND_RESULTS_KEY, self.typ)
    self._csv_filepath = None

  def treat_typ(self):
    if self.typ not in ffnd.ReportProps.RESTYPES:
      self.typ = ffnd.ReportProps.RFDI

  @property
  def csv_filepath(self):
    """
     # self._csv_filepath = self.finder.get_csv_filepath_for_date_n_type_or_raise()
      rentabdia_basefolderpath = self.dtprfxd_finder.find_l2yyyymm_folderpath_by_year_month_typ(
        self.date.year, self.date.month
    """
    refmonth = datetime.date(self.date.year, self.date.month, 1)
    if self._csv_filepath is not None:
      return self._csv_filepath
    ppath = self.dtprfxd_finder.find_l3yyyymm_filepath_w_typ_by_refmonth_ext(refmonth=refmonth, dot_ext='.csv')
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
      1: 'name', 2: 'onday', 3: 'accmonth',4: 'lastmonth', 5: 'inyear', 6: 'in12m', 7: 'in24m', 8: 'in36m'
    }, inplace=True)
    print('='*40)
    print(df.to_string())
    print('='*40)
    df = df.sort_values("onday", ascending=True)
    print('sorting', '='*40)
    print(df.to_string())
    # se1 = df[['name', 'onday']]
    # print(se1)


def adhoctests():
  typ = ffnd.BBFIFileFinder.Props.RFLP
  pdate = '2023-11-13'
  analyser = ResultAnalyser(pdate, typ)
  analyser.read_df()


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctests()
