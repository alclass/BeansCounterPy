#!/usr/bin/env python3
"""
lookup_monthrange_in_datafolder.py
  searches the datafolder for ini and fim refmonths
"""
import datetime
import os
import re
import settings as sett
str_yearplusblank_re = r'^\d{4}\ '
yearplusblank_re = re.compile(str_yearplusblank_re)
str_yeardashmonthplusblank_re = r'^\d{4}\-\d{2}\ '
yeardashmonthplusblank_re = re.compile(str_yeardashmonthplusblank_re)


def get_class_attrs(pclass):
  pdict = vars(pclass())
  plist = pdict.keys()
  plist = list(filter(lambda attr: not attr.startswith('_'), plist))
  return plist


def find_strinlist_that_starts_with_a_5charyearblank_via_if(entries):
  """
  recuperates year plus a blank
  """
  newentries = []
  for e in entries:
    try:
      _ = int(e[0:4])
      if e[4:5] != ' ':
        continue
      newentries.append(e)
    except (IndexError, ValueError):
      pass
  return newentries


def find_entries_that_start_with_a_yeardashmonth_via_re(entries):
  newentries = []
  for e in entries:
    if yeardashmonthplusblank_re.match(e):
      newentries.append(e)
  return newentries


def find_entries_that_start_with_a_yeardashmonth_via_if(entries):
  newentries = []
  for e in entries:
    try:
      _ = int(e[0:4])  # suppose a year number
      if e[4:5] != '-':
        continue
      mm = int(e[5:7])  # suppose a month number (including testing range 1..12 after in sequence)
      if mm < 1 or mm > 12:
        continue
      newentries.append(e)
    except (IndexError, ValueError):
      continue
  return newentries


def find_lesser_n_greater_yearprefixpaths_from_basepath(folder_asbspath):
  """
  returns a tuple with lesser_year_path & greater_year_path in a base path

  Example:
    + base_directory:
      + "2018 Extratos Mensais ..."
      + "2019 Extratos Mensais ..."
      + (...)
      + "2023 Extratos Mensais ..."
  In the scheme above, return will be:
    ("base_directory/2018 Extratos Mensais ...", "base_directory/2023 Extratos Mensais ...")

  Notice that this function looks up for the lesser year prefix foldername and the greater year prefix one.
  """
  if folder_asbspath is None or not os.path.isdir(folder_asbspath):
    return None, None
  entries = os.listdir(folder_asbspath)
  # compose fullpaths from entries
  fullpaths = list(map(lambda e: os.path.join(folder_asbspath, e), entries))
  # maintain only those that are directories
  direntries = list(filter(lambda e: os.path.isdir(e), fullpaths))
  # filter out those that do not have year-blank as prefix
  # recompose foldernames
  foldernames = [os.path.split(fn)[-1] for fn in direntries]
  yearprefix_foldernames = list(filter(lambda e: yearplusblank_re.match(e), foldernames))
  if len(yearprefix_foldernames) == 0:
    return None, None
  yearprefix_foldernames.sort()
  lesser_yearprefix_foldername = yearprefix_foldernames[0]
  greater_yearprefix_foldername = yearprefix_foldernames[-1]
  lesser_yearprefix_path = os.path.join(folder_asbspath, lesser_yearprefix_foldername)
  greater_yearprefix_path = os.path.join(folder_asbspath, greater_yearprefix_foldername)
  return lesser_yearprefix_path, greater_yearprefix_path


def find_lesser_or_greater_yeardashmonth_prefix_filename_from_basefolder(basepath, is_lesser=True):
  if basepath is None or not os.path.isdir(basepath):
    return None
  allentries = os.listdir(basepath)
  # compose full paths to know which ones are file
  fullpathentries = list(map(lambda e: os.path.join(basepath, e), allentries))
  filepaths = list(filter(lambda e: os.path.isfile, fullpathentries))
  filenames = [os.path.split(fp)[-1] for fp in filepaths]
  yearmonth_prefixed_filenames = find_entries_that_start_with_a_yeardashmonth_via_if(filenames)
  # somehow the line bellow is not filtering correctly, the solution was to use line above
  # yearmonth_prefixed_filenames = list(filter(lambda e: yeardashmonthplusblank_re.findall, filenames))
  if len(yearmonth_prefixed_filenames) == 0:
    return None
  yearmonth_prefixed_filenames.sort()
  if is_lesser:
    return yearmonth_prefixed_filenames[0]
  else:
    return yearmonth_prefixed_filenames[-1]


