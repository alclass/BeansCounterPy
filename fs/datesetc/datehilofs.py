#!/usr/bin/env python3
"""
  datehilofs.py
    "hilo" here just means extension date function using strings. Eg, month with a 3-letter string.
"""
import datetime
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
