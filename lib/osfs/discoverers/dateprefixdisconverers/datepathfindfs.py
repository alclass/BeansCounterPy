#!/usr/bin/env python3
"""
lib/osfs/datepathfindfs.py
  Extra functions in the 'osfs' area that deals with the year & month (or others) prefixes to OSEntries.

Function example:
  1) in filefolder_retriever_fs.py: there is a function for finding filenames from a folder
     => osfunctions.find_filenames_from_path(param_folderpath)
  2) in here (datepathfindfs.py): there is a function for finding filepaths from a folder starting with yyyy-mm
     => oshilofunctions.find_filepaths_whose_filename_starts_with_a_yeardashmonth_via_if(basefolderpath)

'hilo' imports 'osfs' (the inverse cannot happen due to circular dependency),
  so another way of thinking about 'hilo', loosely speaking, is that it is on top of 'osfs'.

Notice on the word 'hilo':
  The 'hilo' (high & low) is just a sort of fancy name chosen for these extra functions
    also, it has nothing to do with the greek prefix in hilomorphism, an Aristotelian concept...
    also, it is not the 'hilo' word from Spanish which means thread et al.
"""
import datetime
import glob
import os
import re
from pathlib import Path, PosixPath
import settings as sett
import lib.osfs.filefolder_retriever_fs as osfs
yearplusblank_str = r"^(?P<year>\d{4})\s(?P<after>.*)$"
yearplusblank_re = re.compile(yearplusblank_str)
yeardashmonthplusblank_str = r"^(?P<year>\d{2,4})-(?P<month>[1-9]|0[1-9]|1[0-2])\s(?P<after>.*)$"
yeardashmonthplusblank_re = re.compile(yeardashmonthplusblank_str)
yeardashmonthdashdayplusblank_str = r"^(?P<year>\d{2,4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\s(?P<after>.*)$"
yeardashmonthdashdayplusblank_re = re.compile(yeardashmonthdashdayplusblank_str)


def extract_int_prefix_fr_int_space_str(name: str) -> int | None:
  """
  For the extraction of year, year should be followed by a blank
  """
  try:
    pp = name.split(' ')
    intn = int(pp[0])
    return intn
  except (IndexError, TypeError, ValueError):
    pass
  return None


def extract_year_prefix_fr_pathsleaf(ppath: str | PosixPath) -> int | None:
  try:
    if ppath.find(os.sep) < 0:
      # the path is a sole name
      entryname = ppath
    else:
      # path is a separator, pick up the name part (the 'leaf' part)
      entryname = os.path.split(ppath)[-1]
    year = extract_int_prefix_fr_int_space_str(entryname)
    return year
  except (IndexError, TypeError, ValueError):
    pass
  return None


def extract_filepaths_from_folderpaths(folderpaths: list[PosixPath], dot_ext: str | None = None) -> list[PosixPath]:
  if dot_ext is not None:
    if not dot_ext.startswith('.'):
      dot_ext = '.' + dot_ext
  filepaths = []
  for folderpath in folderpaths:
    folderpath = Path(os.path.abspath(folderpath))
    entries = os.listdir(folderpath)
    if len(entries) < 1:
      continue
    fpaths = map(lambda e: folderpath / e, entries)
    fpaths = filter(lambda e: e.is_file(), fpaths)
    if dot_ext is not None:
      # used e.suffix | @see also e.matches(dot_exp) and str(e).endswith(), not our case sufixes == ['tar', 'gz]
      fpaths = filter(lambda e: e.suffix == dot_ext, fpaths)
    filepaths += list(fpaths)
  return filepaths


def find_files_w_prefix_fr_folderpath(
    prefix: str,
    folderpath: PosixPath | str,
    dot_ext: str = None,
    dowalk: bool = False,
  ) -> list[PosixPath]:
  if folderpath is None:
    return []
  folderpath = Path(os.path.abspath(folderpath))
  dot_ext = dot_ext if dot_ext is not None else ''
  if dot_ext != '' and not dot_ext.startswith('.'):
    dot_ext = f".{dot_ext}"
  allfoundfiles = []
  for curpath, _, filenames in os.walk(folderpath):
    foundfilenames = filter(lambda e: e.startswith(prefix) and e.endswith(dot_ext), filenames)
    foundfiles = [folderpath / fn for fn in foundfilenames]
    allfoundfiles += foundfiles
    if not dowalk:
      break
  return allfoundfiles


