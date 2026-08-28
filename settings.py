#!/usr/bin/env python3
"""
settings.py
  Contains parameters for the app and also uses parametes from local_settings.py
   this latter which is not pushed to the upstream repo's.

Tip when needing to 'refresh' the compiled files cache:

To clean up Python's compiled cache via a bash command line:
  $find . -type d -name "__pycache__" -exec rm -r {} +

To find all .env's in the repo's directory tree:
  find . -name ".env"
  if in .gitignore (as they should be), you will not find them using git ls-files

from pathlib import PosixPath
import sys
"""
import os
from pathlib import Path
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
APP_ROOTFOLDER = Path(os.path.dirname(__file__))
APP_SQLITE_FILENAME = os.getenv("APP_SQLITE_FILENAME", 'beanscounterapp.sqlite')
DATADIR_FOLDERNAME = os.getenv("DATADIR_FOLDERNAME", 'dados')


def get_datadir_foldername_or_default() -> str:
  return DATADIR_FOLDERNAME


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
  print('testdata dir foldername =', datapath)


if __name__ == '__main__':
  show_paths()
