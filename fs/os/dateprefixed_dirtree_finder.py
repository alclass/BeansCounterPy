#!/usr/bin/env python3
"""
fs/os/dateprefixed_dirtree_finder.py
  contains class organized the first sketches for the OS discovery class, before writing it.
"""
import datetime
import os.path
import fs.os.oshilofunctions as hilo
import models.banks.bankpropsmod as bkmd  # bkmd.BankProps


def extract_year_from_prefix_in_name(name):
  """
  For the extraction of year, year should be followed by a blank
  """
  try:
    pp = name.split(' ')
    year = int(pp[0])
    return year
  except (IndexError, TypeError, ValueError):
    pass
  return None


def extract_year_from_prefix_in_path(ppath):
  try:
    if ppath.find(os.sep) < 0:
      return extract_year_from_prefix_in_name(ppath)
    foldername = os.path.split(ppath)[-1]
    return extract_year_from_prefix_in_name(foldername)
  except (IndexError, TypeError, ValueError):
    pass
  return None


def extract_year_month_from_prefix_in_name(name):
  try:
    pp = name.split(' ')
    year = int(pp[0])
    month = int(pp[1])
    refmonthdate = datetime.date(year=year, month=month, day=1)
    return refmonthdate
  except (IndexError, TypeError, ValueError):
    pass
  return None


def extract_prefix_year_month_as_refmonth_from_path(ppath):
  try:
    if ppath.find(os.sep) < 0:
      return extract_year_month_from_prefix_in_name(ppath)
    foldername = os.path.split(ppath)[-1]
    return extract_year_month_from_prefix_in_name(foldername)
  except (IndexError, TypeError, ValueError):
    pass
  return None