def find_refmonthprefixed_files_fr_folderpath(
    basefolderpath, year, typ=None, dot_ext=None
):
  folderpaths = find_specyear_typ_folderpaths_from_folderpath(basefolderpath, year, typ)
  filepaths = extract_filepaths_from_folderpaths(folderpaths, dot_ext)
  return filepaths


def filterin_names_that_start_with_a_yeardashmonth_via_if(names) -> list[str]:
  outnames = []
  for e in names:
    try:
      _ = int(e[0:4])  # suppose a year number
      if e[4:5] != '-':
        continue
      mm = int(e[5:7])  # suppose a month number (including testing range 1..12 after in sequence)
      if mm < 1 or mm > 12:
        continue
      outnames.append(e)
    except (IndexError, ValueError):
      continue
  return outnames


def filterin_names_that_start_with_a_yeardashmonth_via_re(entries):
  outnames = []
  for e in entries:
    if yeardashmonthplusblank_re.match(e):
      outnames.append(e)
  return outnames


def find_specyear_typ_folderpaths_from_folderpath(basefolderpath, year, typ=None):
  foldernames = find_l1foldernames_all_years_from_basefolder_opt_substr(basefolderpath, typ)
  specyearfoldernames = filter(lambda e: e.startswith(str(year)), foldernames)
  specyearfolderpaths = [os.path.join(basefolderpath, e) for e in specyearfoldernames]
  return specyearfolderpaths


def find_foldernames_in_folderpath(basefolderpath, typ=None):
  if basefolderpath is None or not os.path.isdir(basefolderpath):
    return []
  osentries = os.listdir(basefolderpath)
  foldernames = [e for e in osentries if os.path.isdir(os.path.join(basefolderpath, e))]
  if typ:
    foldernames = filter(lambda e: e.find(typ) > - 1, foldernames)
  return sorted(foldernames)


def find_l2yyyyfolderpaths_any_months_from_folderpath_w_year_opt_substr(basefolderpath, year, substr=None):
  foldernames = find_foldernames_in_folderpath(basefolderpath, substr)
  try:
    prefix = '{year}-'.format(year=year)
    foldernames = filter(lambda e: e.startswith(str(prefix)), foldernames)
    if isinstance(substr, str):
      foldernames = filter(lambda e: e.find(substr) > -1, foldernames)
  except (TypeError, ValueError):
    pass
  folderpaths = [os.path.join(basefolderpath, e) for e in foldernames]
  return sorted(folderpaths)


def find_l2yyyymmfolderpaths_from_folderpath_w_year_month_opt_substr(basefolderpath, year, month, substr=None):
  foldernames = find_foldernames_in_folderpath(basefolderpath, substr)
  try:
    prefix = '{year}-{month:02} '.format(year=year, month=month)
    foldernames = filter(lambda e: e.startswith(str(prefix)), foldernames)
    if isinstance(substr, str):
      foldernames = filter(lambda e: e.find(substr) > -1, foldernames)
  except (TypeError, ValueError):
    pass
  folderpaths = [os.path.join(basefolderpath, e) for e in foldernames]
  return folderpaths


def find_l2_or_l3_filenames_from_folderpath_w_year_month_opt_ext_substr(
    basefolderpath, year, month, dot_ext=None, substr=None
):
  return find_l2_or_l3_filenames_from_folderpath_w_year_month_opt_day_ext_substr(
    basefolderpath, year, month, day=None, dot_ext=dot_ext, substr=substr
  )


