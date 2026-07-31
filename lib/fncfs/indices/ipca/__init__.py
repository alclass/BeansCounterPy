"""
lib/fncfs/indices/ipca/__init__.py

import lib.fncfs.indices.ipca as ipcapth  # ipcapth.get_ipca_datadir()
"""
import os
from pathlib import Path
import settings as sett
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
# ================
# 1 os-name config-vars
# ================
IPCA_MIDPATH = os.getenv("IPCA_MIDPATH")
YEARLY_JSON_FILENAME_INTERPOL = os.getenv("YEARLY_JSON_FILENAME_INTERPOL")
# =============
# raise OSError exception if os.getenv() gets None
# =============
errmsg_interpol = "Error: please, fill in config-var [{configvar}] in .env in directory [{SCRIPT_DIR}]"
if IPCA_MIDPATH is None:
  configvar = "IPCA_MIDPATH"
  errmsg = errmsg_interpol.format(configvar=configvar, SCRIPT_DIR=SCRIPT_DIR)
  raise OSError(errmsg)
if YEARLY_JSON_FILENAME_INTERPOL is None:
  configvar = "YEARLY_JSON_FILENAME_INTERPOL"
  errmsg = errmsg_interpol.format(configvar=configvar, SCRIPT_DIR=SCRIPT_DIR)
  raise OSError(errmsg)


def get_ipca_datadir() -> Path:
  """
  Gets data directory for monthly ipca indices

  Notice that an exception is not raised if IPCA_MIDPATH does not exist.
  Caller may create it later on and, then, if so, raise an exception.

  p = get_ipca_datadir()
  print(p)
  """
  apps_data_rootpath = sett.get_apps_data_rootdir_abspath()
  ipca_dirpath = apps_data_rootpath / str(IPCA_MIDPATH)
  return ipca_dirpath


def depr_get_ipca_datadir_on_year(year: int) -> Path:
  """
  DEPRECATED
  (This function is correct and works, but ipca dir does not exist anywore per year.)
  Gets data directory for monthly ipca indices.

  p = get_ipca_datadir_on_year(2026)
  print(p)
  """
  yearpath = get_ipca_datadir() / str(year)
  return yearpath


def adhoctest1():
  """
  """
  year = 2026
  p = depr_get_ipca_datadir_on_year(year)
  scrmsg = (f"adhoctest (deprecated because ipca's are not per year anymore)"
            f" depr_get_ipca_datadir_on_year({year}) -> {p}")
  print(scrmsg)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
