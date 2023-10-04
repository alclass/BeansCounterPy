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
import scrapers.bbfi.scraper_monthly_rendextracts as scrpmonths
import fs.db.dbasfolder.discover_bbfi_datadirections as discbbfi


class Insertor:

  TABLENAME = 'bbfimonthlyresults'

  def __init__(self, refmonthdate_ini, refmonthdate_fim, sqlitefilepath=None):
    self.refmonthdate_ini = refmonthdate_ini
    self.refmonthdate_fim = refmonthdate_fim
    self.sqlitefilepath = sqlitefilepath
    self.treat_sqlitefilepath()
    self.roller = None

  def treat_sqlitefilepath(self):
    if self.sqlitefilepath is None or not os.path.isfile(self.sqlitefilepath):
      self.sqlitefilepath = sett.get_dbfi_sqlite_filepath()

  def get_connection(self):
    conn = sqlite3.connect(self.sqlitefilepath)
    return conn

  def create_db_if_not_exists(self):
    sqlcreatetable_to_interpol = """CREATE TABLE IF NOT EXISTS %(tablename)s (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      refmonthdate TEXT,
      name TEXT NOT NULL,
      cnpj TEXT,
      data_saldo_ant DATE NOT NULL,
      saldo_anterior FLOAT NOT NULL,
      qtd_cotas_anterior FLOAT,
      data_saldo_atu FLOAT NOT NULL,
      saldo_atual FLOAT NOT NULL,
      qtd_cotas_atual FLOAT,
      prct_rend_mes FLOAT NOT NULL,
      prct_rend_desdeano FLOAT NOT NULL,
      prct_rend_12meses FLOAT NOT NULL,
      aplicacoes FLOAT,
      resgates FLOAT,
      rend_bruto FLOAT NOT NULL,
      ir FLOAT,
      iof FLOAT,
      rend_liq FLOAT NOT NULL,
      UNIQUE(refmonthdate, name)
    );
    """
    sqlcreatetable = sqlcreatetable_to_interpol % {'tablename': self.TABLENAME}
    conn = self.get_connection()
    conn.cursor().execute(sqlcreatetable)
    conn.close()

  def do_insert(self, fundo_result_record):
    """
  (fieldnames up till this moment):
  fieldnames = [
    'refmonthdate', 'name', 'cnpj', 'data_saldo_ant', 'saldo_anterior',
    'qtd_cotas_anterior', 'data_saldo_atu', 'saldo_atual', 'qtd_cotas_atual', 'prct_rend_mes',
    'prct_rend_desdeano', 'prct_rend_12meses', 'aplicacoes',
    'resgates', 'rend_bruto', 'ir', 'iof', 'rend_liq'
  ]
    @see also script adhoctests/gen_attrs_from_class.py
    """
    sqlinsert_to_interpol = """
    INSERT OR IGNORE INTO %(tablename)s
      %(fieldnames)s VALUES %(sqlquestionmarks)s;
    """
    sqlfieldnames = str(list(fundo_result_record.keys()))
    sqlfieldnames = sqlfieldnames.replace('[', '').replace(']', '')
    sqlfieldnames = '(' + sqlfieldnames + ')'
    tuplevalues = tuple(fundo_result_record.values())
    sqlquestionmarks = '(' + '?,'*len(tuplevalues)
    sqlquestionmarks = sqlquestionmarks[:-1] + ')'
    sqlinsert = sqlinsert_to_interpol % {
      'tablename': self.TABLENAME,
      'fieldnames': sqlfieldnames,
      'sqlquestionmarks': sqlquestionmarks,
    }
    conn = self.get_connection()
    cursor = conn.cursor()
    retval = cursor.execute(sqlinsert, tuplevalues)
    print(retval, sqlinsert)
    if retval.rowcount == 1:
      print('rowcount', retval.rowcount, 'db-committed, closing connection')
      conn.commit()
    else:
      print('rowcount', retval.rowcount, 'NOT db-committed, closing connection')
    conn.close()

  def insert_daterange_records(self):
    self.create_db_if_not_exists()
    for fundo_result_record in self.roller.fundo_result_records:
      self.do_insert(fundo_result_record)

  def read_daterange_records(self):
    self.roller = scrpmonths.MonthlyRoller(
      yearmonth_ini=self.refmonthdate_ini,
      yearmonth_fim=self.refmonthdate_fim
    )
    self.roller.process()
    n_records = len(self.roller.fundo_result_records)
    print('Read %d read_daterange_records' % n_records)
    # roller has list [fundo_result_records] which contains the sought-for data

  def process(self):
    self.read_daterange_records()
    self.insert_daterange_records()


def process():
  dbfi_finder = discbbfi.get_dbfi_finder()
  insertor = Insertor(dbfi_finder.lesser_refmonthdate, dbfi_finder.greater_refmonthdate)
  insertor.process()


if __name__ == '__main__':
  process()
