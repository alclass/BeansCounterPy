#!/usr/bin/env python3
"""
createtable_fundos.py
  creates the fundos table if it does not exist.

Obs:
  The sql command here is still manually produced.
  We hope someday to somehow make it "dynamical", ie, capable of introspecting the data class
    and autogenerate the sql CREATE TABLE command text.
"""
# import unittest
import settings as sett
import os.path
import sqlite3
import models.banks.banksgeneral as bkge


class TableCreator:

  def __init__(self, sqlitefilepath=None, tablename=None):
    self.sqlitefilepath = sqlitefilepath
    self.tablename = tablename
    self.retval = None  # a str repr of the return value (retval) from cursor.execute()
    self.treat_sqlitefilepath_n_tablename()

  def treat_sqlitefilepath_n_tablename(self):
    if self.sqlitefilepath is None or not os.path.isfile(self.sqlitefilepath):
      # the one defined in settings.py
      self.sqlitefilepath = sett.get_app_sqlite_filepath()
    if self.tablename is None or not os.path.isfile(self.tablename):
      # the one defined in static/classmethod class BANK
      self.tablename = bkge.BANK.SQL_TABLENAME

  def get_connection(self):
    conn = sqlite3.connect(self.sqlitefilepath)
    return conn

  def create_fundos_dbtable_if_not_exists(self):
    """
    @see also module's __doc__ string above
    """
    sqlcreatetable_to_interpol = """
      CREATE TABLE IF NOT EXISTS %(tablename)s (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bank3letter CHAR(3) NOT NULL,
        refmonthdate DATE NOT NULL,
        name TEXT NOT NULL,
        cnpj TEXT,
        data_saldo_ant DATE,
        saldo_anterior FLOAT,
        qtd_cotas_ant FLOAT,
        valor_cota_ant FLOAT,
        data_saldo_atu DATE,
        saldo_atual FLOAT,
        qtd_cotas_atu FLOAT,
        valor_cota_atu FLOAT,
        prct_rend_mes FLOAT NOT NULL,
        prct_rend_desdeano FLOAT NOT NULL,
        prct_rend_12meses FLOAT NOT NULL,
        ir FLOAT,
        iof FLOAT,
        aplicacoes FLOAT,
        resgates FLOAT,
        resg_bru_em_trans FLOAT,
        rendimento_bruto FLOAT,
        rendimento_liq FLOAT,
        rendimento_base FLOAT,
      UNIQUE(bank3letter, name, refmonthdate)
    );
    """
    sqlcreatetable = sqlcreatetable_to_interpol % {'tablename': self.tablename}
    conn = self.get_connection()
    cursor = conn.cursor()
    retval = cursor.execute(sqlcreatetable)
    if retval:
      self.retval = str(retval)
      print(retval)
    conn.close()

  def __str__(self):
    outstr = """<TableCreator tablename={tablename}>
    sqlitefilepath = {sqlitefilepath}
    sqlite retval = {retval}
    """.format(tablename=self.tablename, sqlitefilepath=self.sqlitefilepath, retval=self.retval)
    return outstr


def process():
  tablecreator = TableCreator()
  tablecreator.create_fundos_dbtable_if_not_exists()
  print(tablecreator)


if __name__ == '__main__':
  process()
