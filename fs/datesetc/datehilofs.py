#!/usr/bin/env python3
"""
fs/datesetc/datehilofs.py
    "hilo" here just means extension date function using strings. Eg, month with a 3-letter string.
  Avoid importing datefunctions.py, in the same package as this, to liberate it to import from this,
    in other words, to avoid circulation importation and somehow maintain 'upstream'
    (or unidirectional dependence).
"""
import copy
import time
import datetime
from dateutil.relativedelta import relativedelta
month3letterlist = 'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'.split('|')


def find_strinlist_that_starts_with_a_5charyearblank_via_if(entries):
  """
  recuperates year plus a blank
  """
  newentries = []
  if entries is None:
    return []
  for e in entries:
    try:
      _ = int(e[0:4])
      if e[4:5] != ' ':
        continue
      newentries.append(e)
    except (IndexError, ValueError):
      pass
  return newentries


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
  dateini = make_date_with(dateini)
  if dateini is None:
    return []
  # treat datefim
  datefim = make_date_with(datefim)
  if datefim is None:
    datefim = datetime.date.today()
  if dateini == datefim:
    return [dateini]
  if dateini > datefim:
    return []
  # from here: dateini < datefim
  if not descending:  # ie, ascending
    return gen_date_range_ini_to_fim_asc(dateini, datefim)
  return gen_date_range_ini_to_fim_desc(dateini, datefim)


def gen_refmonthdate_ini_fim_range_asc(p_refmonthdateini, p_refmonthdatefim):
  current_date = copy.copy(p_refmonthdateini)
  while current_date <= p_refmonthdatefim:
    yield current_date
    current_date = current_date + relativedelta(months=1)
  return


def gen_refmonthdate_ini_fim_range_desc(p_refmonthdateini, p_refmonthdatefim):
  current_date = copy.copy(p_refmonthdateini)
  while current_date >= p_refmonthdatefim:
    yield current_date
    current_date = current_date - relativedelta(months=1)
  return


def gen_refmonthdate_ini_fim_range(p_refmonthdateini, p_refmonthdatefim, descending=False):
  refmonthdateini = make_refmonth_or_none(p_refmonthdateini)
  refmonthdatefim = make_refmonth_or_none(p_refmonthdatefim)
  if not descending:  # ie, ascending
    return gen_refmonthdate_ini_fim_range_asc(refmonthdateini, refmonthdatefim)
  return gen_refmonthdate_ini_fim_range_desc(refmonthdateini, refmonthdatefim)


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


def is_str_dateprefixed(stri):
  """
  Returns True if string has a "yyyy-mm-dd " (date+blank) beginning
  """
  try:
    pp = stri.split(' ')
    strdate = pp[0]
    pdate = make_date_with(strdate)
    if pdate:
      return True
  except (AttributeError, IndexError):
    pass
  return False


def make_date_with_or_today(pdate):
  return make_date_with(pdate) or datetime.date.today()


def make_date_with(pdate):
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


def make_date_from_ddmmmyyyy_with_month3letter(ddmmmyyyy_with_month3letter):
  """
  Examples:
    input: '01-jan-2023' => output: datetime.date(year=2023, month=1, day=1)
    input: '17-oct-2015' => output: datetime.date(year=2015, month=10, day=17)
  """
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


def make_today_as_a_month3letter_date():
  today = datetime.date.today()
  return render_date_as_ddmmmyyyy_with_month3letter_or_none(today)


def make_refmonth_or_none(refmonth):
  if isinstance(refmonth, datetime.date):
    if refmonth.day == 1:
       return refmonth
    else:
      return datetime.date(year=refmonth.year, month=refmonth.month, day=1)
  try:
    refmonth = refmonth.strip(' \t\r\n')
    pp = refmonth.split('-')
    year = int(pp[0])
    month = int(pp[1])
    return datetime.date(year=year, month=month, day=1)
  except (AttributeError, IndexError, TypeError, ValueError):
    pass
  return None


def make_refmonth_or_current(p_refmonth=None):
  refmonthdate = make_refmonth_or_none(p_refmonth)
  if refmonthdate is None:
    today = datetime.date.today()
    return datetime.date(year=today.year, month=today.month, day=1)
  return refmonthdate


def render_date_as_ddmmmyyyy_with_month3letter_or_none(pdate, sep='/'):
  if pdate is None:
    return None
  try:
    idx = pdate.month - 1
    month3letter = month3letterlist[idx]
    outdate = '{day:02}{sep}{month3letter}{sep}{year}'.format(
      day=pdate.day, month3letter=month3letter, year=pdate.year, sep=sep,
    )
    return outdate
  except (AttributeError, IndexError):
    pass
  return None


def render_date_as_ddmmmyyyy_with_month3letter_or_today(pdate, sep='/'):
  idate = make_date_with_or_today(pdate)
  return render_date_as_ddmmmyyyy_with_month3letter_or_none(idate, sep)


def return_datelist_or_empty_from_strlist(datelist):
  outlist = []
  try:
    for pdate in datelist:
      odate = make_date_with(pdate)
      if odate:
        outlist.append(odate)
  except TypeError:  # catches if datelist is not subscriptable
    pass
  return outlist


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
  pdate = make_date_with(strdate)
  mmmstrdate = render_date_as_ddmmmyyyy_with_month3letter_or_none(pdate)  # default sep is '/'
  print('pdate', pdate, ' => ddmmmyyyy', mmmstrdate)
  mmmstrdate = render_date_as_ddmmmyyyy_with_month3letter_or_none(pdate, '-')  # default sep is '/'
  print('pdate', pdate, ' => ddmmmyyyy', mmmstrdate)
  pdate = make_date_from_ddmmmyyyy_with_month3letter(mmmstrdate)
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
