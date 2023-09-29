#!/usr/bin/env python3
# import datetime
# import hashlib
# import os
# import sqlite3
# import fs.hashfunctions.hash_mod as hm
import fs.db.dbbase_cm as dbb
import unittest


class DBRentabFundo(dbb.DBBase):

  FUNDONAME_DEFAULT = 'FIC_EXPERT'
  TABLENAME_DEFAULT = 'rentfundos'

  def __init__(self, name=None, tablename=None):
    self.name = name
    self.tablename = tablename
    super().__init__(name, tablename)
    self.treat_params()

  def fetch_tuplerentabfundo_from_name_n_monthref(self, name, monthref):
    """
    To implement
    """
    _ = self.name
    _ = name
    _ = monthref
    return True

  def treat_params(self):
    if self.name is None:
      self.name = self.FUNDONAME_DEFAULT
    if self.tablename is None:
      self.tablename = self.TABLENAME_DEFAULT

  def select_with_sql(self, sql):
    conn = self.get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(sql)
    rowlist = rows.fetch_all()
    cursor.close()
    conn.commit()
    conn.close()
    return rowlist

  def db_insert_via_tuplevalues(self, tuplevalues):
    question_marks = len(tuplevalues) * '?, '
    question_marks = question_marks.rstrip(', ')
    sql = 'INSERT into %(tablename)s VALUES (' + question_marks + ');'
    return self.db_insert_with_sql_n_tuplevalues(sql, tuplevalues)

  def db_insert_via_obj(self, rentfundo):
    tuplevalues = (
      None, rentfundo.name, rentfundo.name, rentfundo.monthref,
      rentfundo.month_rate, rentfundo.year_acc_rate, rentfundo.year_rate
    )
    return self.db_insert_via_tuplevalues(tuplevalues)


def process():
  """
  adhoc_select()
  adhoc_delete_all_rows()
  adhoc_select_all()
  bool_res = adhoc_insert_some()
  print('was_inserted', bool_res)
  """
  pass


if __name__ == '__main__':
  process()


class TestCaseBeansCounter(unittest.TestCase):

  def setUp(self):
    self.db = DBRentabFundo(None, 'testdb.sqlite')
    self.rentfundo = DBRentabFundo()

  def test1_rentabfundo(self):
    self.assertEqual('testdb.sqlite', self.db.sqlitefilename)
    self.assertEqual('testdb.sqlite', self.db.sqlitefilename)

  def test1_recinsert_rentabfundo(self):
    name = 'FIC_EXPERT'
    monthref = '2021-10-01'
    monthrate = 0.03
    yearaccrate = 0.13
    yearrate = 0.15
    tuplevalues = (None, name, monthref, monthrate, yearaccrate, yearrate)
    self.rentfundo.db_insert_via_tuplevalues(tuplevalues)
    resulttuple = self.rentfundo.fetch_tuplerentabfundo_from_name_n_monthref(name, monthref)
    expectedtuple = tuplevalues[1:]
    resulttuplewithoutid = resulttuple[1:]
    self.assertEqual(len(expectedtuple), len(resulttuplewithoutid))
    self.assertEqual(expectedtuple, resulttuplewithoutid)
