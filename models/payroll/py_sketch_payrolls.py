#!/usr/bin/env python
"""
sketches_payroll.py
"""
from dateutil.relativedelta import relativedelta
import copy
import datetime


def make_refmonthdate_or_raise(refmonthdate):
  if refmonthdate is None:
    error_msg = 'Error: refmonthdate is None'
    raise ValueError(error_msg)
  if isinstance(refmonthdate, datetime.date):
    if refmonthdate.day == 1:
      return refmonthdate
    else:
      return datetime.date(year=refmonthdate.year, month=refmonthdate.month, day=1)
  try:
    refmonthdate = str(refmonthdate)
    pp = refmonthdate.split('-')
    year = int(pp[0])
    month = int(pp[1])
    return datetime.date(year=year, month=month, day=1)
  except (IndexError, ValueError):
    pass
  error_msg = 'Error: refmonthdate is None'
  raise ValueError(error_msg)


def gen_refmonths_within(refmonthini, refmonthfim):
  refmonthini = make_refmonthdate_or_raise(refmonthini)
  refmonthfim = make_refmonthdate_or_raise(refmonthfim)
  current_refmonth = copy.copy(refmonthini)
  while current_refmonth <= refmonthfim:
    yield current_refmonth
    current_refmonth = current_refmonth + relativedelta(months=1)
  return


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
