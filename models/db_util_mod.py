#!/usr/bin/env python3
"""
db_util_mod.py

Schema
table accrecords
----------------
id | accname | vdate | netvalue | value

table variations
----------------
id | accname | obsdate

table rentabfundos
----------------
id | name | monthref | month_rate | year_acc_rate | year_rate




"""
import os.path
import sqlite3
import unittest


mountpath = None
sqlitefilename = '.beans_counter.sqlite'
maintablename = 'accounts'


class DB:

  def __init__(self, mountpath=None, sqlitefilename=None, maintablename=None):
    self.mountpath = mountpath
    self.sqlitefilename = sqlitefilename
    self.maintablename = maintablename

  @property
  def sqlitefilepath(self):
    return os.path.join(self.mountpath, self.sqlitefilename)

  def get_connection(self):
    return sqlite3.connect(self.sqlitefilepath)

  def db_select_with_sql_n_tuplevalues(self, sql, tuplevalues):
    conn = self.get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(sql, tuplevalues)
    rowlist = rows.fetch_all()
    cursor.close()
    conn.commit()
    conn.close()
    return rowlist

  def db_create_table_rentabfundos(self):
    '''
    id | name | monthref | monthrate | yearaccrate | yearrate

    '''
    sql = '''
    CREATE TABLE IF NOT EXISTS rentabfundos (
      id INTEGER PRIMARY KEY AUTO INCREMENT,
      name TEXT,
      monthref DATE,
      monthrate DECIMAL,
      yearaccrate DECIMAL,
      yearrate DECIMAL
    )
    '''

  def db_insert_with_sql_n_tuplevalues(self, sql, tuplevalues):
    conn = self.get_connection()
    cursor = conn.cursor()
    res = cursor.execute(sql, tuplevalues)
    cursor.close()
    conn.commit()
    conn.close()
    return res


class DBRentabFundo:

  FUNDONAME_DEFAULT = 'FIC_EXPERT'
  TABLENAME_DEFAULT = 'rentfundos'

  def __init__(self, name=None, tablename=None):
    self.name = name
    self.tablename = tablename
    self.db = DB()
    self.treat_params()

  def treat_params(self):
    if self.name is None:
      self.name = self.FUNDONAME_DEFAULT
    if self.tablename is None:
      self.tablename = self.TABLENAME_DEFAULT

  def select_with_sql(self, sql):
    conn = self.db.get_connection()
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
    return self.db.db_insert_with_sql_n_tuplevalues(sql, tuplevalues)

  def db_insert_via_obj(self, rentfundo):
    tuplevalues = (
      None, rentfundo.name, rentfundo.name, rentfundo.monthref,
      rentfundo.month_rate, rentfundo.year_acc_rate, rentfundo.year_rate
    )
    return self.db_insert_via_tuplevalues(tuplevalues)


class TestCaseBeansCounter(unittest.TestCase):

  def setUp(self):
    self.db = DB(None, sqlitefilename='testdb.sqlite')
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
    self.rentfundo.db_insert(tuplevalues)
    resulttuple = self.rentfundo.fetch_tuplerentabfundo_from_name_n_monthref(name, monthref)
    expectedtuple = tuplevalues[1:]
    resulttuplewithoutid = resulttuple[1:]
    self.assertEqual(len(expectedtuple), len(resulttuplewithoutid))
    self.assertEqual(expectedtuple, resulttuplewithoutid)