def find_l2_or_l3_filenames_from_folderpath_w_year_month_opt_day_ext_substr(
    basefolderpath, year, month, day=None, dot_ext=None, substr=None
):
  """
  When using parameter "day", this method should only be called by the next function ie
    find_filenames_w_year_month_day_ext_in_folderpath(basefolderpath, year, month, day, dot_ext)
    (a kind of private function under the hypothesis "day is not None")
  """
  if basefolderpath is None or not os.path.isdir(basefolderpath):
    return []
  try:
    year = int(year)
    month = int(month)
    if day is not None:
      day = int(day)
  except ValueError:
    return []
  if 0 > month > 12:
    return []
  if day is None:
    # notice that 'yyyy-mm ' or 'yyy-mm-dd' are expected
    prefixstr = '{year}-{month:02}'.format(year=year, month=month)
  else:
    prefixstr = '{year}-{month:02}-{day:02} '.format(year=year, month=month, day=day)
  l2_or_l3_filenames = osfs.retrieve_filenames_in_folder_or_empty(basefolderpath)
  if l2_or_l3_filenames is None or len(l2_or_l3_filenames) == 0:
    return []
  l2_or_l3_filenames = filter(lambda e: e.startswith(prefixstr), l2_or_l3_filenames)
  if isinstance(substr, str):
    l2_or_l3_filenames = filter(lambda e: e.find(substr) > -1, l2_or_l3_filenames)
  if dot_ext is None:
    return l2_or_l3_filenames
  if isinstance(dot_ext, str):
    if not dot_ext.startswith('.'):
      dot_ext = '.' + dot_ext
    l2_or_l3_filenames = filter(lambda e: e.endswith(dot_ext), l2_or_l3_filenames)
  return sorted(l2_or_l3_filenames)


def find_l2_or_l3_filenames_from_folderpath_w_year_month_as_refmonth_opt_ext_substr(
    basefolderpath, refmonthdate, dot_ext=None, substr=None
):
  try:
    year = refmonthdate.year
    month = refmonthdate.month
    filenames = find_l2_or_l3_filenames_from_folderpath_w_year_month_opt_ext_substr(
      basefolderpath, year, month, dot_ext, substr
    )
    if filenames is None or len(filenames) == 0:
      return []
    filenames = sorted(filenames)
    return filenames
  except (AttributeError, TypeError):
    pass
  return []


def find_l2_or_l3_filepaths_from_folderpath_w_year_month_opt_day_ext_substr(
    basefolderpath, year, month, day=None, dot_ext=None, substr=None
):
  filenames = find_l2_or_l3_filenames_from_folderpath_w_year_month_opt_day_ext_substr(
    basefolderpath, year, month, day, dot_ext, substr
  )
  filepaths = sorted(map(lambda e: os.path.join(basefolderpath, e), filenames))
  return filepaths


def find_l2_or_l3_filepaths_from_folderpath_w_year_month_opt_ext_substr(
    basefolderpath, year, month, dot_ext=None, substr=None
):
  filenames = find_l2_or_l3_filenames_from_folderpath_w_year_month_opt_ext_substr(
    basefolderpath, year, month, dot_ext, substr
  )
  filepaths = sorted(map(lambda e: os.path.join(basefolderpath, e), filenames))
  return filepaths


def find_l2_or_l3_filepaths_from_folderpath_w_year_month_as_refmonth_opt_ext_substr(
    basefolderpath, refmonthdate, dot_ext=None, substr=None
):
  filenames = find_l2_or_l3_filenames_from_folderpath_w_year_month_as_refmonth_opt_ext_substr(
    basefolderpath, refmonthdate, dot_ext, substr
  )
  filepaths = [os.path.join(basefolderpath, e) for e in filenames]
  return filepaths


def find_yyyyfilenames_from_folderpath_w_year_opt_ext_substr(basefolderpath, year, dot_ext=None, substr=None):
  """

  """
  if basefolderpath is None or not os.path.isdir(basefolderpath):
    return []
  asterisk_dot_ext = '*'
  if dot_ext is not None:
    if not dot_ext.startswith('.'):
      asterisk_dot_ext = asterisk_dot_ext + '.' + dot_ext
    else:
      asterisk_dot_ext = asterisk_dot_ext + dot_ext
  filepaths = glob.glob(basefolderpath + '/' + asterisk_dot_ext)
  filepaths = filter(lambda e: os.path.isfile(e), filepaths)
  filenames = [os.path.split(fp)[-1] for fp in filepaths]
  try:
    stryear = str(year) + ' '
    filenames = filter(lambda e: e.startswith(stryear), filenames)
  except (TypeError, ValueError):
    pass
  if isinstance(substr, str):
    filenames = filter(lambda e: e.find(substr) > -1, filenames)
  return filenames


def find_yyyyfilepaths_from_folderpath_w_year_opt_ext_substr(basefolderpath, year, dot_ext=None, substr=None):
  filenames = find_yyyyfilenames_from_folderpath_w_year_opt_ext_substr(basefolderpath, year, dot_ext, substr)
  if filenames is None or len(filenames) == 0:
    return []
  filepaths = [os.path.join(basefolderpath, e) for e in filenames]
  return filepaths


