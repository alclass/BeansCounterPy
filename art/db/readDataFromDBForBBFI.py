#!/usr/bin/env python3
"""
readDataFromDBForBBFI.py
  reads data from SQL-DB.
  @see also art/db/insertBBFIDataFromFileToDB.py

"""
# import fs.db.dbasfolder.lookup_monthrange_in_datafolder as lkup  # for finding "conventioned" paths
# import fs.os.oshilofunctions as hilo  # for recuperating refmonth from str
import models.banks.banksgeneral as bkge  # for bootsrapping bank's fi's base folderpath (needed for lkup)
# import models.banks.bb.bbScraperWithFileText as bbScrp  # for the BBFI text scraper
# import models.banks.fundoAplicSql as fApSql  # inherited class for db-inserting
import fs.db.createtable_fundos as creatdb
import sqlite3
import settings as sett
import models.banks.fundoAplic as fAplic


def get_connection():
  sqlitefilepath = sett.get_app_sqlite_filepath()
  return sqlite3.connect(sqlitefilepath)


def create_fundos_sqlitedbtable_if_not_exists():
  dbcreator = creatdb.TableCreator()
  dbcreator.create_fundos_dbtable_if_not_exists()


class DataFromDBReader:

  def __init__(self, bank3letter):
    self.tablename = bkge.BANK.SQL_TABLENAME
    self.bank3letter = bank3letter
    self.bbfibasefolderpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(self.bank3letter)
    self.total_read_recs = 0
    self._total_fundos = 0
    self.total_inserted = 0
    self.fundos = []

  @property
  def total_fundos(self):
    return len(self.fundos)

  def sql_select_all(self):
    conn = get_connection()
    # line below turns on row fetched as dict
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sqlselectall = "SELECT * FROM {tablename};".format(tablename=self.tablename)
    fetch_obj = cursor.execute(sqlselectall)
    if fetch_obj:
      self.total_read_recs += 1
      for row in fetch_obj.fetchall():
        pdict = dict(row)
        fundo = fAplic.FundoAplic()
        fundo.load_from_dict(pdict)
        self.fundos.append(fundo)
    return

  def read_all(self):
    self.sql_select_all()

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
      total_read_files=self.total_read_recs,
      total_fundos=self.total_fundos,
      total_inserted=self.total_inserted,
    )
    return outstr


def adhoctest():
  pass


def process():
  bank3letter = 'bdb'
  reader = DataFromDBReader(bank3letter)
  reader.read_all()
  for fundo in reader.fundos:
    print(fundo)
  print(reader)


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
