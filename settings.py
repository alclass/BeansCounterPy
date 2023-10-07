#!/usr/bin/env python3
""""
scrape_monthly_rendextracts.py
  Organizes the month range and then calls extractSpecificBBFundos.py month to month
"""
import os
import sys
import fs.os.osfunctions as osfs
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


class BANK:

  BANKDICT = {
    1: ('bdb', 'Banco do Brasil S.A.'),
    33: ('std', 'Banco Santander (Brasil) S.A.'),
    104: ('cef', 'Caixa Econômica Federal'),
    237: ('bra', 'Banco Bradesco S.A.'),
    341: ('ita', 'Banco Itaú S.A.'),
  }
  BANKDICT_BY_3LETTER = None  # it will "lazily" be init'd

  @classmethod
  def invert_dict(cls):
    if cls.BANKDICT_BY_3LETTER is not None:
      return
    cls.BANKDICT_BY_3LETTER = {}
    for banknumber in cls.BANKDICT:
      # banknumber is int
      code3letter, descr = cls.BANKDICT[banknumber]
      cls.BANKDICT_BY_3LETTER[code3letter] = (banknumber, descr)

  @classmethod
  def does_bank3letter_exist(cls, bank3letter=None):
    if bank3letter is None:
      return False
    banknumber = cls.get_banknumber_by_its3letter(bank3letter)
    if banknumber not in cls.BANKDICT.keys():
      return False
    return True

  @classmethod
  def get_bank3letter_by_number(cls, banknumber=None):
    if banknumber is None:
      return None
    try:
      code3letter, _ = cls.BANKDICT[banknumber]
      return code3letter
    except IndexError:
      return None

  @classmethod
  def get_banknumber_by_its3letter(cls, its3letter=None):
    if its3letter is None:
      return None
    if cls.BANKDICT_BY_3LETTER is None:
      cls.invert_dict()
    try:
      tupl = cls.BANKDICT_BY_3LETTER[its3letter]
      banknumber = tupl[0]
      return banknumber
    except IndexError:
      return None

  @classmethod
  def get_apps_bankdata_abspath(cls):
    apps_data_abspath = get_apps_data_rootdir_abspath()
    bankdata_abspath = os.path.join(apps_data_abspath, SUBFOLDER_BANKDATA)
    return bankdata_abspath

  @classmethod
  def get_bank_foldername_by_number(cls, banknumber_str_or_int=None):
    try:
      banknumber = int(banknumber_str_or_int)
    except (TypeError, ValueError):
      return None
    str_banknumber_prefix = str(banknumber).zfill(3) + ' '
    bankdatapath = cls.get_apps_bankdata_abspath()
    entries = os.listdir(bankdatapath)
    fullentries = [os.path.join(bankdatapath, e) for e in entries]
    dirfullentries = filter(lambda e: os.path.isdir(e), fullentries)
    direntries = [os.path.split(e)[-1] for e in dirfullentries]
    prefixed_direntries = list(filter(lambda e: e.startswith(str_banknumber_prefix), direntries))
    foldername = prefixed_direntries[0]
    return foldername

  @classmethod
  def get_bank_foldername_by_its3letter(cls, bank3letter):
    banknumber = cls.get_banknumber_by_its3letter(bank3letter)
    return cls.get_bank_foldername_by_number(banknumber)

  @classmethod
  def get_bank_folderpath_by_number(cls, banknumber_str_or_int=None):
    foldername = cls.get_bank_foldername_by_number(banknumber_str_or_int)
    if foldername is None:
      return None
    bankdata_abspath = cls.get_apps_bankdata_abspath()
    bank_rootfolderpath = os.path.join(bankdata_abspath, foldername)
    return bank_rootfolderpath

  @classmethod
  def get_bank_folderpath_by_its3letter(cls, bank3letter):
    banknumber = BANK.get_banknumber_by_its3letter(bank3letter)
    return cls.get_bank_folderpath_by_number(banknumber)

  @classmethod
  def get_bank_fi_folderpath_by_its3letter(cls, bank3letter):
    folderpath = cls.get_bank_folderpath_by_its3letter(bank3letter)
    entries = osfs.find_foldernames_from_path(folderpath)
    filtered = filter(lambda e: e.lower().startswith('fi '), entries)  # it's a convention!
    fi_foldername = list(filtered)[0]
    return os.path.join(folderpath, fi_foldername)


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
  bank3letter_sought = 'bdb'
  if bank3letter_sought is not None:
    banknumber = BANK.get_banknumber_by_its3letter(bank3letter_sought)
    bank_folderpath = BANK.get_bank_folderpath_by_number(banknumber)
    print('bank3letter_sought [', bank3letter_sought, '] bank_folderpath =', bank_folderpath)


if __name__ == '__main__':
  show_paths()