class DatePrefixedOSFinder:

  def __init__(self, basefolderpath, typ=None):
    self.basefolderpath = basefolderpath
    self.typ = typ
    self.treat_typ()

  def treat_typ(self):
    if self.typ is None:
      return
    if self.typ not in bkmd.BankProps.SUBTYPERES:
      error_msg = 'Parameter Error: typ [%s] entered to DatePrefixedOSFinder is not valid.' % str(self.typ)
      raise ValueError(error_msg)

  def find_l1yyyy_folderpaths_by_typ(self, typ=None):
    """
    theses are:
    + basefolder
      + "yyyy name <typ>"
    <typ> is "intentionally used if there are more than one yyyy folder in basefolder
    Example:
    + basefolder (anyone given to __init__())
      + 2022 BB FI Ren Diá htmls
      + 2022 BB FI calc htmls
      + 2023 BB FI Ren Diá htmls
      + 2022 BB FI calc htmls
    The example above is to illustrate that substring "Ren" (a typ for the example) helps retrieve:
      + 2022 BB FI Ren Diá htmls
      + 2023 BB FI Ren Diá htmls
    ie the years for foldernames continuing as "BB FI Ren Diá htmls" ignoring those as "BB FI calc htmls"
    return: <list>
    """
    return hilo.find_folderpaths_whose_foldernames_starts_with_a_yearplusblank_via_re_in_basefolder(
      self.basefolderpath, typ
    )

  def find_all_l1yyyy_folderpaths(self):
    """
    Call find_l1yyyy_folderpaths_by_typ() without typ (ie typ being None)
    """
    return self.find_l1yyyy_folderpaths_by_typ()

  def find_l1yyyyfolderpath_by_year_typ(self, year, typ=None):
    """
    This method has the ideia of giving one sole folderpath with a year prefix and a typ/mark
    If more than one such folders exist, a ValueError exception is raised
    In the example of method above, ie
      + 2022 BB FI Ren Diá htmls
      + 2023 BB FI Ren Diá htmls
    a call like find_l1yyyyfolderpath_by_year_typ(2023, "Ren") should retrieve
      + 2023 BB FI Ren Diá htmls
    return: a folderpath or None
    """
    hilo.find_folderpath_that_starts_with_a_spec_year_via_re_in_basefolder(self.basefolderpath, year)
    paths = self.find_l1yyyy_folderpaths_by_typ(typ)
    if typ and len(paths) > 1:
      error_msg = (
          'Data Error: there are more than one folder with'
          ' mark/typ "%s" in basefolder [%s]. The intention is having only one.'
      ) % (typ, self.basefolderpath)
      raise ValueError(error_msg)
    if len(paths) == 0:
      return None
    return paths[0]

  def find_l2yyyymm_folderpaths_any_months_by_year_typ(self, year, typ=None):
    """
    theses are:
    + basefolder
      + "yyyy name <typ>"
        + "yyyy-mm name <typ>"
    return: <list>
    """
    l1folderpath = self.find_l1yyyyfolderpath_by_year_typ(year, typ)
    if l1folderpath is None or not os.path.isdir(l1folderpath):
      return []
    folderpaths = hilo.find_spec_year_typ_folderpaths_any_months_from_folderpath(l1folderpath, year, typ)
    if folderpaths is None or len(folderpaths) == 0:
      return []
    return folderpaths

  def find_l2yyyymm_folderpaths_by_year_month_typ(self, year, month, typ=None):
    """
    theses are:
    + basefolder
      + "yyyy name <typ>"
        + "yyyy-mm name <typ>"
    return: <list>
    """
    l1folderpath = self.find_l1yyyyfolderpath_by_year_typ(year, typ)
    folderpaths = hilo.find_spec_year_month_typ_folderpaths_from_folderpath(l1folderpath, year, month, typ)
    if folderpaths is None or len(folderpaths) == 0:
      return []
    return folderpaths

  def find_all_l2yyyymm_folderpaths(self):
    """
    """
    all_l1_folderpaths = self.find_all_l1yyyy_folderpaths()
    all_l2_folderpaths = []
    for l1_folderpath in all_l1_folderpaths:
      year = extract_year_from_prefix_in_path(l1_folderpath)
      if year is None:
        continue
      l2_folderpaths = self.find_l2yyyymm_folderpaths_any_months_by_year_typ(year)
      if l2_folderpaths is not None and len(l2_folderpaths) > 0:
        all_l2_folderpaths += l2_folderpaths
      else:
        continue
    return all_l2_folderpaths

  def find_l2yyyymm_filepaths_by_year_month_typ_ext(self, year, month, typ=None, dot_ext=None):
    l1yyyyfolderpath = self.find_l1yyyyfolderpath_by_year_typ(year, typ)
    if l1yyyyfolderpath is None or not os.path.isdir(l1yyyyfolderpath):
      return []
    filepaths = hilo.find_filepaths_w_year_month_ext_in_folderpath(l1yyyyfolderpath, year, month, dot_ext)
    if filepaths is None or len(filepaths) == 0:
      return []
    if self.typ:
      outfilepaths = []
      for fp in filepaths:
        filename = os.path.split(fp)[-1]
        if filename.find(self.typ) > -1:
          outfilepaths.append(fp)

  def find_l3yyyymm_filepaths_by_year_month_typ_ext(self, year, month, dot_ext=None, day=None):
    """
    Obs: typ is used for foldernames; dot_ext is used for filenames
    When the caller intents to use parameter day, it should call the next method below ie
      self.find_l3yyyymmdd_filepaths_by_year_month_day_typ_ext(self, year, month, day, dotext)
        though it is just reorders the parameter sequence signature
    """
    l2folderpaths = self.find_l2yyyymm_folderpaths_by_year_month_typ(year, month)
    if l2folderpaths is None or len(l2folderpaths) == 0:
      return []
    filepaths = []
    for folderpath in l2folderpaths:
      if day is None:
        filenames = hilo.find_filenames_w_year_month_ext_in_folderpath(folderpath, year, month, dot_ext)
      else:
        filenames = hilo.find_filenames_w_year_month_day_ext_in_folderpath(folderpath, year, month, day, dot_ext)
      if filenames is None or len(filenames) == 0:
        continue
      if self.typ is not None:
        outfilenames = []
        for filename in filenames:
          if filename.find(self.typ) > -1:
            outfilenames.append(filenames)
        filenames = outfilenames
      localfilepaths = map(lambda e: os.path.join(folderpath, e), filenames)
      filepaths += localfilepaths
    return filepaths

  def find_l3yyyymmdd_filepaths_by_year_month_day_typ_ext(self, year, month, day, typ, dotext=None):
    """
    The method is a helper-function that just reorders the parameter sequence signature for the above method:
      self.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month, typ, dotext, day)
    """
    return self.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month, dotext, day)

  def find_l3yyyymmdd_filepaths_by_refmonth_typ_ext(self, refmonthdate, typ, dotext=None):
    try:
      year = refmonthdate.year
      month = refmonthdate.month
    except TypeError:
      return []
    return self.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month, dotext)

  def find_all_l3yyyymm_filepaths(self, dot_ext=None):
    """
    returns the first element from find_l3yyyymm_filepaths_by_year_month_typ_ext(typ=None)
    """
    all_l3yyyymmdd_filepaths = []
    all_l2yyyymm_folderpaths = self.find_all_l2yyyymm_folderpaths()
    for l2yyyymm_folderpath in all_l2yyyymm_folderpaths:
      refmonthdate = extract_prefix_year_month_as_refmonth_from_path(l2yyyymm_folderpath)
      if refmonthdate is None:
        continue
      year, month = refmonthdate.year, refmonthdate.month
      l3yyyymmdd_filepaths = self.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month)
      if l3yyyymmdd_filepaths is None or len(l3yyyymmdd_filepaths) > 0:
        all_l3yyyymmdd_filepaths += l3yyyymmdd_filepaths
    return all_l3yyyymmdd_filepaths

  def __str__(self):
    outstr = 'basefolderpath = "%s"' % self.basefolderpath
    return outstr


