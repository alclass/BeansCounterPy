#!/usr/bin/env python3
"""
The context to be solved here is to extract data from xml that has been converted original from pdf

  A refpage for XML parsing in Python
  https://www.geeksforgeeks.org/xml-parsing-python/
"""
import models.banks.fundoAplic as fAplic
import models.banks.banksgeneral as bkge
import sqlite3
import settings as sett


def get_connection():
  sqlitefilepath = sett.get_app_sqlite_filepath()
  return sqlite3.connect(sqlitefilepath)


class FundoAplicSql(fAplic.FundoAplic):

  def __init__(self, tablename=None):
    self.tablename = tablename
    self.treat_tablename()
    self.total_read = 0
    super().__init__()

  def treat_tablename(self):
    if self.tablename is None:
      self.tablename = bkge.BANK.SQL_TABLENAME

  @property
  def str_questionmarks(self):
    qtd = len(self.attrs())
    str_qm = '(' + '?,' * qtd
    str_qm = str_qm[:-1] + ')'
    return str_qm

  @property
  def sql_insert_commandtext(self):
    sqlins = "INSERT OR IGNORE INTO {tablename} {fieldnames} VALUES {str_questionmarks};".format(
        tablename=self.tablename,
        fieldnames=self.fieldnames_w_parentheses_for_sqlins,
        str_questionmarks=self.str_questionmarks,
    )
    return sqlins

  @property
  def fieldnames_w_parentheses_for_sqlins(self):
    """
    Usage:
      one possible "outside" use of this method is to get data for sqlite cursor.execute() second tuple parameter
      (same as tuplevalues below)
    """
    fields = self.attrs()
    _sql_fieldnames = '('
    for fieldname in fields:
      _sql_fieldnames += '"' + fieldname + '",'
    _sql_fieldnames = _sql_fieldnames[:-1] + ')'
    return _sql_fieldnames

  @property
  def tuplevalues(self):
    """
    Usage:
      one possible "outside" use of this method is to get data for sqlite cursor.execute() second tuple parameter
      (same as fieldnames above)
    """
    fields = self.attrs()
    outlist = []
    for fieldname in fields:
      value = eval('self.' + fieldname)
      outlist.append(value)
    return tuple(outlist)

  def insert(self):
    was_inserted = False
    conn = get_connection()
    cursor = conn.cursor()
    retval = cursor.execute(self.sql_insert_commandtext, self.tuplevalues)
    print('In insert() retval =', str(retval), self.sql_insert_commandtext)
    if retval.rowcount == 1:
      print('rowcount', retval.rowcount, 'db-committed, closing connection')
      conn.commit()
      was_inserted = True
    else:
      print('rowcount', retval.rowcount, 'NOT db-committed, closing connection')
    conn.close()
    return was_inserted


def adhoctest():
  """
  sql = dbfundo.sql_insert_commandtext
  print(sql)
  """
  dbfundo = FundoAplicSql()
  dbfundo.sql_select_all()


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
