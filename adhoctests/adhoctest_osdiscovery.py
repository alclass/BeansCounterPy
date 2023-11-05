#!/usr/bin/env python3
"""
adhoctests/adhoctest_osdiscovery.py
  organized the first sketches for the OS discovery class, before writing it.
fs/os/dirtree_dateprefixed2.py
"""
import datetime
import os.path
import fs.os.oshilofunctions as hilo
import fs.os.dateprefixed_dirtree_finder as fnd  # fnd.DatePrefixedOSFinder


def adhost1():
  bfp = (
    '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/001 BDB bankdata/'
    'FI Extratos Mensais Ano a Ano BB OD'
  )
  disc = fnd.DatePrefixedOSFinder(bfp)
  print(disc)
  l1folders = disc.find_l1yyyy_folderpaths_by_typ()
  for l1folder in l1folders:
    print('l1', l1folder)
  year = 2022
  l2folders = disc.find_l2yyyymm_folderpaths_any_months_by_year_typ(year)
  print('-' * 40)
  for l2folder in l2folders:
    print('l2folder', l2folder)
  if len(l2folders) == 0:
    print('no l2folders for year', year)
  month = 10
  l2files = disc.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month)
  print('-' * 40)
  for l2file in l2files:
    print('l2file', l2file)
  if len(l2files) == 0:
    print('no l2files for year', year)


def adhost2():
  """
    l1_folders = disc.find_l1yyyy_folderpaths_by_typ(year)
    print('l1', '-' * 40)
    print(year)
  """
  bfp = (
    '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
    '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/'
    'BB FI Rendimentos Diários htmls'
  )
  disc = fnd.DatePrefixedOSFinder(bfp)
  print(disc)
  l1folders = disc.find_l1yyyy_folderpaths_by_typ()
  for l1folder in l1folders:
    print('l1', l1folder)
  year = 2023
  for l2folder in l1folders:
    print('l2folder', l2folder)
  if len(l1folders) == 0:
    print('no l2folders for year', year)
  l2folders = disc.find_l2yyyymm_folderpaths_any_months_by_year_typ(year)
  print('l2', '-' * 40)
  for l2folder in l2folders:
    print('l2+folder', l2folder)
  if len(l2folders) == 0:
    print('no l2files for year', year)
  month = 10
  l3files = disc.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month)
  print('l3', '-' * 40)
  for l3file in l3files:
    print('l3file', l3file)
  if len(l3files) == 0:
    print('no l3files for year', year, 'month', month)
  ext = 'csv'
  l3files = disc.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month, dot_ext=ext)
  print('l3', ext,  '-' * 40)
  for l3file in l3files:
    print('l3file ext', ext, l3file)
  if len(l3files) == 0:
    print('no l3files for year', year, 'month', month, 'ext', ext)
  month = 11
  l3files = disc.find_l3yyyymm_filepaths_by_year_month_typ_ext(year, month, dot_ext=ext)
  print('l3', year, month, ext,  '-' * 40)
  for l3file in l3files:
    print('l3file ext', ext, l3file)
  if len(l3files) == 0:
    print('no l3files for year', year, 'month', month, 'ext', ext)


def process():
  pass


if __name__ == '__main__':
  adhost2()