def find_filepaths_w_year_month_ext_in_folderpath(basefolderpath, year, month, dot_ext=None):
  yearmonthfilenames = find_l2_or_l3_filenames_from_folderpath_w_year_month_opt_ext_substr(
    basefolderpath, year, month, dot_ext
  )
  if yearmonthfilenames is None or len(yearmonthfilenames) == 0:
    return []
  yearmonthfilepaths = sorted(map(lambda e: os.path.join(basefolderpath, e), yearmonthfilenames))
  return yearmonthfilepaths


def find_filepaths_w_year_month_as_refmonth_n_ext_in_folderpath(basefolderpath, refmonthdate, dot_ext=None):
  try:
    year = refmonthdate.year
    month = refmonthdate.month
    return find_filepaths_w_year_month_ext_in_folderpath(basefolderpath, year, month, dot_ext)
  except (AttributeError, TypeError):
    pass
  return []


def find_filepaths_whose_filenames_start_with_a_yeardashmonth_via_if(basefolderpath, dot_ext=None):
  filenames = osfs.retrieve_filenames_in_folder_or_empty(basefolderpath)
  filenames = filterin_names_that_start_with_a_yeardashmonth_via_if(filenames)
  if dot_ext is not None:
    if not dot_ext.startswith('.'):
      dot_ext = '.' + dot_ext
    filenames = filter(lambda e: e.endswith(dot_ext), filenames)
  filepaths = sorted(map(lambda e: os.path.join(basefolderpath, e), filenames))
  return filepaths


def find_yearmonthfolderpath_from(yearfolderpath, refmonthdate):
  direntries = os.listdir(yearfolderpath)
  paths = map(lambda e: os.path.join(yearfolderpath, e), direntries)
  folderpaths = filter(lambda e: os.path.isdir(e), paths)
  foldernames = map(lambda e: os.path.split(e)[-1], folderpaths)
  prefix_yearmonth = "{year}-{month:02} ".format(year=refmonthdate.year, month=refmonthdate.month)
  yearmonthfoldernames = filter(lambda e: e.startswith(prefix_yearmonth), foldernames)
  yearmonthfolderpaths = sorted(map(lambda e: os.path.join(yearfolderpath, e), yearmonthfoldernames))
  if len(yearmonthfolderpaths) == 0:
    return []
  if len(yearmonthfolderpaths) > 1:
    error_msg = f"""Error with data:
     there are more than one folder with year/month {refmonthdate}
     prefixed in path {yearfolderpath}
    """.format(refmonthdate=refmonthdate, yearfolderpath=yearfolderpath)
    raise OSError(error_msg)
  return yearmonthfolderpaths[0]


def find_l1foldernames_all_years_from_basefolder_opt_substr(basefolderpath, substr=None):
  foldernames = osfs.retrieve_foldernames_from_basefolderpath(basefolderpath)
  yearfoldernames = filter(lambda e: yearplusblank_re.match(e), foldernames)
  if isinstance(substr, str):
    yearfoldernames = filter(lambda e: e.find(substr) > -1, yearfoldernames)
  yearfoldernames = sorted(yearfoldernames)
  return yearfoldernames


def find_l1folderpaths_all_years_from_basefolder_opt_substr(basefolderpath, substr=None):
  yyyyfoldernames = find_l1foldernames_all_years_from_basefolder_opt_substr(basefolderpath, substr)
  yyyyfolderpaths = sorted(map(lambda e: os.path.join(basefolderpath, e), yyyyfoldernames))
  return yyyyfolderpaths


def find_foldernames_that_starts_with_a_spec_year_via_re_in_basefolder(basefolderpath, year, typ=None):
  yearfoldernames = find_l1foldernames_all_years_from_basefolder_opt_substr(basefolderpath)
  stryearplusblank = str(year) + ' '
  yearfoldernames = sorted(filter(lambda e: e.startswith(stryearplusblank), yearfoldernames))
  return yearfoldernames


def find_foldername_that_starts_with_a_spec_year_via_re_in_basefolder(basefolderpath, year, typ=None):
  foldernames = find_l1foldernames_all_years_from_basefolder_opt_substr(basefolderpath, year)
  if len(foldernames) > 0:
    return foldernames[0]
  return None


