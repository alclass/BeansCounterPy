#!/usr/bin/env python3
"""
oshilofunctions.py
  extra functions in the 'os' area
  The 'hilo' (high & low) is just a sort of fancy name chosen for these extra functions
    also, it has nothing to do with the greek prefix in hilomorphism, an Aristotelian concept...
    also, it is not the 'hilo' word from Spanish which means thread et al.
"""
import datetime
import os
import re
str_yearplusblank_re = r'^\d{4}\ '
yearplusblank_re = re.compile(str_yearplusblank_re)
str_yeardashmonthplusblank_re = r'^\d{4}\-\d{2}\ '
yeardashmonthplusblank_re = re.compile(str_yeardashmonthplusblank_re)


def find_entries_that_start_with_a_yeardashmonth_via_re(entries):
  newentries = []
  for e in entries:
    if yeardashmonthplusblank_re.match(e):
      newentries.append(e)
  return newentries


def find_strinlist_that_starts_with_a_5charyearblank_via_if(entries):
  """
  recuperates year plus a blank
  """
  newentries = []
  if entries is None:
    return []
  for e in entries:
    try:
      _ = int(e[0:4])
      if e[4:5] != ' ':
        continue
      newentries.append(e)
    except (IndexError, ValueError):
      pass
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
  yearprefix_strlist = ["2018 FI Extratos Mensais", "2021 FI Extratos Mensais", "2023 FI Extratos Mensais"]
  year = 2021
  expected_str = find_a_yearprefixedstr_from_strlist_by_year(year, yearprefix_strlist)
  print('for', year, '=>', expected_str)
  year = 2022
  expected_str = find_a_yearprefixedstr_from_strlist_by_year(year, yearprefix_strlist)
  print('for', year, '=>', expected_str)
  year = 'bla'
  expected_str = find_a_yearprefixedstr_from_strlist_by_year(year, yearprefix_strlist)
  print('for', year, '=>', expected_str)
  yearmonthprefix_str = "2022-10 FI extrato.txt"
  pdate = extract_date_from_yearmonthprefix_str(yearmonthprefix_str)
  print('for', yearmonthprefix_str, '=>', pdate)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
