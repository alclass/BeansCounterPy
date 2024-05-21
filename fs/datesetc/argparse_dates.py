#!/usr/bin/env python3
"""
fs/datesetc/argparse_dates.py
  contains argparse functionality for scripts to import
"""
import argparse
import datetime
import fs.datesetc.datehilofs as hilodt
import fs.datesetc.datefs as dtfs


def get_args():
  """
  pdates = []
  for arg in sys.argv[1:]:
    pdate = arg
    pdates.append(pdate)
  return pdates

  """
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '-d', '--date', metavar='date', type=str, nargs=1,
    help="a date in format yyyy-mm-dd for input to the script",
  )
  parser.add_argument(
    '-t', '--today', action="store_true",
    help="a date in format yyyy-mm-dd for input to the script",
  )
  parser.add_argument(
    '-rmd', '--refmonthdate', metavar='refmonthdate', type=str, nargs=1,
    help="a refmonthdate in format yyyy-mm for input to the script",
  )
  parser.add_argument(
    '-dl', '--datelist', metavar='datelist', type=str, nargs='+',
    help="a datelist each one in format yyyy-mm-dd separated by a space (gap/blank) for input to the script",
  )
  parser.add_argument(
    '-dr', '--daterange', metavar='daterange', type=str, nargs=2,
    help="a daterange has two dates, each in format yyyy-mm-dd, "
         "and represents all days in-between dateini and datefim for input to the script",
  )
  args = parser.parse_args()
  print('args =>', args)
  return args


class Dispatcher:

  def __init__(self, args, func=None):
    self.func = func
    self.args = args
    self.n_rolls = 0
    self.n_funcapply = 0
    self.today = datetime.date.today()
    self.treat_func()

  def treat_func(self):
    if self.func and not callable(self.func):
      error_msg = 'Func (%s) must be callable in Dispatcher' % str(self.func)
      raise RuntimeError(error_msg)
    elif self.func is None:
      self.func = self._roll_dates

  def apply(self, plist):
    """
    error_msg = "Error: Paramenter function 'func' has been given to Dispatch."
    raise ValueError(error_msg)
    """
    self.n_funcapply += 1
    return self.func(plist)

  def _roll_dates(self, plist):
    """
    """
    for pdate in plist:
      print('rolling date', pdate, 'Please, rerun with func parameter defined.')
    return self.n_rolls

  def dispatch(self):
    if self.args.daterange:
      dateini = hilodt.make_date_or_none(self.args.daterange[0])
      datefim = hilodt.make_date_or_none(self.args.daterange[1])
      if dateini is None or datefim is None:
        print('dateini is None or datefim is None. Returning.')
        return 0
      if dateini > self.today:
        return 0
      if datefim > self.today:
        datefim = self.today
      plist = hilodt.gen_date_range_ini_to_fim(dateini, datefim)
      return self.apply(plist)
    if self.args.datelist:
      plist = self.args.datelist
      plist = map(lambda d: hilodt.make_date_or_none(d), plist)
      plist = filter(lambda d: d is not None, plist)
      plist = sorted(filter(lambda d: d <= self.today, plist))
      return self.apply(plist)
    if self.args.refmonthdate:
      refmonthdate = self.args.refmonthdate[0]
      refmonthdate = dtfs.make_refmonthdate_or_none(refmonthdate)
      if refmonthdate is None:
        print("refmonthdate is None ie it's invalid. Returning.")
        return 0
      plist = hilodt.gen_daily_dates_for_refmonth(refmonthdate)
      return self.apply(plist)
    if self.args.date:
      plist = self.args.date  # args.date is already a list
      return self.apply(plist)
    if self.args.today:
      plist = [self.today]  # today, differently from args.date, needs to be enclosed into a list
      return self.apply(plist)


def process():
  """
  """
  args = get_args()
  print('Dispatching', args)
  dispatcher = Dispatcher(args)
  dispatcher.dispatch()


if __name__ == "__main__":
  process()