def find_l1yyyyfoldernames_from_basefolder_w_year_opt_substr(basefolderpath, year, substr=None):
  yearfoldernames = find_l1foldernames_all_years_from_basefolder_opt_substr(basefolderpath, substr)
  try:
    year = int(year)
    yearprefixstr = f'{year} '  # notice the blank/gap/charspace after the year in the prefix
    yearfoldernames = sorted(filter(lambda e: yearprefixstr.startswith(yearprefixstr), yearfoldernames))
    return yearfoldernames
  except (TypeError, ValueError):
    pass
  return []


def find_l1yyyyfolderpaths_from_basefolder_w_year_opt_substr(basefolderpath, year, substr=None):
  yearfoldernames = find_l1yyyyfoldernames_from_basefolder_w_year_opt_substr(basefolderpath, year, substr)
  yearfolderpaths = [os.path.join(basefolderpath, e) for e in yearfoldernames]
  return yearfolderpaths


def find_lesser_or_greater_yeardashmonth_prefix_filename_from_basefolder(basepath, is_lesser=True):
  if basepath is None or not os.path.isdir(basepath):
    return None
  allentries = os.listdir(basepath)
  # compose full paths to know which ones are file
  fullpathentries = list(map(lambda e: os.path.join(basepath, e), allentries))
  filepaths = list(filter(lambda e: os.path.isfile, fullpathentries))
  filenames = [os.path.split(fp)[-1] for fp in filepaths]
  yearmonth_prefixed_filenames = filterin_names_that_start_with_a_yeardashmonth_via_if(filenames)
  # somehow the line bellow is not filtering correctly, the solution was to use line above
  # yearmonth_prefixed_filenames = list(filter(lambda e: yeardashmonthplusblank_re.findall, filenames))
  if len(yearmonth_prefixed_filenames) == 0:
    return None
  yearmonth_prefixed_filenames.sort()
  if is_lesser:
    return yearmonth_prefixed_filenames[0]
  else:
    return yearmonth_prefixed_filenames[-1]


def extract_date_from_yearmonthprefix_str(yearmonthprefix_str):
  """
  Eg: suppose a filename => "2022-10 FI extrato.txt"
    From this, function should return datetime.date(2022, 10, 1)
  """
  if yearmonthprefix_str is None:
    return None
  try:
    pp = yearmonthprefix_str.split(' ')
    ppp = pp[0].split('-')
    year = int(ppp[0])
    month = int(ppp[1])
    pdate = datetime.date(year=year, month=month, day=1)
    return pdate
  except (IndexError, ValueError):
    pass
    return None


def extract_year_from_yearprefix_str(yearprefix_str):
  """
  Eg: suppose a filename => "2022-10 FI extrato.txt"
    From this, function should return datetime.date(2022, 10, 1)
  """
  if yearprefix_str is None:
    return None
  try:
    pp = yearprefix_str.split(' ')
    ppp = pp[0].split('-')
    year = int(ppp[0])
    return year
  except (IndexError, ValueError):
    pass
    return None


def find_a_yearprefixedstr_from_strlist_by_year(year, yearprefix_strlist):
  """
  Eg:
    1) suppose parameters strlist =>
    1-1 year = 2021
    1-2 yearprefix_strlist = \
       ["2018 FI Extratos Mensais", "2021 FI Extratos Mensais", "2023 FI Extratos Mensais"]
    From this, function should return "2021 FI Extratos Mensais" (because its prefix coincides with 'year')

  Notice also that it will find the first one, others alphabetically higher will not be found.
  """
  if yearprefix_strlist is None or len(yearprefix_strlist) == 0:
    return None
  for yearprefix_str in yearprefix_strlist:
    extr_year = extract_year_from_yearprefix_str(yearprefix_str)
    if extr_year is None:
      return None
    try:
      if int(year) == int(extr_year):
        return yearprefix_str
    except ValueError:
      pass
  return None


def derive_refmonthdate_from_a_yearmonthprefixedstr(yearmonthprefixedstr):
  if yearmonthprefixedstr is None:
    return yearmonthprefixedstr
  try:
    yearmonthprefixedstr = str(yearmonthprefixedstr)
    pp = yearmonthprefixedstr.split(' ')
    ppp = pp[0].split('-')
    year = int(ppp[0])
    month = int(ppp[1])
    refmonthdate = datetime.date(year=year, month=month, day=1)
    return refmonthdate
  except (IndexError, ValueError):
    pass
  return None


