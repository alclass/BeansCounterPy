#!/usr/bin/env python3
"""
fs/os/dateprefixed_dirtree_finder.py
  contains class organized the first sketches for the OS discovery class, before writing it.
"""
import datetime
import os.path
import fs.os.oshilofunctions as hilo


class DatePrefixedOSFinder:

  def __init__(self, basefolderpath, substr=None):
    self.basefolderpath = basefolderpath
    self.substr = substr
    self.treat_substr()

  def treat_substr(self):
    if self.substr is None:
      return
    try:
      self.substr = str(self.substr)
    except ValueError:
      error_msg = ('Parameter Error for DatePrefixedOSFinder: substr [%s] is not convertable to a string.'
                   % str(self.substr))
      raise ValueError(error_msg)

  def gen_dates_from_all_l3yyyymmdd_files(self):
    previous_date = None
    for filename in self.find_all_l3yyyymm_filenames():
      try:
        pp = filename.split(' ')[0]
        strdate = pp.split('-')
        year = int(strdate[0])
        month = int(strdate[1])
        day = int(strdate[2])
        pdate = datetime.date(year, month, day)
        if pdate == previous_date:
          continue
        previous_date = pdate
        yield pdate
      except (IndexError, TypeError, ValueError):
        pass
    return  # ends of generation

  def find_l1yyyy_folderpaths_w_opt_substr(self, substr=None):
    """
    theses are:
    + basefolder
      + "yyyy name <substr>"
    <substr> may be "intentionally used if there are more than one yyyy folder in basefolder
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
    return hilo.find_l1folderpaths_all_years_from_basefolder_opt_substr(
      self.basefolderpath, substr
    )

  def find_all_l1yyyy_folderpaths(self):
    """
    Call find_l1yyyy_folderpaths_w_opt_substr() without substr (ie its being None)
    """
    return self.find_l1yyyy_folderpaths_w_opt_substr()

  def find_l1yyyyfolderpaths_by_year_n_opt_substr(self, year, substr=None):
    return hilo.find_l1yyyyfolderpaths_from_basefolder_w_year_opt_substr(self.basefolderpath, year, substr)

  def find_l1yyyyfolderpath_by_year_n_opt_substr(self, year, substr=None):
    """
    This method has the ideia of giving one sole folderpath with a year prefix and a typ/mark
    If more than one such folders exist, a ValueError exception is raised
    In the example of method above, ie
      + 2022 BB FI Ren Diá htmls
      + 2023 BB FI Ren Diá htmls
    a call like find_l1yyyyfolderpath_by_year_n_opt_substr(2023, "Ren") should retrieve
      + 2023 BB FI Ren Diá htmls
    return: a folderpath or None
    """
    paths = self.find_l1yyyyfolderpaths_by_year_n_opt_substr(year, substr)
    if len(paths) == 0:
      return None
    if len(paths) > 1:
      error_msg = (
          'Data Logical Error: there are more than one folder with'
          ' substr "%s" in basefolder [%s]. This method understands there should be only one.'
      ) % (str(substr), self.basefolderpath)
      raise ValueError(error_msg)
    l1yyyyfolderpath = paths[0]
    return l1yyyyfolderpath

  def find_l2yyyymm_folderpaths_any_months_by_year_opt_substr(self, year, substr=None):
    """
    theses are:
    + basefolder
      + "yyyy name <typ>"
        + "yyyy-mm name <typ>"
    return: <list>
    """
    l1yearfolderpath = self.find_l1yyyyfolderpath_by_year_n_opt_substr(year, substr)
    l2yyyyfolderpaths = hilo.find_l2yyyyfolderpaths_any_months_from_folderpath_w_year_opt_substr(
      l1yearfolderpath, year, substr)
    return l2yyyyfolderpaths

  def find_all_refmonths_l2yyyymmfolder_by_year_opt_substr(self, year, substr=None):
    l2yyyyfolderpaths = self.find_l2yyyymm_folderpaths_any_months_by_year_opt_substr(year, substr)
    refmonthdates = []
    for l2yyyyfolderpath in l2yyyyfolderpaths:
      foldername = os.path.split(l2yyyyfolderpath)[-1]
      refmonthdate = hilo.derive_refmonthdate_from_a_yearmonthprefixedstr_or_mostrecent(foldername)
      refmonthdates.append(refmonthdate)
    return refmonthdates

  def find_l2yyyymm_folderpaths_by_year_month_opt_substr(self, year, month, substr=None):
    """
    theses are:
    + basefolder
      + "yyyy name <typ>"
        + "yyyy-mm name <typ>"
    return: <list>
    """
    l1yyyyfolderpath = self.find_l1yyyyfolderpath_by_year_n_opt_substr(year, substr)
    folderpaths = hilo.find_l2yyyymmfolderpaths_from_folderpath_w_year_month_opt_substr(
      l1yyyyfolderpath, year, month, substr
    )
    if folderpaths is None or len(folderpaths) == 0:
      return []
    return folderpaths

  def find_all_l2yyyymm_folderpaths(self):
    """
    """
    all_l1_folderpaths = self.find_all_l1yyyy_folderpaths()
    all_l2_folderpaths = []
    for l1_folderpath in all_l1_folderpaths:
      year = hilo.extract_year_from_prefix_in_path(l1_folderpath)
      if year is None:
        continue
      l2_folderpaths = self.find_l2yyyymm_folderpaths_any_months_by_year_opt_substr(year)
      if l2_folderpaths is not None and len(l2_folderpaths) > 0:
        all_l2_folderpaths += l2_folderpaths
      else:
        continue
    return all_l2_folderpaths

  def find_l2yyyymm_filepaths_by_year_month_typ_ext(self, year, month, typ=None, dot_ext=None):
    l1yyyyfolderpath = self.find_l1yyyyfolderpath_by_year_n_opt_substr(year, typ)
    if l1yyyyfolderpath is None or not os.path.isdir(l1yyyyfolderpath):
      return []
    filepaths = hilo.find_l2_or_l3_filepaths_from_folderpath_w_year_month_as_refmonth_opt_ext_substr(
      l1yyyyfolderpath, year, month, dot_ext
    )
    if filepaths is None or len(filepaths) == 0:
      return []
    if self.substr:
      outfilepaths = []
      for fp in filepaths:
        filename = os.path.split(fp)[-1]
        if filename.find(self.substr) > -1:
          outfilepaths.append(fp)

  def find_l2_or_l3_filepaths_by_year_month_opt_ext_substr(
      self, year, month, dot_ext=None, substr=None
  ):
    return self.find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(
      year, month, day=None, dot_ext=dot_ext, substr=substr
    )

  def find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(
      self, year, month, day=None, dot_ext=None, substr=None
  ):
    """
    Obs: substr is used for both foldernames & filenames; dot_ext is used for filenames
      (someone may have created a folder with an extension, but the system will filter it out [not os.isfile()])
    When the caller intents to use parameter day, it should call the next method below ie
      self.find_l3yyyymmdd_filepaths_by_year_month_day_typ_ext(self, year, month, day, dotext)
        though it is just reorders the parameter sequence signature
    """
    l2folderpaths = self.find_l2yyyymm_folderpaths_by_year_month_opt_substr(year, month)
    if l2folderpaths is None or len(l2folderpaths) == 0:
      return []
    filepaths = []
    for folderpath in l2folderpaths:
      # for next call, day may be None
      localfilepaths = hilo.find_l2_or_l3_filepaths_from_folderpath_w_year_month_opt_day_ext_substr(
        folderpath, year, month, day, dot_ext, substr
      )
      filepaths += localfilepaths
    return filepaths

  def find_l2_or_l3_filepaths_by_refmonth_opt_ext_substr(self, refmonthdate, dotext=None, substr=None):
    try:
      year = int(refmonthdate.year)
      month = int(refmonthdate.month)
    except (AttributeError, TypeError, ValueError):
      return []
    return self.find_l2_or_l3_filepaths_by_year_month_opt_ext_substr(year, month, dotext, substr)

  def find_last_l2_or_l3_filepath_by_refmonth_opt_ext_substr(self, refmonthdate, dotext=None, substr=None):
    fps_in_month = self.find_l2_or_l3_filepaths_by_refmonth_opt_ext_substr(refmonthdate, dotext, substr)
    if fps_in_month and len(fps_in_month) > 0:
      return fps_in_month[-1]
    return None

  def find_all_l3yyyymm_filenames(self, dot_ext=None):
    all_l3yyyymmdd_filepaths = self.find_all_l3yyyymm_filepaths(dot_ext)
    all_l3yyyymmdd_filenames = [os.path.split(fp)[-1] for fp in all_l3yyyymmdd_filepaths]
    return all_l3yyyymmdd_filenames

  def find_all_l3yyyymm_filepaths(self, dot_ext=None):
    """
    returns the first element from find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(typ=None)
    """
    all_l3yyyymmdd_filepaths = []
    all_l2yyyymm_folderpaths = self.find_all_l2yyyymm_folderpaths()
    for l2yyyymm_folderpath in all_l2yyyymm_folderpaths:
      refmonthdate = hilo.extract_prefix_year_month_as_refmonth_from_path(l2yyyymm_folderpath)
      if refmonthdate is None:
        continue
      year, month = refmonthdate.year, refmonthdate.month
      l3yyyymmdd_filepaths = self.find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(year, month, dot_ext)
      if l3yyyymmdd_filepaths is None or len(l3yyyymmdd_filepaths) > 0:
        all_l3yyyymmdd_filepaths += l3yyyymmdd_filepaths
    return sorted(all_l3yyyymmdd_filepaths)

  def __str__(self):
    outstr = 'basefolderpath = "%s"' % self.basefolderpath
    return outstr


def adhoctest1():
  bfp = (
    '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/001 BDB bankdata/'
    'FI Extratos Mensais Ano a Ano BB OD'
  )
  disc = DatePrefixedOSFinder(bfp)
  print(disc)
  l1folders = disc.find_l1yyyy_folderpaths_w_opt_substr()
  for l1folder in l1folders:
    print('l1', l1folder)
  year = 2022
  l2folders = disc.find_l2yyyymm_folderpaths_any_months_by_year_opt_substr(year)
  print('-' * 40)
  for l2folder in l2folders:
    print('l2folder', l2folder)
  if len(l2folders) == 0:
    print('no l2folders for year', year)
  month = 10
  l2files = disc.find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(year, month)
  print('-' * 40)
  for l2file in l2files:
    print('l2file', l2file)
  if len(l2files) == 0:
    print('no l2files for year', year)


def adhoctest2():
  """
    l1_folders = disc.find_l1yyyy_folderpaths_w_opt_substr(year)
    print('l1', '-' * 40)
    print(year)
  """
  bfp = (
    '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/001 BDB bankdata/'
    'FI Extratos Mensais Ano a Ano BB OD/BB FI Rendimentos Diários htmls'
  )
  disc = DatePrefixedOSFinder(bfp)
  print(disc)
  l1folders = disc.find_l1yyyy_folderpaths_w_opt_substr()
  for l1folder in l1folders:
    print('l1', l1folder)
  year = 2023
  for l1folder in l1folders:
    print('l1folder', l1folder)
  if len(l1folders) == 0:
    print('no l1folders for year', year)
  l2folders = disc.find_l2yyyymm_folderpaths_any_months_by_year_opt_substr(year)
  print('l2', '-' * 40)
  for l2folder in l2folders:
    print('l2+folder', l2folder)
  if len(l2folders) == 0:
    print('no l2files for year', year)
  month = 10
  l3files = disc.find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(year, month)
  print('l3', '-' * 40)
  for i, l3file in enumerate(l3files):
    print(i+1, year, month, 'l3file', l3file)
  if len(l3files) == 0:
    print('no l3files for year', year, 'month', month)
  ext = 'csv'
  l3files = disc.find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(year, month, dot_ext=ext)
  print('l3', ext,  '-' * 40)
  for i, l3file in enumerate(l3files):
    fn = os.path.split(l3file)[-1]
    print(i+1, 'l3file ext', year, month, ext, fn, l3file)
  if len(l3files) == 0:
    print('no l3files for year', year, 'month', month, 'ext', ext)
  month = 11
  l3files = disc.find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(year, month, dot_ext=ext)
  print('l3', year, month, ext,  '-' * 40)
  for i, l3file in enumerate(l3files):
    fn = os.path.split(l3file)[-1]
    print(i+1, 'l3file ext', year, month, ext, fn, l3file)
  if len(l3files) == 0:
    print('no l3files for year', year, 'month', month, 'ext', ext)


def process():
  pass


if __name__ == '__main__':
  adhoctest2()
