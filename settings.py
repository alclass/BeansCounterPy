#!/usr/bin/env python3
""""
scraper_monthly_rendextracts.py
  Organizes the month range and then calls extractFromWithinAFundoReport.py month to month
"""
import datetime
import os
try:
  import local_settings as locset
except ImportError:
  pass
MONTH_INI = datetime.date(year=2022, month=8, day=1)
MONTH_FIM = datetime.date(year=2023, month=8, day=1)
BB_FI_EXTRACTS_ROOT_FOLDERNAME = "FI Extratos Mensais Ano a Ano BB OD"  # conventioned: do not change it
BB_FI_EXTRACTS_FOLDERNAME_YEAR_INTERPOL = "{year} FI Extratos Mensais BB"  # conventioned: notice the str interpolation
BB_FI_EXTRACT_FILENAME_YEARMONTH_INTERPOL = '{year}-{month:02d} FI extrato BB.txt'  # also conventioned:yyyy/mm interpol
DEFAULT_DATADIR_FOLDERNAME = 'dados'  # this one is parameterized, a different one may be set in local_settings.py
APP_ROOTFOLDER = os.path.dirname(__file__)


def get_datadir_foldername_or_default():
  datadif_foldername = None
  try:
    datadif_foldername = locset.DATADIR_FOLDERNAME
  except ValueError:
    pass
  return datadif_foldername or DEFAULT_DATADIR_FOLDERNAME


def get_apps_data_abspath():
  DATADIR_FOLDERNAME = get_datadir_foldername_or_default()
  datapath = os.path.join(APP_ROOTFOLDER, DATADIR_FOLDERNAME)
  return datapath


def get_bb_fi_extracts_datafolder_abspath_by_year(year):
  apps_data_abspath = get_apps_data_abspath()
  bb_fi_rootfolder_abspath = os.path.join(apps_data_abspath, BB_FI_EXTRACTS_ROOT_FOLDERNAME)
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


def show_paths():
  datapath = get_apps_data_abspath()
  print('datapath =', datapath)
  year = 2023
  bb_fi_yearfolder_abspath = get_bb_fi_extracts_datafolder_abspath_by_year(year)
  print('bb_fi_yearfolder_abspath =', bb_fi_yearfolder_abspath)
  bb_fi_yearmonth_filepath = get_bb_fi_extract_filepath_by_year_month(2023, 4)
  print('bb_fi_yearmonth_filepath =', bb_fi_yearmonth_filepath)


if __name__ == '__main__':
  show_paths()