def derive_refmonthdate_from_a_yearmonthprefixedstr_or_mostrecent(yearmonthprefixedstr=None):
  refmonthdate = derive_refmonthdate_from_a_yearmonthprefixedstr(yearmonthprefixedstr)
  if refmonthdate is not None:
    return refmonthdate
  today = datetime.date.today()
  if today.day == 1:
    return today
  refmonthdate = datetime.date(year=today.year, month=today.month, day=1)
  return refmonthdate


def adhoctest():
  """
  yearprefix_strlist = ["2018 FI Extratos Mensais", "2021 FI Extratos Mensais", "2023 FI Extratos Mensais"]
  year = 2021
  expected_str = find_a_yearprefixedstr_from_strlist_by_year(year, yearprefix_strlist)
  print 'for', year, '=>', expected_str
  year = 2022
  expected_str = find_a_yearprefixedstr_from_strlist_by_year(year, yearprefix_strlist)
  print 'for', year, '=>', expected_str
  year = 'bla'
  expected_str = find_a_yearprefixedstr_from_strlist_by_year(year, yearprefix_strlist)
  print 'for', year, '=>', expected_str
  yearmonthprefix_str = "2022-10 FI extrato.txt"
  pdate = extract_date_from_yearmonthprefix_str(yearmonthprefix_str)
  print 'for', yearmonthprefix_str, '=>', pdate
  """
  print('Adhoc test for find_filepaths_w_year_month_ext_in_folderpath()')
  refmonthdate = '2022-12'
  basefolderpath = '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
  basefolderpath += '104 CEF bankdata/FI Extratos Mensais Ano a Ano CEF OD/2022 FI extratos mensais CEF'
  ext = 'xml'
  print('parameters refmonth', refmonthdate, 'ext or dot_ext', ext)
  print('folder', basefolderpath)
  fps = find_filepaths_w_year_month_ext_in_folderpath(refmonthdate, basefolderpath, ext)
  if fps is not None:
    for fp in fps:
      print(fp)


def adhoctest2():
  rootdir = sett.APP_ROOTFOLDER
  rootdir = Path(rootdir)
  ppaths = [
    rootdir / 'lib/osfs',
    rootdir / 'lib/datesetc',
  ]
  retlist = extract_filepaths_from_folderpaths(ppaths, '.py')
  scrmsg = f"""
  extract_filepaths_from_folderpaths(ppaths)
  input -> {ppaths}
  output -> """
  print(scrmsg)
  for fpath in retlist:
    print(fpath)
  total = len(retlist)
  print('total', total)


import art.finc.bnk.inst.bb as bbcfg  # bbcfg.BB_CC_EXTR_ANO_A_ANO_BASEFOLDER
def adhoctest3():
  folderpath = bbcfg.BB_CC_EXTR_ANO_A_ANO_BASEFOLDER
  prefix = '2024-10 '
  dot_ext = None  # 'html'
  dowalk = True
  foundfiles = find_files_w_prefix_fr_folderpath(
    prefix=prefix,
    folderpath=folderpath,
    dot_ext=dot_ext,
    dowalk=dowalk,
  )
  scrmsg = f"""Calling:
    foundfiles = find_files_w_prefix_fr_folderpath(
    prefix={prefix},
    folderpath={folderpath},
    dot_ext={dot_ext},
    dowalk={dowalk},
  )
  Returing:
  """
  print(scrmsg)
  for fp in foundfiles:
    print(fp)


def adhoctest4():
  t = '2023-4 blah'
  match_o = yeardashmonthplusblank_re.match(t)
  if match_o:
    pass
  scrmsg = f"{t} -> {match_o}"
  if match_o:
    year = match_o.group('year')
    month = int(match_o.group('month'))
    scrmsg = f"{t} -> year = {year} | month = {month:02}"
  print(scrmsg)
  t = '2023-2-7 blah'
  match_o = yeardashmonthdashdayplusblank_re.match(t)
  if match_o:
    pass
  scrmsg = f"{t} -> {match_o}"
  if match_o:
    year = match_o.group('year')
    month = int(match_o.group('month'))
    day = int(match_o.group('day'))
    scrmsg = f"{t} -> year = {year} | month = {month:02} | day = {day:02}"
  print(scrmsg)



def process():
  pass


if __name__ == '__main__':
  """
  process()
  adhoctest()
  adhoctest2()
  adhoctest3()
  """
  adhoctest4()
