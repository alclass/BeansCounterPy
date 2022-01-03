#!/usr/bin/env python3
"""
rentabfundos_mod.py
This module contains the RentabFundo class
"""
import fs.db.dbbase_mod as dbu


class RentabFundo:

  def __init__(self, name, monthref, monthrate, yearaccrate, yearrate, netvalue, grossvalue):
    self._id = None
    self.name = name
    self.monthref = monthref
    self.monthrate = monthrate
    self.yearaccrate = yearaccrate
    self.yearrate = yearrate
    self.netvalue = netvalue
    self.grossvalue = grossvalue
    self.db_rentab = dbu.DBRentabFundo()

  def db_insert(self):  # , bank=None
    tuplevalues = (
      self.name,
      self.monthref,
      self.monthrate,
      self.yearaccrate,
      self.yearrate,
      self.netvalue,
      self.grossvalue,
    )
    return self.db_rentab.db_insert_via_tuplevalues(tuplevalues)

  def tabulate_dataseries(self):
    sql = 'SELECT from %(tablename)s ORDER BY monthref;'
    rowlist = self.db_rentab.select_with_sql(sql)
    for tuplevalue in rowlist:
      rentabfundo = self.__class__(
        name=tuplevalue[1],
        monthref=tuplevalue[1],
        monthrate=tuplevalue[1],
        yearaccrate=tuplevalue[1],
        yearrate=tuplevalue[1],
        netvalue=tuplevalue[1],
        grossvalue=tuplevalue[1],
      )
      rentabfundo._id = tuplevalue[0],
      print(rentabfundo)

  def as_dict(self):
    outdict = {
      '_id': self._id,
      'name': self.name,
      'monthref': self.monthref,
      'monthrate': self.monthrate,
      'yearaccrate': self.yearaccrate,
      'yearrate': self.yearrate,
      'netvalue': self.netvalue,
      'grossvalue': self.grossvalue,
    }
    return outdict

  def __str__(self):
    outstr = '''
      name=%(name)s | monthref=%(monthref)s
      monthrate=%(monthrate)s | yearaccrate=%(yearaccrate)s
          
    '''
    return outstr


def process():
  pass


if __name__ == '__main__':
  process()
