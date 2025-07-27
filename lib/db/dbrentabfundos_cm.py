#!/usr/bin/env python3
# import datetime
# import hashlib
# import os
# import sqlite3
# import fs.hashfunctions.hash_mod as hm
import lib.db.dbbase_cm as dbb


class DBRentabFundos(dbb.DBBase):

  default_tablename = 'rentabfundos'

  def __init__(self, mount_abspath=None, inlocus_sqlite_filename=None, tablename=None):
    """
    mount_abspath is the dirpath where the sqlitefile resides
    """
    self.mountpath = mount_abspath
    if tablename is None:
      self.tablename = self.default_tablename
    super().__init__(mount_abspath, inlocus_sqlite_filename)

  def form_fields_line_for_createtable(self):
    """
    This method is to be implemented in child-inherited classes
      fieldnames_common = [
        'bancosigla', 'fundocod', 'name', 'monthref',
        'rendmes', 'rendnoano', 'rend12meses',
        'quantcotasmesanterior', 'quantcotasfimmes',
        'saldobrutomesanterior', 'saldobrutofimmes', 'rendliq', 'irrf'
      ]
    """
    middle_sql = """
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      bancosigla TEXT,
      fundocod TEXT,
      name TEXT,
      monthref NUMERIC,
      rendmes REAL,
      rendnoano REAL,
      rend12meses REAL,
      quantcotasmesanterior REAL,
      quantcotasfimmes REAL,
      saldobrutomesanterior REAL,
      saldobrutofimmes REAL,
      rendbase REAL,
      irrf REAL
    """
    return middle_sql

  def sqlite_createtable_if_not_exists(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    sql = self.interpolate_create_table_sql()
    cursor.execute(sql)
    # print(sql)
    # print('Created table', tablename)
    cursor.close()
    conn.close()

  def fetch_rec_if_hkey_exists_in_db(self, hkey):
    sql = 'select * from %(tablename)s WHERE hkey=?;' % {'tablename': self.tablename}
    tuplevalues = (hkey, )
    conn = self.get_connection()
    cursor = conn.cursor()
    fetch_result = cursor.execute(sql, tuplevalues)
    result_tuple_list = fetch_result.fetchall()
    cursor.close()
    conn.close()
    return result_tuple_list

  def form_update_with_all_fields_sql(self):
    """
    Notice that the interpolation %(tablename)s is not done here, it'll be done later on.
    """
    sql_before_interpol = '''
    UPDATE %(tablename)s 
      SET
        name=?, 
        parentpath=?, 
        is_present=?,
        sha1=?,
        bytesize=?, 
        mdatetime=? 
      WHERE
        hkey=?;
      '''
    return sql_before_interpol


def adhoc_select():
  db = DBRentabFundos()
  tuplelist = db.do_select_all()
  print(tuplelist)
  for row in tuplelist:
    _id = row[0]
    print('_id', _id)
    hkey = row[1]
    print('hkey', hkey)
    name = row[2]
    print('name', name)
    parentpath = row[3]
    print('parentpath', parentpath)
    is_file = row[4]
    print('is_file', bool(is_file))
    sha1 = row[5]
    print('sha1', sha1.hex())
    bytesize = row[6]
    print('bytesize', bytesize)
    mdatetime = row[7]
    print('mdatetime', mdatetime)


def adhoc_select_all():
  db = DBRentabFundos()
  result_tuple_list = db.do_select_all()
  for tuplerow in result_tuple_list:
    print(tuplerow)
  return result_tuple_list


def adhoc_delete_all_rows():
  db = DBRentabFundos()
  n_rows_before = db.count_rows()
  print('n_rows_before', n_rows_before)
  result_tuple_list = db.delete_all_rows()
  n_rows_after = db.count_rows()
  print('result_tuple_list', result_tuple_list)
  print('n_rows_after', n_rows_after)


def process():
  """
  adhoc_select()
  adhoc_delete_all_rows()
  adhoc_select_all()
  bool_res = adhoc_insert_some()
  print('was_inserted', bool_res)
  """
  adhoc_select_all()


if __name__ == '__main__':
  process()
