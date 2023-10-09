#!/usr/bin/env python3
"""
lookup_monthrange_in_datafolder.py
  searches the datafolder for ini and fim refmonths
"""
import datetime
import os
import fs.os.osfunctions as osfs
import fs.os.oshilofunctions as hilo
# import models.banks.banksgeneral
# import settings as sett



def get_class_attrs(pclass):
  pdict = vars(pclass())
  plist = pdict.keys()
  plist = list(filter(lambda attr: not attr.startswith('_'), plist))
  return plist


class PrefixDateFinder:

  def __init__(self, p_folder_asbspath):
    self.folder_asbspath = p_folder_asbspath
    self._firstlevel_year_folderpaths = None
    self._secondlevel_yearmonth_folderpaths = None

    self._lesser_yearprefix_foldername = None
    self._greater_yearprefix_foldername = None
    self._lesser_yearmonthprefix_filename = None
    self._greater_yearmonthprefix_filename = None
    self._yearmonth_filenames = None
    self._yearmonth_filepaths = None

    self._lesser_yeardashmonth_filename = None
    self._lesser_yeardashmonth_filepath = None
    self._greater_yeardashmonth_filename = None
    self._greater_yeardashmonth_filepath = None
    self.fill_in_attrs()

  @property
  def firstlevel_year_folderpaths(self):
    if self._firstlevel_year_folderpaths is None:
      self._firstlevel_year_folderpaths = []
      foldernames = osfs.find_foldernames_from_path(self.folder_asbspath)
      foldernames = hilo.find_strinlist_that_starts_with_a_5charyearblank_via_if(foldernames)
      self._firstlevel_year_folderpaths = sorted(map(lambda e: os.path.join(self.folder_asbspath, e), foldernames))
    return self._firstlevel_year_folderpaths

  @property
  def firstlevel_year_foldernames(self):
    """
    This property (firstlevel_year_foldernames) is recomputed each time, ie, not stored in object
    """
    _firstlevel_year_foldernames = []
    for firstlevel_year_folderpath in self.firstlevel_year_folderpaths:
      foldername = os.path.split(firstlevel_year_folderpath)[-1]
      return self.firstlevel_year_folderpaths[0]
    _firstlevel_year_foldernames.sort()
    return _firstlevel_year_foldernames

  @property
  def lesser_yearprefix_folderpath(self):
    """
      property not stored in object, recomputed each time
    """
    return self.firstlevel_year_folderpaths[0]

  @property
  def lesser_yearprefix_foldername(self):
    """
      property not stored in object, recomputed each time
    """
    folderpath = self.lesser_yearprefix_folderpath
    return os.path.split(folderpath)[-1]

  @property
  def greater_yearprefix_folderpath(self):
    """
      property not stored in object, recomputed each time
    """
    return self.firstlevel_year_folderpaths[-1]

  @property
  def greater_yearprefix_foldername(self):
    """
      property not stored in object, recomputed each time
    """
    folderpath = self.greater_yearprefix_folderpath
    return os.path.split(folderpath)[-1]

  @property
  def secondlevel_yearmonth_folderpaths(self):
    if self._secondlevel_yearmonth_folderpaths is None:
      self._secondlevel_yearmonth_folderpaths = []
      for firstlevel_year_folderpath in self.firstlevel_year_folderpaths:
        foldernames = osfs.find_foldernames_from_path(firstlevel_year_folderpath)
        yeardashmonthfoldernames = hilo.find_entries_that_start_with_a_yeardashmonth_via_if(foldernames)
        for yeardashmonthfoldername in yeardashmonthfoldernames:
          ppath = os.path.join(firstlevel_year_folderpath, yeardashmonthfoldername)
          self._secondlevel_yearmonth_folderpaths.append(ppath)
      self._secondlevel_yearmonth_folderpaths.sort()
    return self._secondlevel_yearmonth_folderpaths

  @property
  def secondlevel_yearmonth_foldernames(self):
    """
      property not stored in object, recomputed each time
    """
    _secondlevel_yearmonth_foldernames = []
    for secondlevel_yearmonth_folderpath in self.secondlevel_yearmonth_folderpaths:
      foldername = os.path.split(secondlevel_yearmonth_folderpath)[-1]
      _secondlevel_yearmonth_foldernames.append(foldername)
      _secondlevel_yearmonth_foldernames.sort()
    return _secondlevel_yearmonth_foldernames

  @property
  def lesser_secondlevel_yearmonth_folderpath(self):
    """
      property not stored in object, recomputed each time
    """
    return self.secondlevel_yearmonth_folderpaths[0]

  @property
  def lesser_secondlevel_yearmonth_foldername(self):
    """
      property not stored in object, recomputed each time
    """
    return self.secondlevel_yearmonth_foldernames[0]

  @property
  def greater_secondlevel_yearmonth_folderpath(self):
    """
      property not stored in object, recomputed each time
    """
    return self.secondlevel_yearmonth_folderpaths[-1]

  @property
  def greater_secondlevel_yearmonth_foldername(self):
    """
      property not stored in object, recomputed each time
    """
    return self.secondlevel_yearmonth_foldernames[-1]

  def find_n_set_yearmonth_filenames_n_paths(self, rerun=False):
    if self._yearmonth_filenames is not None and self._yearmonth_filepaths is not None and not rerun:
      return
    self._yearmonth_filenames = []
    self._yearmonth_filepaths = []
    last_folderpath = None
    for folderpath in self.secondlevel_yearmonth_folderpaths:
      filenames = osfs.find_filenames_with_regexp_on_path(r'\d{4}\-\d{2}\ ', folderpath)
      if len(filenames) == 0:
        continue
      filenames.sort()
      if self._lesser_yeardashmonth_filename is None:
        lesser_filename = filenames[0]
        self._lesser_yeardashmonth_filename = lesser_filename
        self._lesser_yeardashmonth_filepath = os.path.join(folderpath, lesser_filename)
      self._yearmonth_filenames += filenames
      filepaths = sorted(map(lambda e: os.path.join(folderpath, e), filenames))
      self._yearmonth_filepaths += filepaths
      last_folderpath = folderpath
    if self._greater_yeardashmonth_filename is None:
      self._greater_yeardashmonth_filename = self._yearmonth_filenames[-1]
      self._greater_yeardashmonth_filepath = os.path.join(last_folderpath, self._greater_yeardashmonth_filename)

  @property
  def yearmonth_filenames(self):
    if self._yearmonth_filenames is None:
      self.find_n_set_yearmonth_filenames_n_paths()
    return self._yearmonth_filenames

  @property
  def yearmonth_filepaths(self):
    if self._yearmonth_filepaths is None:
      self.find_n_set_yearmonth_filenames_n_paths()
    return self._yearmonth_filepaths

  @property
  def lesser_yeardashmonth_filename(self):
    """
  self.greater_yearmonthprefix_filename = find_lesser_or_greater_yeardashmonth_prefix_filename_from_basefolder(
      self.gre,
      False
    )

    """
    if self._lesser_yeardashmonth_filename is None:
      self.find_n_set_yearmonth_filenames_n_paths()
    return self._lesser_yeardashmonth_filename

  @property
  def greater_yeardashmonth_filepath(self):
    if self._greater_yeardashmonth_filepath is None:
      self.find_n_set_yearmonth_filenames_n_paths()
    return self._greater_yeardashmonth_filepath

  @property
  def lesser_refmonthdate(self):
    if self.lesser_yeardashmonth_filename:
      try:
        yearmonthprefix = self.lesser_yeardashmonth_filename.split(' ')[0]
        pp = yearmonthprefix.split('-')
        year = int(pp[0])
        month = int(pp[1])
        pdate = datetime.date(year=year, month=month, day=1)
        return pdate
      except (IndexError, ValueError):
        pass
    return None

  @property
  def greater_refmonthdate(self):
    if self.lesser_yeardashmonth_filename:
      try:
        yearmonthprefix = self.lesser_yeardashmonth_filename.split(' ')[0]
        pp = yearmonthprefix.split('-')
        year = int(pp[0])
        month = int(pp[1])
        pdate = datetime.date(year=year, month=month, day=1)
        return pdate
      except (IndexError, ValueError):
        pass
    return None

  def find_yearmonth_folderpaths_by_year(self, year):
    str_re = r'' + str(year) + r'\ '
    fns = osfs.find_foldernames_with_regexp_on_path(str_re, self.firstlevel_year_foldernames)
    if fns is None or len(fns) == 0:
      return None
    foldername = fns[0]
    innerfolderpath = os.path.join(self.folder_asbspath, foldername)
    folderpaths = osfs.find_foldernames_from_path(innerfolderpath)
    return folderpaths

  def find_n_set_both_lesser_n_greater_year_firstlevel_paths_from_basepath(self):
    """
    """
    return self.lesser_yearprefix_folderpath, self.greater_yearprefix_folderpath

  def fill_in_attrs(self):
    self.find_n_set_yearmonth_filenames_n_paths()

  def outdict_dyn(self):
    attrs = vars(self)
    attrs = list(filter(lambda a: not a.startswith('_'), attrs))
    pdict = {}
    for attr in attrs:
      pdict[attr] = eval('self.'+attr)
    return pdict

  def outdict(self):
    pdict = {
      'folder_asbspath': self.folder_asbspath,
      'lesser_yearprefix_path': self.lesser_yearprefix_path,
      'greater_yearprefix_path': self.greater_yearprefix_path,
      'lesser_yearmonthprefix_filename': self.lesser_yearmonthprefix_filename,
      'greater_yearmonthprefix_filename': self.greater_yearmonthprefix_filename,
      'lesser_refmonthdate': self.lesser_refmonthdate,
      'greater_refmonthdate': self.greater_refmonthdate,
    }
    return pdict

  def __str__(self):
    outstr = """
      folder_asbspath                  = {folder_asbspath}
      lesser_yearprefix_path           = {lesser_yearprefix_path}
      greater_yearprefix_path          = {greater_yearprefix_path}
      lesser_yearmonthprefix_filename  = {lesser_yearmonthprefix_filename}
      greater_yearmonthprefix_filename = {greater_yearmonthprefix_filename}
      lesser_refmonthdate  = {lesser_refmonthdate}
      greater_refmonthdate  = {greater_refmonthdate}
    """.format(**self.outdict())
    return outstr


