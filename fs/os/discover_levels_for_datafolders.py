#!/usr/bin/env python3
"""
discover_levels_for_datafolders.py
"""
import os.path

import models.banks.banksgeneral
import settings as sett
import fs.os.osfunctions as osfs


class FolderYearMonthLevelDiscoverer:
  """
  On convention, there are two levels upon a "qualified" (*)  data folder
    1st level: the first level directory are prefixed with year + blank
    2nd level: the second level directory are prefixed with year + dash + 2-digit month + blank
  (*) "qualified" may be data by area or by place (example: data for a certain vendor or client)

  Examples:
    + data root folder
      + vendor_abc data directory
        + 2021 documents
          + 2021-11 conversations
        + 2023 documents
          + 2023-04 contracts
          + 2023-07 payments

  In the above example, "discoverer" will find:
    for vendor_abc, the directories:
      '2021-11 conversations', '2023-04 contracts', '2023-07 payments'
    Obs: the vendor_abc directory is passed on as a parameter.

  @see class methos below for details on how return data is organized
  """

  def __init__(self, rootfolderpath):
    self.rootfolderpath = rootfolderpath
    self.level1_qualified_foldernames = {}  # notice it's a dict with lists
    self.yeardict = None

  @property
  def total_files(self):
    foldernames = self.level1_qualified_foldernames.keys()
    _total_files = 0
    for foldername in foldernames:
      filenames = self.level1_qualified_foldernames[foldername]
      _total_files = len(filenames)
    return _total_files

  def fillin_yeardict(self):
    self.yeardict = {}
    for foldername in self.level1_qualified_foldernames:
      try:
        year = int(foldername[:4])
        self.yeardict[year] = foldername
      except (IndexError, ValueError):
        continue

  def get_foldername_by_year(self, year):
    if not self.yeardict:
      self.fillin_yeardict()
    try:
      return self.yeardict[year]
    except KeyError:
      pass
    return None

  def get_folderpath_by_year(self, year):
    foldername = self.get_foldername_by_year(year)
    if foldername is None:
      return None
    return os.path.join(self.rootfolderpath, foldername)

  def get_filename_by_yearmonth(self, year, month):
    foldername = self.get_foldername_by_year(year)
    if foldername is None:
      return None
    filenames = self.level1_qualified_foldernames[foldername]
    prefix_yeardashmonthblank = str(year) + '-' + str(month).zfill(2) + ' '
    filtered = list(filter(lambda e: e.startswith(prefix_yeardashmonthblank), filenames))
    if len(filtered) > 0:  # notice in the case that has not been treated of more than one year-month file
      filename = list(filtered)[0]
      return filename
    return None

  def get_filepath_by_yearmonth(self, year, month):
    filename = self.get_filename_by_yearmonth(year, month)
    if filename is None:
      return None
    folderpath = self.get_folderpath_by_year(year)
    if folderpath is None:
      return None
    return os.path.join(folderpath, filename)

  def find_1st_level(self):
    str_regexp = '^\d{4}\ '  # year blank
    foldernames = osfs.find_foldernames_with_regexp_on_path(str_regexp, self.rootfolderpath)
    for foldername in foldernames:
      self.level1_qualified_foldernames[foldername] = []

  def find_2nd_level(self):
    foldernames = self.level1_qualified_foldernames.keys()
    for foldername in foldernames:
      str_regexp = '^\d{4}\-\d{2}\ '  # year dash month blank
      folderpath = os.path.join(self.rootfolderpath, foldername)
      filenames = osfs.find_filenames_with_regexp_on_path(str_regexp, folderpath)
      if filenames:
        self.level1_qualified_foldernames[foldername] = filenames

  def process(self):
    self.find_1st_level()
    self.find_2nd_level()

  def __str__(self):
    outstr = "Folders & files found\n"
    outstr += "=====================\n\n"
    foldernames = self.level1_qualified_foldernames.keys()
    sorted(foldernames)
    seq_folder = 0
    for foldername in foldernames:
      seq_folder += 1
      outstr += "\t %d Foldername: %s\n" % (seq_folder, foldername)
      filenames = self.level1_qualified_foldernames[foldername]
      seq_filename = 0
      sorted(filenames)
      for filename in filenames:
        seq_filename += 1
        outstr += "\t\t%d filename: %s\n" % (seq_filename, filename)
    outstr += 'Total files = %d' % self.total_files
    return outstr


class FolderYearMonthLevelDiscovererForBankAndKind(FolderYearMonthLevelDiscoverer):
  """
  This inherited class just envelopes two attributes to the parent class. These are:
    1) bank3letter
    2) kind
  "kind" is not yet fully implemented, because the idea
     is to have different folders for different kinds
     (only one exists as of now, ie "fi" meaning "fundo de investimento" in Portuguese)
     Perhaps this trend or way may be changed for some other strategy.
  """

  def __init__(self, bank3letter, financkind=None):
    self.bank3letter = bank3letter
    self.financkind = financkind
    if self.financkind is None:
      self.financkind = 'fi'
    if self.financkind == 'fi':
      self.basefolderpath = models.banks.banksgeneral.BANK.get_bank_fi_folderpath_by_its3letter(self.bank3letter)
    else:
      error_msg = 'Bank kind %s is not yet implemented' % str(self.financkind)
      raise ValueError(error_msg)
    super().__init__(self.basefolderpath)
    super().process()

  def __str__(self):
    baseoutstr = super().__str__()
    outstr = "Bank: %s\n" % self.bank3letter
    outstr += "=====================\n"
    outstr += baseoutstr
    return outstr


def adhoctest():
  abank = 'cef'
  abank_fi_rootfolder_abspath = models.banks.banksgeneral.BANK.get_bank_fi_folderpath_by_its3letter(abank)
  discoverer = FolderYearMonthLevelDiscoverer(abank_fi_rootfolder_abspath)
  discoverer.process()
  print(discoverer)
  filepath = discoverer.get_filepath_by_yearmonth(2022, 9)
  print('filepath', filepath)
  abank = 'bdb'
  abank_fi_rootfolder_abspath = models.banks.banksgeneral.BANK.get_bank_fi_folderpath_by_its3letter(abank)
  discoverer = FolderYearMonthLevelDiscoverer(abank_fi_rootfolder_abspath)
  discoverer.process()
  print(discoverer)
  filepath = discoverer.get_filepath_by_yearmonth(2022, 9)
  print('filepath', filepath)
  discoverer = FolderYearMonthLevelDiscovererForBankAndKind(bank3letter=abank)
  print('discoverer', discoverer)


def process():
  adhoctest()


if __name__ == '__main__':
  """
  """
  process()
