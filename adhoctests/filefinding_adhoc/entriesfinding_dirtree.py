#!/usr/bin/env python3
"""
adhoctests/filefinding_adhoc/entriesfinding_dirtree.py
"""
import inspect
import os.path
import datetime
import fs.datesetc.datehilofs as hilodt
import models.banks.bankpropsmod as bkmd  # .BankProps
import models.banks.bank_data_settings as bdsett  # bdsett.BankProps.BANKBASEFOLDERPATHS
import models.banks.banksgeneral as bkgen  # bkgen.BANK
# import fs.os.dirtree_dateprefixed2 as prfx2  # prfx.FolderNodeForDatePrefixTree
# import fs.os.oshilofunctions as hilo
import fs.os.dateprefixed_dirtree_finder as prfx
import models.banks.bb.fi.bbfi_file_find as bkfind  # bkfind.BBFIFileFinder


def get_csv_filepath():
  """
   # self._csv_filepath = self.finder.get_csv_filepath_for_date_n_type_or_raise()
    rentabdia_basefolderpath = self.dtprfxd_finder.find_or_create__l2yyyymm_folderpath_by_year_month_typ(
      self.date.year, self.date.month
  # pdate = hilodt.make_date_or_none(strdate)

  dtprfxd_finder = prfx.DatePrefixedOSFinder(basefolderpath=)
  ppath = dtprfxd_finder.find_l3yyyymm_filepath_w_typ_by_refmonth_ext(refmonth=refmonth, dot_ext='.csv')
  if ppath is None or not os.path.isfile(ppath):
    error_msg = 'CVS file is missing at [%s] ' % str(ppath)
    raise OSError(error_msg)
  self._csv_filepath = ppath

  """
  strdate = '2023-11-14'
  refmonth = hilodt.make_refmonth_or_current(strdate)
  bkf = bkfind.BBFIFileFinder(strdate)
  fp = bkf.get_csv_filepath_for_date_n_type_or_raise()
  print(fp)


def adhoctest():
  get_csv_filepath()


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
