#!/usr/bin/env python3
"""
art/maintenance/bbfidailyres_dirtree_create.py
  creates the directory structure for bb fi daily resuls with
  the leaf directory corresponding to current month's.

Example: suppose month is 2023-12: issuing the command

  $art/maintenance/bbfidailyres_dirtree_create.py
will make

{conf_base_folder}/001 BCB/Fi/2023-12

"""
import datetime

import settings as sett
import models.banks.bankpathfinder as bkfd
BANK3LETTER = 'bdb'


def adhoctest():
  bkfinder = bkfd.BankOSFolderFileFinder(bank3letter=BANK3LETTER)
  today = datetime.date.today()
  t = bkfinder.find_or_create_l1yyyyfolderpath_by_year_opt_substr(today.year)
  print(t)
  pass


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  pass
  """
  process()
  adhoctest()

