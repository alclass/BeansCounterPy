#!/usr/bin/env python3
"""
models/banks/bankpathfinder.py
"""
import inspect
import os.path
import fs.datesetc.datehilofs as hilodt
import models.banks.bankpropsmod as bkmd  # .BankProps

import models.banks.bank_data_settings as bdsett  # bdsett.BankProps.BANKBASEFOLDERPATHS
import models.banks.banksgeneral as bkgen  # bkgen.BANK
# import fs.os.dirtree_dateprefixed2 as prfx2  # prfx.FolderNodeForDatePrefixTree
# import fs.os.oshilofunctions as hilo
import fs.os.dateprefixed_dirtree_finder as prfx


class BankOSFolderFileFinder:

  ACCOUNT_KEY = bkmd.BankProps.FI_FUNDOS_KEY
  FI_FUNDOS_KEY = bkmd.BankProps.FI_FUNDOS_KEY
  REND_RESULTS_KEY = bkmd.BankProps.REND_RESULTS_KEY
  TYPECATS = bkmd.BankProps.TYPECATS
  FILESUFFIXDICT = bkmd.BankProps.FILESUFFIXDICT
  FOLDERSUFFIXDICT = bkmd.BankProps.FOLDERSUFFIXDICT
  ACOES = bkmd.BankProps.ACOES
  RFDI = bkmd.BankProps.RFDI
  RFLP = bkmd.BankProps.RFLP
  SUBTYPERES = bkmd.BankProps.SUBTYPERES

  def __init__(self, bank3letter, typecat=None, reporttype=None):
    self.bank3letter = bank3letter
    self.banknumber = bkgen.BANK.get_banknumber_by_its3letter(self.bank3letter)
    self._basefolderpath = None
    self._typecat = typecat
    _ = self.typecat
    self.reporttype = reporttype
    self.treat_reporttype()
    self.prxfinder = prfx.DatePrefixedOSFinder(self.basefolderpath, self.reporttype)

  def treat_reporttype(self):
    if self.reporttype is not self.SUBTYPERES:
      self.reporttype = self.RFLP

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

  def create_l1_folder(self, year):
    sufix = self.FOLDERSUFFIXDICT[self.typecat]
    l1folderpath = 'to-find-out'
    try:
      l1foldername = str(year) + ' ' + sufix
      l1folderpath = os.path.join(self.basefolderpath, l1foldername)
      if os.path.isdir(l1folderpath):
        os.makedirs(l1folderpath)
      return l1folderpath
    except (TypeError, ValueError):
      print('Could not create folder', l1folderpath)
    return None

  def create_l2_folder(self, year, month=None):
    sufix = self.FOLDERSUFFIXDICT[self.typecat]
    l2folderpath = 'to-find-out'
    try:
      l2foldername = str(year) + '-' + str(month).zfill(2) + ' ' + sufix
      l1basefolderpath = self.find_l1yyyyfolderpath_by_year_opt_substr(year)
      l2folderpath = os.path.join(l1basefolderpath, l2foldername)
      if os.path.isdir(l2folderpath):
        os.makedirs(l2folderpath)
      return l2folderpath
    except (TypeError, ValueError):
      print('Could not create folder', l2folderpath)
    return None

  def form_l3_filename_w_year_month_day_ext(self, year, month, day=None, subtypre=None, dot_ext=None):
    """
    Example:
      "2023-10-10 RFDI BB rendimentos no dia.csv" is built with the following:
        year = 2023, month = 10, day = 10, subtypre = self.RFDI, sufix = "BB rendimentos no dia", dot_ext = '.csv'
    """
    sufix = self.FILESUFFIXDICT[self.typecat]
    if self.typecat == self.REND_RESULTS_KEY:
      if subtypre is None:
        subtypre = self.ACOES
      sufix = subtypre + ' ' + sufix
    dateprefix = '{year}-{month:02}'.format(year=year, month=month)
    if day is not None:
      dateprefix = dateprefix + str(day).zfill(2)
    if dot_ext is None:
      dot_ext = '.html'  # default with being a constant above
    if not dot_ext.startswith('.'):
      dot_ext = '.' + dot_ext
    filename = dateprefix + ' ' + sufix + dot_ext
    return filename

  def form_l2_filename_w_year_month_ext(self, year, month, dot_ext=None):
    """
    Example:
      "2023-07 FI extrato BB.txt" is built with the following:
        year = 2023, month = 7, sufix = "FI extrato BB", dot_ext = '.txt'
    """
    sufix = self.FILESUFFIXDICT[self.typecat]
    if self.typecat == self.REND_RESULTS_KEY:
      error_msg = 'Consistency Error: type ' + self.typecat + ' does not have l2 filenames.'
      raise ValueError(error_msg)
    dateprefix = '{year}-{month:02}'.format(year=year, month=month)
    if dot_ext is None:
      dot_ext = '.txt'  # default with being a constant above
    if not dot_ext.startswith('.'):
      dot_ext = '.' + dot_ext
    filename = dateprefix + ' ' + sufix + dot_ext
    return filename

  def find_l1yyyyfolderpath_by_year_opt_substr(self, year, substr=None):
    if self.typecat is None:
      return None
    l1yearfolderpaths = self.prxfinder.find_l1yyyyfolderpath_by_year_n_opt_substr(year, substr)
    if l1yearfolderpaths and len(l1yearfolderpaths) == 1:
      return l1yearfolderpaths[0]
    return None

  def find_l2yyyymm_folderpath_by_year_month_typ(self, year, month, typ=None):
    if self.typecat is None:
      return None
    l2yearmonthfolderpaths = self.prxfinder.find_l2yyyymm_folderpaths_by_year_month_opt_substr(year, month, typ)
    if l2yearmonthfolderpaths and len(l2yearmonthfolderpaths) == 1:
      return l2yearmonthfolderpaths[0]
    return None

  def find_or_create_l2yyyymm_folderpath_by_year_month_typ(self, year, month, typ=None):
    l2yearmonthfolderpath = self.find_l2yyyymm_folderpath_by_year_month_typ(year, month, typ)
    if l2yearmonthfolderpath is None:
      # (to think about) typ is not used here, maybe an exception should be raised if typ is not None
      l2yearmonthfolderpath = self.create_l2_folder(year, month)
    return l2yearmonthfolderpath

  def find_l3yyyymm_filepaths_by_year_month_ext(self, year, month, dot_ext=None):
    l3yearmonthfolderpaths = self.prxfinder.find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(year, month,
                                                                                                     dot_ext=dot_ext)
    return l3yearmonthfolderpaths

  def find_l3yyyymm_filepaths_by_refmonth_ext(self, refmonth, dot_ext):
    try:
      year = refmonth.year
      month = refmonth.month
      return self.find_l3yyyymm_filepaths_by_year_month_ext(year, month, dot_ext=dot_ext)
    except (AttributeError, TypeError):
      pass
    return []

  def find_l3yyyymmdd_filepath_w_year_month_day_opt_ext_substr(self, year, month, day, dot_ext=None, substr=None):
    try:
      year = int(year)
      month = int(month)
      day = int(day)
    except (TypeError, ValueError):
      return None
    if dot_ext is None:
      dot_ext = '.csv'
    if not dot_ext.startswith('.'):
      dot_ext = '.' + dot_ext
    ppaths = self.prxfinder.find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(
      year, month, day, dot_ext, substr
    )
    if ppaths and len(ppaths) == 1:
      l3yyyymmddfilepath = ppaths[0]
      return l3yyyymmddfilepath
    return None

  def find_l3yyyymm_filepath_w_typ_by_refmonth_ext(self, refmonth, dot_ext=None):
    if dot_ext is None:
      dot_ext = '.csv'
    if not dot_ext.startswith('.'):
      dot_ext = '.' + dot_ext
    if refmonth is None:
      refmonth = hilodt.make_refmonth_or_current(refmonth)
    ppaths = self.find_l3yyyymm_filepaths_by_refmonth_ext(refmonth, dot_ext)
    for ppath in ppaths:
      _, fn = os.path.split(ppath)
      if fn.find(self.typecat) > -1:
        return ppath
    return None

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
  print(bfinder.find_l1yyyyfolderpath_by_year_opt_substr(year))
  month = 10
  print('find_l2yyyymm_folderpath_by_year_month_typ', year, 'month', month)
  print(bfinder.find_l2yyyymm_folderpath_by_year_month_typ(year, month))
  print('Find filepaths for year', year, 'month', month)
  fpaths = bfinder.find_l3yyyymm_filepaths_by_year_month_ext(year, month)
  for fpath in fpaths:
    print(fpath)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
