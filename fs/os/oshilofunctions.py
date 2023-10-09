#!/usr/bin/env python3
"""
oshilofunctions.py
  extra functions in the 'os' area
  The 'hilo' (high & low) is just a sort of fancy name chosen for these extra functions
    (also, it has nothing to do with the greek prefix in hilomorphism, an Aristotelian concept...)
"""
import os
import re
str_yearplusblank_re = r'^\d{4}\ '
yearplusblank_re = re.compile(str_yearplusblank_re)
str_yeardashmonthplusblank_re = r'^\d{4}\-\d{2}\ '
yeardashmonthplusblank_re = re.compile(str_yeardashmonthplusblank_re)


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


def adhoctest():
  pass


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
