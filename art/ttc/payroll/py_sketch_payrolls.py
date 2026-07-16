#!/usr/bin/env python
"""
models/payroll/py_sketch_payrolls.py

from dateutil.relativedelta import relativedelta
import copy
import datetime
"""
import lib.datesetc.refmonth_fs as rmfs
make_refmonthdate_or_raise = rmfs.make_refmonth_or_raise
gen_refmonths_within = rmfs.generate_monthrange
get_refmonths_within = rmfs.get_monthrange_as_list


def make_refmonthrange_range_list(refmonthini, refmonthfim):
  refmonths = []
  for refmonth in gen_refmonths_within(refmonthini, refmonthfim):
    refmonths.append(refmonth)
  return refmonths


class BatchPayRoll:

  def __init__(self):
    self.payrolls = {}

  def add_payroll(self, payroll):
    refmonthdate = payroll.refmonthdate
    self.payrolls[refmonthdate] = payroll

  def sum_payrolls(self, refmonthrange):
    refmonthini = refmonthrange[0]
    refmonthfim = refmonthrange[1]
    total = 0
    for refmonthdate in gen_refmonths_within(refmonthini, refmonthfim):  # gendt.
      try:
        payroll = self.payrolls[refmonthdate]
        total += payroll.remu_liq
      except (KeyError, TypeError):
        continue
    return total
  
  def __str__(self):
    outstr = "Batch PayRoll\n"
    for i, payroll in enumerate(self.payrolls):
      seq = i + 1
      outstr += '%d \t Payroll %s \n' % (seq, str(payroll))
    return outstr


class PayRoll:

  def __init__(self, itemdate, refmonthdate):
    self.refmonthdate = make_refmonthdate_or_raise(refmonthdate)
    self.itemdate = itemdate
    self.descr = None
    self.remu_brut = None
    self.descontos = None
    self.remu_liq = None

  def outdict(self):
    _outdict = [
      (fieldname, value) for fieldname, value in self.__dict__.items()
      if not callable(fieldname)
    ] 
    return _outdict

  def __str__(self):
    outstr = "PayRoll\n"
    for it in self.outdict():
      fieldname, value = it
      outstr += '{fieldname} = {value}\n'.format(fieldname=fieldname, value=value)
    return outstr


data = {

}


def process():
  p = PayRoll('do mês', '2023-08')
  batch = BatchPayRoll()
  batch.add_payroll(p)
  print(p)
  print(batch)
  str_refmonthrange = '2023-01', '2023-08'
  # monthrange_gen = make_monthrange_ini_fim(str_refmonthrange)
  total = batch.sum_payrolls(str_refmonthrange)
  print('batch.sum_payrolls(str_refmonthrange)', total)


if __name__ == '__main__':
  process()