class PrefixDateFinder:

  def __init__(self, p_folder_asbspath):
    self.folder_asbspath = p_folder_asbspath
    self.lesser_yearprefix_path = None
    self.greater_yearprefix_path = None
    self.lesser_yearmonthprefix_filename = None
    self.greater_yearmonthprefix_filename = None
    self.process()

  @property
  def lesser_yearmonthprefix_filepath(self):
    return os.path.join(self.folder_asbspath, self.lesser_yearmonthprefix_filename)

  @property
  def greater_yearmonthprefix_filepath(self):
    return os.path.join(self.folder_asbspath, self.greater_yearmonthprefix_filename)

  @property
  def lesser_refmonthdate(self):
    if self.lesser_yearmonthprefix_filename:
      try:
        yearmonthprefix = self.lesser_yearmonthprefix_filename.split(' ')[0]
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
    if self.greater_yearmonthprefix_filename:
      try:
        yearmonthprefix = self.greater_yearmonthprefix_filename.split(' ')[0]
        pp = yearmonthprefix.split('-')
        year = int(pp[0])
        month = int(pp[1])
        pdate = datetime.date(year=year, month=month, day=1)
        return pdate
      except (IndexError, ValueError):
        pass
    return None

  def find_lesser_yeardashmonth_prefix_filename_from_yearprefixpath(self):
    self.lesser_yearmonthprefix_filename = find_lesser_or_greater_yeardashmonth_prefix_filename_from_basefolder(
      self.lesser_yearprefix_path,
      True
    )

  def find_greater_yeardashmonth_prefix_filename_from_yearprefixpath(self):
    self.greater_yearmonthprefix_filename = find_lesser_or_greater_yeardashmonth_prefix_filename_from_basefolder(
      self.greater_yearprefix_path,
      False
    )

  def find_n_set_both_lesser_n_greater_year_firstlevel_paths_from_basepath(self):
    self.lesser_yearprefix_path, self.greater_yearprefix_path = find_lesser_n_greater_yearprefixpaths_from_basepath(
      self.folder_asbspath
    )

  def process(self):
    self.find_n_set_both_lesser_n_greater_year_firstlevel_paths_from_basepath()
    self.find_lesser_yeardashmonth_prefix_filename_from_yearprefixpath()
    self.find_greater_yeardashmonth_prefix_filename_from_yearprefixpath()

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
  s = '2023-09 test'
  result = yeardashmonthplusblank_re.match(s)
  seq = 1
  print(seq, '[', s, '] result => ', result)
  s = 'bla 2023-09 test'
  result = yeardashmonthplusblank_re.match(s)
  seq += 1
  print(seq, '[', s, '] result => ', result)
  s = '2023-09a test'
  result = yeardashmonthplusblank_re.match(s)
  seq += 1
  print(seq, '[', s, '] result => ', result)
  print('end adhoctest')


def adhoctest():
  v = 'Worksheets 2018 Ext Men FI BB'
  matchobj = yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)
  v = '2018-01 Ext Men FI BB'
  matchobj = yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)
  v = ' 2018-01 Ext Men FI BB'
  matchobj = yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)
  v = 'fundo_report_example.txt'
  matchobj = yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)


def process():
  bb_fi_rootfolder_abspath = sett.BANK.get_bank_fi_folderpath_by_its3letter('bdb')
  dateprefixfinder = PrefixDateFinder(bb_fi_rootfolder_abspath)
  print(dateprefixfinder)


if __name__ == '__main__':
  """
  adhoctest_yeardashmonth_regexp()
  bb_fi_rootfolder_abspath = sett.get_bb_fi_rootfolder_abspath()
  adhoctest()
  """
  process()