def adhoctest_yeardashmonth_regexp():
  print('='*40)
  print('adhoctest_yeardashmonth_regexp')
  print('='*40)
  s = '2023-09 test'
  result = hilo.yeardashmonthplusblank_re.match(s)
  seq = 1
  print(seq, '[', s, '] result => ', result)
  s = 'bla 2023-09 test'
  result = hilo.yeardashmonthplusblank_re.match(s)
  seq += 1
  print(seq, '[', s, '] result => ', result)
  s = '2023-09a test'
  result = hilo.yeardashmonthplusblank_re.match(s)
  seq += 1
  print(seq, '[', s, '] result => ', result)
  print('end adhoctest')


def adhoctest2():
  print('='*40)
  print('adhoctest2')
  print('='*40)
  v = 'Worksheets 2018 Ext Men FI BB'
  matchobj = hilo.yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)
  v = '2018-01 Ext Men FI BB'
  matchobj = hilo.yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)
  v = ' 2018-01 Ext Men FI BB'
  matchobj = hilo.yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)
  v = 'fundo_report_example.txt'
  matchobj = hilo.yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)


def adhoctest():
  """
  Notice that to avoid "circular imports" this module cannot import models.banks.banksgeneral
    (because that imports this),
    so the adhoctest here will have variable bb_fi_rootfolder_abspath hardcoded
  If this path changes, for running this adhoctest(), variable must be updated too
    bb_fi_rootfolder_abspath = models.banks.banksgeneral.BANK.get_bank_fi_folderpath_by_its3letter('bdb')
  """
  bb_fi_rootfolder_abspath = (
      '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
      '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD'
  )
  dateprefixfinder = PrefixDateFinder(bb_fi_rootfolder_abspath)
  print('='*40)
  print('adhoctest')
  print('='*40)
  print(dateprefixfinder)
  print('dateprefixfinder.lesser_yearmonthprefix_folderpath()')


def process():
  pass


if __name__ == '__main__':
  """
  adhoctest_yeardashmonth_regexp()
  bb_fi_rootfolder_abspath = sett.get_bb_fi_rootfolder_abspath()
  process()
  """
  adhoctest()
  adhoctest2()
  adhoctest_yeardashmonth_regexp()
