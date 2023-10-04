#!/usr/bin/env python3
"""
discover_bbfi_datadirections.py
  envolopes module lookup_monthrange_in_datafolder.py giving it BBFI's basefolder
"""
import settings as sett
import fs.db.dbasfolder.lookup_monthrange_in_datafolder as lookup


def get_bb_fi_basefolder():
  return sett.get_bb_fi_rootfolder_abspath()


def get_dbfi_finder():
  dbfi_finder = lookup.PrefixDateFinder(get_bb_fi_basefolder())
  dbfi_finder.process()
  return dbfi_finder


def process():
  dbfi_finder = get_dbfi_finder()
  print(dbfi_finder)


if __name__ == '__main__':
  """
  """
  process()
