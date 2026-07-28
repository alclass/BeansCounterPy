"""
lib/fncfs/indices/ipca/__init__.py

import lib.fncfs.indices.ipca as ipcapth  # ipcapth.get_ipca_datadir()
"""
from pathlib import Path
import settings as sett
IPCA_MIDPATH = 'indices/monthly_ipca'
YEARLY_JSON_FILENAME_INTERPOL = 'ipca-{year}.json'


def get_ipca_datadir() -> Path:
  """
  Gets data directory for monthly ipca indices

  p = get_ipca_datadir()
  print(p)
  """
  apps_data_rootpath = sett.get_apps_data_rootdir_abspath()
  ipca_dirpath = apps_data_rootpath / IPCA_MIDPATH
  return ipca_dirpath


def get_ipca_datadir_on_year(year: int) -> Path:
  """
  Gets data directory for monthly ipca indices

  p = get_ipca_datadir_on_year(2026)
  print(p)
  """
  yearpath = get_ipca_datadir() / str(year)
  return yearpath


def adhoctest1():
  """
  """
  year = 2026
  p = get_ipca_datadir_on_year(year)
  scrmsg = f"adhoctest get_ipca_datadir_on_year({year}) -> {p}"
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
