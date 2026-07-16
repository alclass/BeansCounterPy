#!/usr/bin/env python3
"""
lib/osfs/discoverers/dateprefixdisconverers/dateprefix_filefind.py
  Contains monthly and refmonthly date functions.

"""
import lib.osfs.discoverers.dateprefixdisconverers.dateprefix_filefind as prfx  # .DatePrefixedOSFinder


import art.lojas.merclivr as init  # init.BASEFOLDERPATH
def adhoctest1():
  rootfolder = init.BASEFOLDERPATH
  finder = prfx.DatePrefixedOSFinder(rootdir=rootfolder)
  print(finder)
  strdate = '2025-02-01'
  files = finder.get_files_on_date(strdate)
  scrmsg = f"finder.get_files_on_date('{strdate}')"
  print(scrmsg)
  for i, fp in enumerate(files):
    print(i+1, '->', fp)
  refmonth = '2024-11'
  files = finder.get_files_on_refmonth(refmonth)
  scrmsg = f"finder.get_files_on_refmonth('{refmonth}')"
  print(scrmsg)
  for i, fp in enumerate(files):
    print(i+1, '->', fp)


def process():
  """
  This module contains library functions
  """
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
