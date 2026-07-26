#!/usr/bin/env python3
"""
settings.py
  Contains parameters for the app and also uses parametes from local_settings.py
   this latter which is not pushed to the upstream repo's.

Tip when needing to 'refresh' the compiled files cache:

To clean up Python's compiled cache via a bash command line:
  $find . -type d -name "__pycache__" -exec rm -r {} +

from pathlib import PosixPath
import sys
"""
import local_root_settings as rootsett
import os
from pathlib import Path
BB_FI_EXTRACTS_ROOT_FOLDERNAME = "FI Extratos Mensais Ano a Ano BB OD"  # conventioned: do not change it
BB_FI_EXTRACTS_FOLDERNAME_YEAR_INTERPOL = "{year} FI Extratos Mensais BB"  # conventioned: notice the str interpolation
BB_FI_EXTRACT_FILENAME_YEARMONTH_INTERPOL = '{year}-{month:02d} FI extrato BB.txt'  # also conventioned:yyyy/mm interpol
DEFAULT_DATADIR_FOLDERNAME = 'dados'  # this one is parameterized, a different one may be set in local_settings.py
SUBFOLDER_BANKDATA = 'bankdata'
# this one is parameterized, a different one may be set in local_settings.py
APP_SQLITE_FILENAME = 'beanscounterapp.sqlite'
APP_ROOTFOLDER = Path(os.path.dirname(__file__))


def get_datadir_foldername_or_default() -> str:
  return rootsett.DATADIR_FOLDERNAME or DEFAULT_DATADIR_FOLDERNAME


def get_apps_data_rootdir_abspath() -> Path:
  datadir_foldername = get_datadir_foldername_or_default()
  datapath = APP_ROOTFOLDER / datadir_foldername
  return datapath


def get_app_sqlite_filepath():
  return os.path.join(get_apps_data_rootdir_abspath(), APP_SQLITE_FILENAME)


def show_paths():
  datapath = get_apps_data_rootdir_abspath()
  print('rootdir =', datapath)
  datapath = get_datadir_foldername_or_default()
  print('data dir foldername =', datapath)


if __name__ == '__main__':
  show_paths()
