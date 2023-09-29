#!/usr/bin/env python3
"""
dbbase_cm.py

Schema
table accrecords
----------------
id | accname | vdate | netvalue | value

table variations
----------------
id | accname | obsdate

table rentabfundos
----------------
0 id 1 codename 2 name 3 monthref 4 rendmes 5 rendnoano 6 rend12meses
7 saldobrutofimmes 8 saldobrutomesanterior
9 quantcotafimmes 10 quantcotamesanterior
11 rendliq 12 irrf
"""
import os.path
import sqlite3
# import unittest
# import defaults_mod as defm


maintablename = 'accounts'
fieldnames = [
   'id', 'codename', 'name', 'monthref', 'rendmes', 'rendnoano', 'rend12meses',
   'saldobrutofimmes', 'saldobrutomesanterior', 'quantcotafimmes', 'quantcotamesanterior',
   'rendliq', 'irrf'
]


class Default:
  mountpath = ''
  sqlitefilename = 'personal_finance_accounting_beans_counter.sqlite'
  # sqlitefilename = '.beans_counter.sqlite'
  tablename = 'fundos'
  limit = 50
  offset = 50


class DBBase:

  def __init__(self, mountpath=None, sqlitefilename=None, tablename=None):
    self.mountpath = mountpath
    self.sqlitefilename = sqlitefilename
    self.tablename = tablename
    self.treat_init_params()

  @property
  def fieldnames(self):
    """
        id | name | monthref | monthrate | yearaccrate | yearrate
    """
    _fieldnames = ['id', 'name', 'monthref', 'monthrate', 'yearaccrate', 'yearrate']
    return _fieldnames

  def treat_init_params(self):
    if self.mountpath is None or not os.path.isdir(self.mountpath):
      self.mountpath = Default.mountpath
      if not os.path.isdir(self.mountpath):
        error_msg = 'mountpath directory that contains sqlitefile does not exist (%s)' % self.mountpath
        raise OSError(error_msg)
    if self.sqlitefilename is None or not os.path.isdir(self.sqlitefilename):
      self.sqlitefilename = Default.sqlitefilename
    if self.tablename is None:
      self.tablename = Default.tablename

  @property
  def sqlitefilepath(self):
    return os.path.join(self.mountpath, self.sqlitefilename)

  def get_connection(self):
    return sqlite3.connect(self.sqlitefilepath)

  def db_select_with_sql_n_tuplevalues(self, sql, tuplevalues):
    conn = self.get_connection()
    cursor = conn.cursor()
    fetched_list = cursor.execute(sql, tuplevalues)
    cursor.close()
    conn.commit()
    conn.close()
    return fetched_list

  def db_create_table_rentabfundos(self):
    """
    id | name | monthref | monthrate | yearaccrate | yearrate
    """
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
    conn = self.get_connection()
    result = conn.execute(sql)
    return result

  def db_insert_with_sql_n_tuplevalues(self, sql, tuplevalues):
    conn = self.get_connection()
    cursor = conn.cursor()
    res = cursor.execute(sql, tuplevalues)
    cursor.close()
    conn.commit()
    conn.close()
    return res

  def form_fields_line_for_createtable(self):
    """
    This method is to be implemented in child-inherited classes
    """
    return " tablename " + self.tablename

  def interpolate_create_table_sql(self):
    sql = 'CREATE TABLE IF NOT EXISTS "%(tablename)s" (' % {'tablename': self.tablename}
    sql += self.form_fields_line_for_createtable()
    sql += ')'
    return sql

  def get_n_fields(self):
    """
    This method depends on the interpolate_create_table_sql() method
    to be implemented in child-inherited classes because from it this method will derive n_fields
    """
    middle_sql = self.form_fields_line_for_createtable()
    middle_sql = middle_sql.lstrip('\n').rstrip(' \n')
    return len(middle_sql.split('\n'))

  def sqlite_createtable_if_not_exists(self):
    sql = self.interpolate_create_table_sql()
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    # print(sql)
    # print('Created table', tablename)
    cursor.close()
    conn.close()

  def delete_rows_not_existing_on_dirtree(self, mountpath):
    plimit = 50
    offset = 0
    ids = []
    rowsgenerator = self.do_select_all_w_limit_n_offset(plimit, offset)
    for rows in rowsgenerator:
      for row in rows:
        name = row[2]
        parentpath = row[3]
        middlepath = os.path.join(parentpath, name)
        if middlepath.startswith('/'):
          middlepath = middlepath.lstrip('/')
        fpath = os.path.join(mountpath, middlepath)
        if not os.path.isfile(fpath):
          ids.append(row[0])
    print('Deleting', ids)
    conn = self.get_connection()
    cursor = conn.cursor()
    for _id in ids:
      sql = 'delete from %(tablename)s where id=?;' % {'tablename': self.tablename}
      tuplevalues = (_id, )
      cursor.execute(sql, tuplevalues)
    conn.commit()
    cursor.close()
    conn.close()
    print('Deleted/Committed', len(ids), 'records')

  def delete_all_rows(self):
    sql = 'DELETE FROM %(tablename)s;' % {'tablename': self.tablename}
    conn = self.get_connection()
    cursor = conn.cursor()
    fetch_result = cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    return fetch_result

  def delete_row_by_id(self, _id):
    sql = 'DELETE FROM %(tablename)s WHERE id=?;' % {'tablename': self.tablename}
    tuplevalues = (_id, )
    conn = self.get_connection()
    cursor = conn.cursor()
    dbdel_result = cursor.execute(sql, tuplevalues)
    conn.commit()
    cursor.close()
    conn.close()
    return dbdel_result

  def delete_row_with_params(self, sql, tuplevalues):
    sql = sql % {'tablename': self.tablename}
    conn = self.get_connection()
    cursor = conn.cursor()
    dbdel_result = cursor.execute(sql, tuplevalues)
    conn.commit()
    cursor.close()
    conn.close()
    return dbdel_result

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

  def count_rows(self):
    sql = 'select count(*) from %(tablename)s;' % {'tablename': self.tablename}
    conn = self.get_connection()
    cursor = conn.cursor()
    fetch_result = cursor.execute(sql)
    result_tuple_list = fetch_result.fetchall()
    cursor.close()
    conn.close()
    return result_tuple_list

  def count_rows_as_int(self):
    rows = self.count_rows()
    if len(rows) > 0:
      row = rows[0]
      try:
        n_rows = int(row[0])
        return n_rows
      except ValueError:
        pass
    return 0

  def do_select_sql_n_tuplevalues_w_limit_n_offset(self, sql, tuplevalues=None, plimit=None, poffset=None):
    limit = plimit
    if limit is None:
      limit = Default.limit
    else:
      limit = int(limit)
    offset = poffset
    if offset is None:
      offset = Default.offset
    else:
      offset = int(offset)
    conn = self.get_connection()
    cursor = conn.cursor()
    sql = sql % {'tablename': self.tablename, 'limit': limit, 'offset': offset}
    while 1:  # up until n_fetched < limit
      if tuplevalues and type(tuplevalues) == tuple:
        fetch_result = cursor.execute(sql, tuplevalues)
      else:
        fetch_result = cursor.execute(sql)
      result_tuple_list = fetch_result.fetchall()
      n_fetched = len(result_tuple_list)
      yield result_tuple_list  # this method fetches chunks of "limit" records each time
      if n_fetched < limit:
        # break out of "infinite" loop
        break
      offset += limit
      sql = sql % {'tablename': self.tablename, 'limit': limit, 'offset': offset}
    cursor.close()
    conn.close()
    return None  # the statement "yield" above returns each chunk of data limit/offset by limit/offset

  def do_select_all_w_limit_n_offset(self, plimit=None, poffset=None):
    """
    This method fetches chunks of "limit" records each time.
    This saves memory and avoids a situation when a large db might take hold of the whole
      and eventually crash the script.

    IMPORTANT: this method cannot be used when record-deletions will occur along the way,
       because the limit/offset will skip ahead the same amount of deleted records,
       those not entering the underlying verifying in code
    """
    limit = plimit
    if limit is None:
      limit = Default.limit
    else:
      limit = int(limit)
    offset = poffset
    if offset is None:
      offset = Default.offset
    else:
      offset = int(offset)
    sql = 'SELECT * FROM %(tablename)s LIMIT %(limit)d OFFSET %(offset)d ;' \
          % {'tablename': self.tablename, 'limit': limit, 'offset': offset}
    conn = self.get_connection()
    cursor = conn.cursor()
    while 1:  # up until n_fetched < limit
      fetch_result = cursor.execute(sql)
      result_tuple_list = fetch_result.fetchall()
      n_fetched = len(result_tuple_list)
      yield result_tuple_list  # this method fetches chunks of "limit" records each time
      if n_fetched < limit:
        # break out of "infinite" loop
        break
      offset += limit
      sql = 'select * from %(tablename)s LIMIT %(limit)d OFFSET %(offset)d ;' \
            % {'tablename': self.tablename, 'limit': limit, 'offset': offset}
    cursor.close()
    conn.close()
    return None  # the statement "yield" above returns each chunk of data limit/offset by limit/offset

  def do_select_all(self):
    sql = 'select * from %(tablename)s;' % {'tablename': self.tablename}
    conn = self.get_connection()
    cursor = conn.cursor()
    fetch_result = cursor.execute(sql)
    result_tuple_list = fetch_result.fetchall()
    cursor.close()
    conn.close()
    return result_tuple_list

  def do_select_with_sql_without_tuplevalues(self, sql):
    self.sqlite_createtable_if_not_exists()
    sql = sql % {'tablename': self.tablename}
    conn = self.get_connection()
    cursor = conn.cursor()
    fetch_result = cursor.execute(sql)
    result_tuple_list = fetch_result.fetchall()
    cursor.close()
    conn.close()
    return result_tuple_list

  def do_select_with_sql_n_tuplevalues(self, sql, tuplevalues):
    self.sqlite_createtable_if_not_exists()
    sql = sql % {'tablename': self.tablename}
    conn = self.get_connection()
    cursor = conn.cursor()
    fetch_result = cursor.execute(sql, tuplevalues)
    result_tuple_list = fetch_result.fetchall()
    cursor.close()
    conn.close()
    return result_tuple_list

  def fetch_node_by_id(self, _id):
    sql = 'select * from %(tablename)s where id=?;' % {'tablename': self.tablename}
    tuplevalues = (_id,)
    return self.do_select_with_sql_n_tuplevalues(sql, tuplevalues)

  def fetch_node_by_hkey(self, hkey):
    sql = 'select * from %(tablename)s where hkey=?;'
    tuplevalues = (hkey,)
    return self.do_select_with_sql_n_tuplevalues(sql, tuplevalues)

  def fetch_all(self):
    sql = 'select * from %(tablename)s;' % {'tablename': self.tablename}
    return self.do_select_with_sql_without_tuplevalues(sql)

  def do_update_with_all_fields_with_tuplevalues_if_needed(self, found_row, tuplevalues):
    if len(found_row) > 0 and len(found_row) == len(tuplevalues):
      for i in range(1, len(found_row)):
        if found_row[i] != tuplevalues[i]:
          return self.do_update_with_all_fields_with_tuplevalues(tuplevalues)
    return False  # ie record was not updated for contents are the same

  def do_insert_or_update_with_tuplevalues(self, tuplevalues):
    """
    returns a boolean ie True if inserted/updated False otherwise ie no inserts or updates happened
    """
    hkey = tuplevalues[1]
    rowlist = self.fetch_node_by_hkey(hkey)
    if len(rowlist) == 0:
      return self.do_insert_with_all_fields_with_tuplevalues(tuplevalues)
    elif len(rowlist) == 1:
      found_row = rowlist[0]
      return self.do_update_with_all_fields_with_tuplevalues_if_needed(found_row, tuplevalues)
    error_msg = 'Inconsistency Error: the entry hkey (%s) has more than one record in db.' % hkey
    raise ValueError(error_msg)

  def do_insert_with_all_fields_with_tuplevalues(self, tuplevalues):
    question_marks = '?, ' * len(tuplevalues)
    question_marks = question_marks.rstrip(', ')
    sql_before_interpol = 'insert into %(tablename)s VALUES (' + question_marks + ')'
    return self.do_insert_with_sql_n_tuplevalues(sql_before_interpol, tuplevalues)

  def form_update_with_all_fields_sql(self):
    sql_before_interpol = '''To be implemented in child class
     %(tablename)s ''' % {'tablename': self.tablename}
    return sql_before_interpol

  def do_update_with_all_fields_with_tuplevalues(self, tuplevalues):
    n_fields = self.get_n_fields()
    if len(tuplevalues) != n_fields:
      error_msg = 'len(tuplevalues) != %d =>' % n_fields + str(tuplevalues)
      raise ValueError(error_msg)
    # remove _id from tuplevalues
    hkey = tuplevalues[1]
    # change the order of hkey because it's going to the WHERE clause at the end
    tuplevalues = tuplevalues[2:] + (hkey, )
    sql_before_interpol = self.form_update_with_all_fields_sql()
    return self.do_update_with_sql_n_tuplevalues(sql_before_interpol, tuplevalues)

  def do_update_with_sql_n_tuplevalues(self, sql, tuplevalues):
    conn = self.get_connection()
    cursor = conn.cursor()
    sql = sql % {'tablename': self.tablename}
    print('do_update =>', tuplevalues)
    try:
      _ = cursor.execute(sql, tuplevalues)
      was_updated = True
    except sqlite3.IntegrityError:
      was_updated = False
    cursor.close()
    conn.commit()
    conn.close()
    return was_updated

  def do_insert_with_sql_n_tuplevalues(self, sql, tuplevalues):
    conn = self.get_connection()
    cursor = conn.cursor()
    sql = sql % {'tablename': self.tablename}
    try:
      _ = cursor.execute(sql, tuplevalues)
      was_inserted = True
    except sqlite3.IntegrityError:
      was_inserted = False
    cursor.close()
    conn.commit()
    conn.close()
    return was_inserted
