import os

from fs.os import osfunctions as osfs
import fs.db.dbasfolder.lookup_monthrange_in_datafolder as lookup
import settings as sett


class BANK:

  SQL_TABLENAME = 'bankmonthlyfundos'
  BANK3LETTER_BDB = 'bdb'
  BANK3LETTER_CEF = 'cef'
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
  def is3letter_available(cls, bank3letter):
    banknumber = cls.get_banknumber_by_its3letter(bank3letter)
    if banknumber is None:
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
    apps_data_abspath = sett.get_apps_data_rootdir_abspath()
    bankdata_abspath = os.path.join(apps_data_abspath, sett.SUBFOLDER_BANKDATA)
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
  def get_bank_rootdirpath_by_number(cls, banknumber_str_or_int=None):
    foldername = cls.get_bank_foldername_by_number(banknumber_str_or_int)
    if foldername is None:
      return None
    bankdata_abspath = cls.get_apps_bankdata_abspath()
    bank_rootfolderpath = os.path.join(bankdata_abspath, foldername)
    return bank_rootfolderpath

  @classmethod
  def get_bank_rootdirname_by_number(cls, banknumber):
    """
    This is the same asget_bank_foldername_by_number(cls, banknumber_str_or_int=None)
      with a minor difference in the parameter signature
    """
    return cls.get_bank_foldername_by_number(banknumber)

  @classmethod
  def get_bank_rootdirpath_by_its3letter(cls, bank3letter):
    banknumber = BANK.get_banknumber_by_its3letter(bank3letter)
    return cls.get_bank_rootdirpath_by_number(banknumber)

  @classmethod
  def get_bank_foldername_by_its3letter(cls, bank3letter):
    banknumber = cls.get_banknumber_by_its3letter(bank3letter)
    return cls.get_bank_foldername_by_number(banknumber)

  @classmethod
  def get_bank_fi_folderpath_by_its3letter(cls, bank3letter):
    folderpath = cls.get_bank_rootdirpath_by_its3letter(bank3letter)
    entries = osfs.find_foldernames_from_path(folderpath)
    filtered = filter(lambda e: e.lower().startswith('fi '), entries)  # it's a convention!
    fi_foldername = list(filtered)[0]
    return os.path.join(folderpath, fi_foldername)

  @classmethod
  def get_pathentries_finderobj_by_bank3letter(cls, bank3letter):
    folderpath = cls.get_bank_rootdirpath_by_its3letter(bank3letter)
    return lookup.DatePrefixedOSEntriesFinder(folderpath)

  @classmethod
  def mount_text_list_available_banks(cls):
    """
    lists all bank registers here (*) available :: (*) here means "directery in this module or in settings.py"
    this method is almost a __str__(), name not chosen due to the class-methods in-here
    """
    outstr = "*** mount_text_list_available_banks ***\n"
    for banknumber in cls.BANKDICT:
      pdict = {
        'banknumber': banknumber,
        'bank3letter': cls.BANKDICT[banknumber][0],
        'bankdescr': cls.BANKDICT[banknumber][1],
      }

      line = '{banknumber} - {bank3letter} - {bankdescr}\n'.format(
        **pdict,
      )
      outstr += line
    return outstr


def adhoctest():
  """
  entries = finder.find_entries_that_start_with_a_yeardashmonth_via_if()
  print(entries)

  """
  bank3letter = 'bdb'
  banknumber = BANK.get_banknumber_by_its3letter(bank3letter)
  bank_folderpath = BANK.get_bank_rootdirpath_by_number(banknumber)
  print('bank3letter [', bank3letter, '] bank_folderpath =', bank_folderpath)
  s = BANK.mount_text_list_available_banks()
  print(s)
  folderpath = BANK.get_bank_fi_folderpath_by_its3letter(bank3letter)
  finder = lookup.DatePrefixedOSEntriesFinder(folderpath)
  print('refmonthdate_ini, refmonthdate_fim', finder.refmonthdate_ini, finder.refmonthdate_fim)


if __name__ == '__main__':
  """
  """
  adhoctest()
