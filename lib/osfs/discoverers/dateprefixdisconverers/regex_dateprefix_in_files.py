#!/usr/bin/env python3
"""
lib/osfs/discoverers/dateprefixdisconverers/regex_dateprefix_in_files.py
  Contains some functions for finding files based on date or date-combination as prefix.

  The date finding mixes a regex with a date-extracting function.
  These functions are useful for finding filenames (and files) having a date-prefix.

  There are also some extra functions in here.
"""
import os
from  pathlib import Path
import re
import datetime
import lib.datesetc.refmonth_fs as rmfs
import lib.osfs.filefolder_retriever_fs as ffretr
gather_all_files_up_from = ffretr.gather_all_files_up_from
# Simple regex to grab the structure
dateprefix_pattern = r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\s(?P<after>.*)$"
dateprefix_re = re.compile(dateprefix_pattern)
refmonthprefix_pattern = r"^(?P<year>\d{4})-(?P<month>\d{1,2})\s(?P<after>.*)$"
refmonthprefix_re = re.compile(refmonthprefix_pattern)
yearprefix_pattern = r"^(?P<year>\d{4})\s(?P<after>.*)$"
yearprefix_re = re.compile(yearprefix_pattern)
text = "2024-02-29 text goes here"


def match_n_get_yearprefix_in_str(pstr):
  """
  """
  pstr = str(pstr)
  match_o = yearprefix_re.match(pstr)
  if match_o:
    gd = match_o.groupdict()
    try:
      # datetime validation naturally raises a ValueError for invalid days/leap years
      year = int(gd['year'])
      return year
    except ValueError:
      pass
  return None


def match_n_get_refmonthprefix_in_str(pstr):
  """
      valid_date = datetime.datetime.strptime(f {gd['year']}-{gd['month']}-{gd['day']}", "%Y-%m-%d")
      print(f"Valid date! {valid_date.date()} -> After: {gd['after']}")
    except ValueError:
      print("Regex matched formatting, but calendar date is impossible.")
  """
  pstr = str(pstr)
  match_o = refmonthprefix_re.match(pstr)
  if match_o:
    gd = match_o.groupdict()
    try:
      # datetime validation naturally raises a ValueError for invalid days/leap years
      year, month = gd['year'], gd['month']
      year, month = tuple(map(int, (year, month)))
      idate = datetime.date(year=year, month=month, day=1)
      return idate
    except ValueError:
      pass
  return None


def match_n_get_dateprefix_in_str(pstr):
  """

  This piece is a reminder for how to use datetime.datetime.strptime:
    try:
      # (...)
      valid_date = datetime.datetime.strptime(f {gd['year']}-{gd['month']}-{gd['day']}", "%Y-%m-%d")
      print(f"Valid date! {valid_date.date()} -> After: {gd['after']}")
    except ValueError:
      print("Regex matched formatting, but calendar date is impossible.")
  """
  pstr = str(pstr)
  match_o = dateprefix_re.match(pstr)
  if match_o:
    gd = match_o.groupdict()
    try:
      year, month, day = gd['year'], gd['month'], gd['day']
      year, month, day = tuple(map(int, (year, month, day)))
      # datetime validation naturally raises a ValueError if year, month, day are inconsistent
      idate = datetime.date(year=year, month=month, day=day)
      return idate
    except ValueError:
      pass
  return None


def match_str_w_givenyearprefix(pdate, pstr):
  """
  This function is mainly for use in a filter()
  """
  return pdate == match_n_get_yearprefix_in_str(pstr)


def match_str_w_givendateprefix(pdate, pstr):
  """
  This function is mainly for use in a filter()
  """
  return pdate == match_n_get_dateprefix_in_str(pstr)


def match_str_w_givenrefmonthprefix(pdate, pstr):
  """
  This function is mainly for use in a filter()
  """
  return pdate == match_n_get_refmonthprefix_in_str(pstr)


def filterin_files_w_givenrefmonthprefix(refmonth: datetime.date, files: list[Path]):
  """
  The next function below is similar and has some explanation in its docstring
  """
  folderpaths_n_fns = [(p.parent, p.name) for p in files]
  folderpaths_n_fns = filter(lambda tpl_pth_n_fn: match_str_w_givenrefmonthprefix(refmonth, tpl_pth_n_fn[1]), folderpaths_n_fns)
  outfiles = [fp / fn for fp, fn in folderpaths_n_fns]
  return outfiles


def filterin_files_w_givendateprefix(pdate: datetime.date, files: list[Path]):
  """
  Filters in files that begins with the given date.

  Obs:
    Instead of trying a 'functional composition', code below used a 'zip' to the filter() function.
    @see code below.
    This is because the filtering is applied to filename not to filepath,
      and the 'zip' helps rejoin filepath (folder with filename) after filtering.
  """
  # files is list with filepaths (not filenames)
  # so let us create a zip (a tuple list having pairs (folder, filename))
  folderpaths_n_fns = [(p.parent, p.name) for p in files]
  folderpaths_n_fns = filter(lambda tpl_pth_n_fn: match_str_w_givendateprefix(pdate, tpl_pth_n_fn[1]), folderpaths_n_fns)
  # at this point, recompose 'files' with their pairs (folder, filename)
  outfiles = [fp / fn for fp, fn in folderpaths_n_fns]
  return outfiles

import art.finc.bnk.inst.bb.local_settings as ls
def adhoctest1():
  refmonth = rmfs.make_refmonth_or_current('2024-10')
  files = ffretr.gather_all_files_up_from(ls.BB_CC_EXTR_ANO_A_ANO_BASEFOLDER)
  ret_files = filterin_files_w_givenrefmonthprefix(refmonth, files)
  n_files = len(ret_files)
  scrmsg = f"Found {n_files} files | from {len(files)} files"
  print(scrmsg)
  for fp in ret_files:
    print(fp)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  adhoctest1()
  adhoctest2()
  """
  adhoctest1()
