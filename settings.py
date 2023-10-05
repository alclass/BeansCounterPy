#!/usr/bin/env python3
""""
scraper_monthly_rendextracts.py
  Organizes the month range and then calls extractFromWithinAFundoReport.py month to month
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
BBFI_SQLITE_FILENAME = 'bbfi.sqlite'  # this one is parameterized, a different one may be set in local_settings.py
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


def get_apps_bankdata_abspath():
  apps_data_abspath = get_apps_data_rootdir_abspath()
  bankdata_abspath = os.path.join(apps_data_abspath, SUBFOLDER_BANKDATA)
  return bankdata_abspath


def get_bb_fi_rootfolder_abspath():
  bankdata_abspath = get_apps_bankdata_abspath()
  bb_fi_rootfolder_abspath = os.path.join(bankdata_abspath, BB_FI_EXTRACTS_ROOT_FOLDERNAME)
  return bb_fi_rootfolder_abspath


def get_cef_fi_rootfolder_abspath():
  apps_bankdata_abspath = get_apps_bankdata_abspath()
  middlepath = 'CEF bankdata OD/FI Extratos Mensais Ano a Ano CEF OD/2023 FI extratos mensais CEF'
  cef_fi_dir_abspath = os.path.join(apps_bankdata_abspath, middlepath)
  return cef_fi_dir_abspath


def get_bb_fi_extracts_datafolder_abspath_by_year(year):
  bb_fi_rootfolder_abspath = get_bb_fi_rootfolder_abspath()
  bb_fi_yearfoldername = BB_FI_EXTRACTS_FOLDERNAME_YEAR_INTERPOL.format(year=year)
  bb_fi_yearfolder_abspath = os.path.join(bb_fi_rootfolder_abspath, bb_fi_yearfoldername)
  return bb_fi_yearfolder_abspath


def get_bb_fi_extract_filename_by_year_month(year, month):
  bb_fi_yearmonth_filename = BB_FI_EXTRACT_FILENAME_YEARMONTH_INTERPOL.format(year=year, month=month)
  return bb_fi_yearmonth_filename


def get_bb_fi_extract_filepath_by_year_month(year, month):
  bb_fi_yearmonth_filename = get_bb_fi_extract_filename_by_year_month(year, month)
  bb_fi_yearfolder_abspath = get_bb_fi_extracts_datafolder_abspath_by_year(year)
  bb_fi_yearmonth_filepath = os.path.join(bb_fi_yearfolder_abspath, bb_fi_yearmonth_filename)
  return bb_fi_yearmonth_filepath


def get_dbfi_sqlite_filepath():
  return os.path.join(get_apps_data_rootdir_abspath(), BBFI_SQLITE_FILENAME)


def show_paths():
  datapath = get_apps_data_rootdir_abspath()
  print('datapath =', datapath)
  year = 2023
  bb_fi_yearfolder_abspath = get_bb_fi_extracts_datafolder_abspath_by_year(year)
  print('bb_fi_yearfolder_abspath =', bb_fi_yearfolder_abspath)
  bb_fi_yearmonth_filepath = get_bb_fi_extract_filepath_by_year_month(2023, 4)
  print('bb_fi_yearmonth_filepath =', bb_fi_yearmonth_filepath)


if __name__ == '__main__':
  show_paths()
