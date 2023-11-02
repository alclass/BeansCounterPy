#!/usr/bin/env python3
"""
models/banks/bankpathfinder.py
"""
import datetime
import inspect
import models.banks.bank_data_settings as bdsett  # bdsett.BankProps.BANKBASEFOLDERPATHS
import models.banks.banksgeneral as bkgen  # bkgen.BANK
import fs.os.dirtree_dateprefixed as prfx  # prfx.FolderNodeForDatePrefixTree
import fs.os.oshilofunctions as hilo


class BankOSFolderFileFinder:

  ACCOUNT_KEY = 'ac'
  FI_FUNDOS_KEY = 'fi'
  REND_RESULTS_KEY = 're'
  TYPECATS = [ACCOUNT_KEY, FI_FUNDOS_KEY, REND_RESULTS_KEY]

  def __init__(self, bank3letter, typecat=None):
    self.bank3letter = bank3letter
    self.banknumber = bkgen.BANK.get_banknumber_by_its3letter(self.bank3letter)
    self._basefolderpath = None
    self._typecat = typecat
    _ = self.typecat

  @property
  def basefolderpath(self):
    if self._typecat is None:
      return None
    if self._basefolderpath is None:
      self.set_rootfolderpath()
    return self._basefolderpath

  @property
  def typecat(self):
    if self._typecat in self.TYPECATS:
      return self._typecat
    if self._typecat is None:
      # default
      self._typecat = self.REND_RESULTS_KEY
      self.set_rootfolderpath()
    return self._typecat

  def set_rootfolderpath(self):
    if self.typecat == self.ACCOUNT_KEY:
      self._basefolderpath = bdsett.BankProps.BANKBASEFOLDERPATHS[self.banknumber][self.ACCOUNT_KEY]
    if self.typecat == self.FI_FUNDOS_KEY:
      self._basefolderpath = bdsett.BankProps.BANKBASEFOLDERPATHS[self.banknumber][self.FI_FUNDOS_KEY]
    if self.typecat == self.REND_RESULTS_KEY:
      self._basefolderpath = bdsett.BankProps.BANKBASEFOLDERPATHS[self.banknumber][self.REND_RESULTS_KEY]

  def get_folderpath_by_year(self, year):
    if self.typecat is None:
      return None
    prefixdirtree = prfx.FolderNodeForDatePrefixTree(self.basefolderpath)
    return prefixdirtree.find_1stlevel_yearfolderpath_for(year)

  def get_folderpath_by_yearmonth(self, year, month):
    if self.typecat is None:
      return None
    prefixdirtree = prfx.FolderNodeForDatePrefixTree(self.basefolderpath)
    return prefixdirtree.find_2ndlevel_yearmonth_folderpath_for(year, month)

  def get_filepaths_by_year_month(self, year, month):
    yearmonth_folderpath = self.get_folderpath_by_yearmonth(year, month)
    refmonthdate = datetime.date(year=year, month=month, day=1)
    filepaths_by_year_month = hilo.find_filepaths_whose_filenames_start_with_spec_yearmonth_in_folderpath(
        refmonthdate,
        yearmonth_folderpath
    )
    return filepaths_by_year_month

  def get_filepaths_by_year_month_n_ext(self, year, month, dotext=None):
    if dotext is None:
      return self.get_filepaths_by_year_month(year, month)
    yearmonth_folderpath = self.get_folderpath_by_yearmonth(year, month)
    refmonthdate = datetime.date(year=year, month=month, day=1)
    filepaths_by_year_month = hilo.find_filepaths_whose_filenames_start_with_spec_yearmonth_in_folderpath(
        refmonthdate,
        yearmonth_folderpath
    )
    if not dotext.startswith('.'):
      dotext = '.' + dotext
    return sorted(filter(lambda e: e.endswith(dotext), filepaths_by_year_month))

  def year_range_for(self, datacat=None):
    pass

  def outdict(self):
    """
    for attr in self.__dict__:
      if not callable(attr) and attr.startswith('_'):
        pattr = attr.lstrip('_')
        attrs.append(pattr)
     lambda e: not callable(e) and e.startswith('_') and not e.startswith('__')
    """
    _outdict = {}
    attrs = inspect.getmembers(self,)
    # form dict
    for keyvaluetuple in attrs:
      fieldname = keyvaluetuple[0]
      if callable(fieldname):
        continue
      if fieldname.startswith('__'):
        continue
      if not fieldname.startswith('_'):
        continue
      private_attr = fieldname
      public_attr = private_attr[1:]  # lstrip the _
      value = eval('self.' + public_attr)
      _outdict[public_attr] = value
    return _outdict

  def __str__(self):
    """
    self._ac_basefolderpath
    self._fi_basefolderpath
    self._re_basefolderpath
    """
    outstr = "BankPath Class\n"
    pdict = self.outdict()
    for fieldname in pdict:
      value = pdict[fieldname]
      outstr += "\t {fieldname} = '{value}'\n".format(fieldname=fieldname, value=value)
    return outstr


class BankCat:
  ACCOUNT_KEY = BankOSFolderFileFinder.ACCOUNT_KEY
  FI_FUNDOS_KEY = BankOSFolderFileFinder.FI_FUNDOS_KEY
  REND_RESULTS_KEY = BankOSFolderFileFinder.REND_RESULTS_KEY
  TYPECATS = [ACCOUNT_KEY, FI_FUNDOS_KEY, REND_RESULTS_KEY]


def adhoctest():
  bfinder = BankOSFolderFileFinder('bdb', BankCat.REND_RESULTS_KEY)
  print(bfinder)
  print(bfinder.basefolderpath)
  year = 2023
  print('Find folderpath for year', year)
  print(bfinder.get_folderpath_by_year(year))
  month = 10
  print('get_folderpath_by_yearmonth', year, 'month', month)
  print(bfinder.get_folderpath_by_yearmonth(year, month))
  print('Find filepaths for year', year, 'month', month)
  fpaths = bfinder.get_filepaths_by_year_month(year, month)
  for fpath in fpaths:
    print(fpath)
  fpaths = bfinder.get_filepaths_by_year_month_n_ext(year, month, 'csv')
  for fpath in fpaths:
    print(fpath)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