def adhost1():
  bfp = (
    '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/001 BDB bankdata/'
    'FI Extratos Mensais Ano a Ano BB OD'
  )
  disc = DatePrefixedOSFinder(bfp)
  print(disc)
  l1folders = disc.find_l1yyyy_folderpaths_by_typ()
  for l1folder in l1folders:
    print('l1', l1folder)
  year = 2022
  l2folders = disc.find_l2yyyymm_folderpaths_any_months_by_year_typ(year)
  print('-' * 40)
  for l2folder in l2folders:
    print('l2folder', l2folder)
  if len(l2folders) == 0:
    print('no l2folders for year', year)
  month = 10
  l2files = disc.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month)
  print('-' * 40)
  for l2file in l2files:
    print('l2file', l2file)
  if len(l2files) == 0:
    print('no l2files for year', year)


def adhost2():
  """
    l1_folders = disc.find_l1yyyy_folderpaths_by_typ(year)
    print('l1', '-' * 40)
    print(year)
  """
  bfp = (
    '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
    '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/'
    'BB FI Rendimentos Diários htmls'
  )
  disc = DatePrefixedOSFinder(bfp)
  print(disc)
  l1folders = disc.find_l1yyyy_folderpaths_by_typ()
  for l1folder in l1folders:
    print('l1', l1folder)
  year = 2023
  for l2folder in l1folders:
    print('l2folder', l2folder)
  if len(l1folders) == 0:
    print('no l2folders for year', year)
  l2folders = disc.find_l2yyyymm_folderpaths_any_months_by_year_typ(year)
  print('l2', '-' * 40)
  for l2folder in l2folders:
    print('l2+folder', l2folder)
  if len(l2folders) == 0:
    print('no l2files for year', year)
  month = 10
  l3files = disc.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month)
  print('l3', '-' * 40)
  for l3file in l3files:
    print('l3file', l3file)
  if len(l3files) == 0:
    print('no l3files for year', year, 'month', month)
  ext = 'csv'
  l3files = disc.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month, dot_ext=ext)
  print('l3', ext,  '-' * 40)
  for l3file in l3files:
    print('l3file ext', ext, l3file)
  if len(l3files) == 0:
    print('no l3files for year', year, 'month', month, 'ext', ext)
  month = 11
  l3files = disc.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month, dot_ext=ext)
  print('l3', year, month, ext,  '-' * 40)
  for l3file in l3files:
    print('l3file ext', ext, l3file)
  if len(l3files) == 0:
    print('no l3files for year', year, 'month', month, 'ext', ext)


def process():
  pass


if __name__ == '__main__':
  adhost2()
