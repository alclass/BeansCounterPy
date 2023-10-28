#!/usr/bin/env python3
"""
  datehilofs.py
    "hilo" here just means extension date function using strings. Eg, month with a 3-letter string.
"""
import copy
import datetime
from dateutil.relativedelta import relativedelta
import fs.datesetc.datefs as dtfs
month3letterlist = 'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'.split('|')


def get_3letter_monthdict(month3letter=None):
  if month3letter is None:
    return None
  try:
    smonth3letter = str(month3letter).lower()
    if len(smonth3letter) < 3:
      return None
    if len(smonth3letter) > 3:
      smonth3letter = smonth3letter[:3]  # truncate it to a new variable
    i = month3letterlist.index(smonth3letter)
    return i + 1
  except ValueError:
    pass
  return None


def render_pydate_as_ddmmmyyyy_with_month3letter(pdate, sep='/'):
  if pdate is None:
    return None
  try:
    idate = dtfs.return_date_or_recup_it_from_str(pdate)
    idx = idate.month - 1
    month3letter = month3letterlist[idx]
    outdate = '{day:02}{sep}{month3letter}{sep}{year}'.format(
      day=idate.day, month3letter=month3letter, year=idate.year, sep=sep,
    )
    return outdate
  except (AttributeError, IndexError):
    pass
  return None


def render_pydate_as_ddmmmyyyy_with_month3letter_or_today(pdate):
  if pdate is None:
    today = datetime.date.today()
    return render_pydate_as_ddmmmyyyy_with_month3letter(today)
  return render_pydate_as_ddmmmyyyy_with_month3letter(pdate)


def make_pydate_from_ddmmmyyyy_with_month3letter(ddmmmyyyy_with_month3letter):
  try:
    pp = ddmmmyyyy_with_month3letter.split('-')
    year = int(pp[2])
    day = int(pp[0])
    month3letter = pp[1]
    idx = month3letterlist.index(month3letter)
    month = idx + 1
    return datetime.date(year=year, month=month, day=day)
  except (AttributeError, IndexError, ValueError):
    pass
  return None


def make_todaypydate_with_month3letter():
  today = datetime.date.today()
  return render_pydate_as_ddmmmyyyy_with_month3letter(today)


def try_make_date_with(pdate):
  if isinstance(pdate, datetime.date):
    return pdate
  if pdate is None:
    return None
  try:
    strdate = str(pdate)
    pp = strdate.split('-')
    year = int(pp[0])
    month = int(pp[1])
    day = int(pp[2])
    return datetime.date(year=year, month=month, day=day)
  except (IndexError, ValueError):
    pass
  return None


def return_datelist_or_empty(datelist):
  outlist = []
  try:
    for pdate in datelist:
      odate = try_make_date_with(pdate)
      if odate:
        outlist.append(odate)
  except TypeError:  # catches if datelist is not subscriptable
    pass
  return outlist



def return_datelist_or_empty(datelist):
  if datelist is None or len(datelist) == 0:
    return []
  outlist = []
  try:
    for pdate in datelist:
      odate = try_make_date_with(pdate)
      if odate is None:
        continue
      outlist.append(odate)
    return outlist
  except TypeError:  # includes object not subscriptable
    pass
  return outlist


def gen_date_range_ini_to_fim_asc(dateini, datefim):
  """
  private:
    this function should only be called by gen_date_range_ini_to_fim(dateini, datefim, descending=False)
    because it prepares conditions for the while-loop in-here
  """
  current_date = copy.copy(dateini)
  while current_date <= datefim:
    yield current_date
    current_date = current_date + relativedelta(days=1)
  return


def gen_date_range_ini_to_fim_desc(dateini, datefim):
  """
  private:
    this function should only be called by gen_date_range_ini_to_fim(dateini, datefim, descending=False)
    because it prepares conditions for the while-loop in-here
  """
  current_date = copy.copy(datefim)
  while current_date >= dateini:
    yield current_date
    current_date = current_date - relativedelta(days=1)
  return


def gen_date_range_ini_to_fim(dateini, datefim, descending=False):
  """'
  Example: gen_date_range_ini_to_fim('2023-2-4', '2023-2-7')
    will generate:
  return_gen = [
    datetime.date(2023, 2, 4), datetime.date(2023, 2, 5),
    datetime.date(2023, 2, 6), datetime.date(2023, 2, 7),
  ]
  Or, visually as str: ['2023-02-04', '2023-02-05', '2023-02-06', '2023-02-07']
  Notice that, differently from range(4, 7), which excludes the 7 itself, day "7" is included in the output
  """
  # treat dateini
  dateini = try_make_date_with(dateini)
  if dateini is None:
    return []
  # treat datefim
  datefim = try_make_date_with(datefim)
  if datefim is None:
    datefim = datetime.date.today()
  if dateini == datefim:
    return [dateini]
  if dateini > datefim:
    return []
  # from here: dateini < datefim
  if not descending:  # ie, ascending
    return gen_date_range_ini_to_fim_asc(dateini, datefim)
  gen_date_range_ini_to_fim_desc(dateini, datefim)


def adhoctest():
  month3letter = 'octo'
  n = get_3letter_monthdict(month3letter)
  print(month3letter, n)
  month3letter = 'bla'
  n = get_3letter_monthdict(month3letter)
  print(month3letter, n)
  month3letter = 'FEB'
  n = get_3letter_monthdict(month3letter)
  print(month3letter, n)
  month3letter = 'mAy'
  n = get_3letter_monthdict(month3letter)
  print(month3letter, n)
  strdate = '2023-2-4'
  pdate = dtfs.transform_strdate_yyyymmdd_to_date_sep_by(strdate)  # default sep is '-'
  mmmstrdate = render_pydate_as_ddmmmyyyy_with_month3letter(pdate)  # default sep is '/'
  print('pdate', pdate, ' => ddmmmyyyy', mmmstrdate)
  mmmstrdate = render_pydate_as_ddmmmyyyy_with_month3letter(pdate, '-')  # default sep is '/'
  print('pdate', pdate, ' => ddmmmyyyy', mmmstrdate)
  pdate = make_pydate_from_ddmmmyyyy_with_month3letter(mmmstrdate)
  print('ddmmmyyyy', mmmstrdate, ' => pdate', pdate)
  dateini = '2023-2-4'
  datefim = '2023-2-7'
  print('adhoctest gen_date_range_ini_to_fim(dateini, datefim):', dateini, datefim)
  for pdate in gen_date_range_ini_to_fim(dateini, datefim):
    print(pdate)


def getdate_older_version():
  """
  This function is for "museum" purposes.
  What it does is just: datetime.date.today(), ie a simple call to today() in datetime.date
  """""
  str_date_list = time.ctime().split()
  year = str_date_list[-1]
  month3letter = str_date_list[1]
  month_int = get_3letter_monthdict(month3letter)
  month = str(month_int).zfill(2)
  day = str_date_list[2]
  date_str = year + '-' + month + '-' + day.zfill(2)
  # print 'Today\'s date is', dateStr
  return date_str


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  pass
  adhoctest()
