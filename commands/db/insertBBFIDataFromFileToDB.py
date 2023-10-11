#!/usr/bin/env python3
"""
insertBBFIDataFromFileToDB.py
  loads the whole available data in files, or a subset of it, to a SQL-DB.

  Obs: At this time, it looks up all available files and not a subset.
"""
import os
import fs.db.dbasfolder.lookup_monthrange_in_datafolder as lkup  # for finding "conventioned" paths
import fs.os.oshilofunctions as hilo  # for recuperating refmonth from str
import models.banks.banksgeneral as bkge  # for bootsrapping bank's fi's base folderpath (needed for lkup)
import models.banks.bb.bbScraperWithFileText as bbScrp  # for the BBFI text scraper
import models.banks.fundoAplicSql as fApSql  # inherited class for db-inserting
import fs.db.createtable_fundos as creatdb


def create_fundos_sqlitedbtable_if_not_exists():
  dbcreator = creatdb.TableCreator()
  dbcreator.create_fundos_dbtable_if_not_exists()


class DataLFromFilesToDBLoader:

  def __init__(self, bank3letter):
    self.bank3letter = bank3letter
    self.bbfibasefolderpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(self.bank3letter)
    self.total_read_files = 0
    self.total_fundos = 0
    self.total_inserted = 0
    self.finder = lkup.DatePrefixedOSEntriesFinder(self.bbfibasefolderpath)
    create_fundos_sqlitedbtable_if_not_exists()

  def get_fundo_files_data_by_filepath(self, filepath, refmonthdate=None):
    scrapetext = open(filepath, encoding='latin1').read()
    self.total_read_files += 1
    fundo = bbScrp.BBExtractScraperWithFileText(scrapetext, refmonthdate)
    fundo.bank3letter = self.bank3letter  # notice the 'coupling' of bank is outside scraping
    return fundo

  def extract_individual_fundo_with_filepath_n_insert_it(self, filepath, refmonthdate):
    fundo = self.get_fundo_files_data_by_filepath(filepath, refmonthdate)
    if fundo.refmonthdate:
      self.total_fundos += 1
      fundosql = fApSql.FundoAplicSql()
      fundosql.transpose_from(fundo)
      boolval = fundosql.insert()
      if boolval:
        self.total_inserted += 1

  def loop_thru_available_files(self):
    for i, filepath in enumerate(self.finder.gen_filepaths_within_daterange_or_wholeinterval()):
      filename = os.path.split(filepath)[-1]
      print(i+1, 'processing [', filename, ']')
      refmonthdate = hilo.derive_refmonthdate_from_a_yearmonthprefixedstr(filename)
      self.extract_individual_fundo_with_filepath_n_insert_it(filepath, refmonthdate)

  def read_datafiles_n_dbinsert(self):
    self.loop_thru_available_files()

  def __str__(self):
    outstr = """
    bank3letter = {bank3letter}
    bbfibasefolderpath = {bbfibasefolderpath} 
    total_read_files = {total_read_files}
    total_fundos = {total_fundos}
    total_inserted = {total_inserted}
    """.format(
      bank3letter=self.bank3letter,
      bbfibasefolderpath=self.bbfibasefolderpath,
      total_read_files=self.total_read_files,
      total_fundos=self.total_fundos,
      total_inserted=self.total_inserted,
    )
    return outstr


def adhoctest():
  pass


def process():
  bank3letter = 'bdb'
  insertor = DataLFromFilesToDBLoader(bank3letter)
  insertor.read_datafiles_n_dbinsert()
  print(insertor)


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
