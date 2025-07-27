#!/usr/bin/env python3
"""
bankFoldersDiscover.py
  envolopes module lookup_monthrange_convention_from_basedatafolder_on.py giving it BBFI's basefolder
"""
import models.banks.banksgeneral
import lib.db.dbasfolder.lookup_monthrange_convention_from_basedatafolder_on as lookup
DEFAULT_BANK3LETTER = 'bdb'


class BankFoldersDiscover:
  def __init__(self, bank3letter=None):
    self._basefolderpath = None
    self._finder = None
    self.bank3letter = bank3letter
    if self.bank3letter is None:
      self.bank3letter = DEFAULT_BANK3LETTER

  @property
  def basefolderpath(self):
    if self._basefolderpath is None:
      self._basefolderpath = models.banks.banksgeneral.BANK.get_bank_fi_folderpath_by_its3letter(self.bank3letter)
    return self._basefolderpath

  @property
  def finder(self):
    if self._basefolderpath is None:
      self._finder = lookup.DatePrefixedOSEntriesFinder(self.basefolderpath)
    return self._finder


def adhoctest():
  folderdisc = BankFoldersDiscover()
  print(folderdisc.finder)


def process():
  pass


if __name__ == '__main__':
  """
  """
  process()
  adhoctest()
