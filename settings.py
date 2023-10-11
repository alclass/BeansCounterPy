#!/usr/bin/env python3
""""
scrape_monthly_rendextracts.py
  Organizes the month range and then calls bbScraperWithFileText.py month to month
"""
import os
import sys


try:
  import local_settings as locset
except ImportError:
  print('Please, create configuration file local_setting.py and rerun.')
  sys.exit(1)
BB_FI_EXTRACTS_ROOT_FOLDERNAME = "FI Extratos Mensais Ano a Ano BB OD"  # conventioned: do not change it
BB_FI_EXTRACTS_FOLDERNAME_YEAR_INTERPOL = "{year} FI Extratos Mensais BB"  # conventioned: notice the str interpolation
BB_FI_EXTRACT_FILENAME_YEARMONTH_INTERPOL = '{year}-{month:02d} FI extrato BB.txt'  # also conventioned:yyyy/mm interpol
DEFAULT_DATADIR_FOLDERNAME = 'dados'  # this one is parameterized, a different one may be set in local_settings.py
SUBFOLDER_BANKDATA = 'bankdata'
# this one is parameterized, a different one may be set in local_settings.py
APP_SQLITE_FILENAME = 'beanscounterapp.sqlite'
APP_ROOTFOLDER = os.path.dirname(__file__)


def get_datadir_foldername_or_default():
  datadir_foldername = None
  try:
    datadir_foldername = locset.DATADIR_FOLDERNAME
  except ValueError:
    pass
  return datadir_foldername or DEFAULT_DATADIR_FOLDERNAME


def get_apps_data_rootdir_abspath():
  datadir_foldername = get_datadir_foldername_or_default()
  datapath = os.path.join(APP_ROOTFOLDER, datadir_foldername)
  return datapath


def get_app_sqlite_filepath():
  return os.path.join(get_apps_data_rootdir_abspath(), APP_SQLITE_FILENAME)


def show_paths():
  datapath = get_apps_data_rootdir_abspath()
  print('datapath =', datapath)


if __name__ == '__main__':
  show_paths()
