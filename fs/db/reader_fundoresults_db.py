#!/usr/bin/env python3
"""
insert_triplerend_data_into_db.py
  reads data from (the extracts) text files and record them to db
"""
import settings as sett
import os.path
import sqlite3
# import unittest
# import defaults_mod as defm
# import scrapers.bbfi.scraper_monthly_rendextracts as scrpmonths
import fs.db.dbasfolder.discover_bbfi_datadirections as discbbfi


class DBReader:

  TABLENAME = 'bbfimonthlyresults'

  def __init__(self, refmonthdate_ini=None, refmonthdate_fim=None, sqlitefilepath=None):
    self.refmonthdate_ini = refmonthdate_ini
    self.refmonthdate_fim = refmonthdate_fim
    self.sqlitefilepath = sqlitefilepath
    self.treat_sqlitefilepath()
    self.roller = None
    self.fundoresults_dictlist = []
    self._total_dbrecords = None  # this will be filled by select count(*) lazily (ie upon first call)

  def treat_sqlitefilepath(self):
    if self.sqlitefilepath is None or not os.path.isfile(self.sqlitefilepath):
      self.sqlitefilepath = sett.get_dbfi_sqlite_filepath()

  @property
  def total_dbrecords(self):
    if self._total_dbrecords:
      return self._total_dbrecords
    sql = """
    SELECT count(*) from %(tablename)s; 
    """ % {'tablename': self.TABLENAME}
    conn = self.get_connection()
    cursor = conn.cursor()
    retval = cursor.execute(sql)
    if retval:
      row = retval.fetchone()
      try:
        celldatum = row[0]
        self._total_dbrecords = int(celldatum)
        return self._total_dbrecords
      except (IndexError, ValueError):
        pass
    conn.cursor()
    return 'not found'

  @property
  def total_read_records(self):
    """
    method process() or read_db_within_refmonthdates() must have been issued before
      to run the sql-read for filling in dictlist, in case db is not empty
    """
    return len(self.fundoresults_dictlist)

  def get_connection(self):
    conn = sqlite3.connect(self.sqlitefilepath)
    return conn

  def read_db_within_refmonthdates(self, refmonthdate_ini, refmonthdate_fim):
    sql = """
    SELECT * from %(tablename)s
      WHERE
        refmonthdate >= ? and 
        refmonthdate <= ?; 
    """ % {'tablename': self.TABLENAME}
    tuplevalues = (refmonthdate_ini, refmonthdate_fim)
    conn = self.get_connection()
    conn.row_factory = sqlite3.Row  # instantiating a row with dict() will result in a dict-row instead of tuple
    cursor = conn.cursor()
    rows = cursor.execute(sql, tuplevalues)
    for row in rows:
      pdict = dict(row)
      print(pdict)
      self.fundoresults_dictlist.append(pdict)
    conn.cursor()

  def read_db(self):
    sql = """
    SELECT * from %(tablename)s; 
    """ % {'tablename': self.TABLENAME}
    conn = self.get_connection()
    conn.row_factory = sqlite3.Row  # instantiating a row with dict() will result in a dict-row instead of tuple
    cursor = conn.cursor()
    rows = cursor.execute(sql)
    for row in rows:
      pdict = dict(row)
      print(pdict)
      self.fundoresults_dictlist.append(pdict)
    conn.cursor()

  def process(self):
    """
    when selecting a refmonthrange that is a subset, do not call this method (process)
    """
    self.read_db()

  def __str__(self):
    outstr = """
    refmonthdate_ini = {refmonthdate_ini}
    refmonthdate_fim = {refmonthdate_fim}
    sqlitefilepath = {sqlitefilepath}    
    n of records = {total_dbrecords}
    n of read records = {total_read_records} 
    """.format(
      refmonthdate_ini=self.refmonthdate_ini,
      refmonthdate_fim=self.refmonthdate_fim,
      sqlitefilepath=self.sqlitefilepath,
      total_dbrecords=self.total_dbrecords,
      total_read_records=self.total_read_records,
    )
    return outstr


def process():
  dbfi_finder = discbbfi.get_dbfi_finder()
  insertor = DBReader(dbfi_finder.lesser_refmonthdate, dbfi_finder.greater_refmonthdate)
  insertor.process()
  print(insertor)


if __name__ == '__main__':
  process()
