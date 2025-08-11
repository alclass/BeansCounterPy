#!/usr/bin/env python3
"""
fs/datefs/refmonths_mod.py
  Contains monthly and refmonthly date functions.

import fs.datefs.introspect_dates as intr
"""
import calendar
import datetime
from typing import Union
from dateutil.relativedelta import relativedelta
from sqlalchemy.testing import exclude

import lib.datefs.convert_to_date_wo_intr_sep_posorder as cnv


class ClassWithYearMonthDay:
  def __init__(self, year=None, month=None, day=None):
    self.year = year
    self.month = month
    self.day = day

  def as_date(self):
    try:
      y, m, d = int(self.year), int(self.month), int(self.day)
      dt = datetime.date(year=y, month=m, day=d)
      return dt
    except (TypeError, ValueError):
      pass
    return None

  def as_refmonthdate(self):
    try:
      y, m = int(self.year), int(self.month)
      dt = datetime.date(year=y, month=m, day=1)
      return dt
    except (TypeError, ValueError):
      pass
    return None


def is_date_in_refmonth(pdate: datetime.date | str, refmonthdate: datetime.date | str) -> bool:
  pdate = cnv.make_date_or_none(pdate)
  refmonthdate = make_refmonthdate_or_none(refmonthdate)
  try:
    if pdate.year == refmonthdate.year and pdate.month == refmonthdate.month:
      return True
  except AttributeError:
    pass
  return False


def calc_refmonth_plus_n(pdate, n):
  pdate = cnv.make_date_or_none(pdate)
  if pdate is None:
    return None
  try:
    n = int(n)
  except (TypeError, ValueError):
    return pdate
  if pdate.day != 1:
    pdate = datetime.date(year=pdate.year, month=pdate.month, day=1)
  return pdate + relativedelta(months=n)


def calc_refmonth_minus_n(pdate, n):
  try:
    n = int(n)
  except (TypeError, ValueError):
    return pdate
  n = -n
  return calc_refmonth_plus_n(pdate, n)


def calc_n_completemonths_between_dates(
    start_date: Union[str, datetime.date], end_date: Union[str, datetime.date]
  ) -> int | None:
  start_date = cnv.make_date_or_none(start_date)
  if start_date is None:
    return None
  end_date = cnv.make_date_or_none(end_date)
  if end_date is None:
    return None
  if start_date > end_date:
    tmpdate = end_date
    end_date = start_date
    start_date = tmpdate
  # Calculate the difference
  delta = relativedelta(end_date, start_date)
  # Get total months
  total_months = delta.months + (delta.years * 12)
  return total_months


def get_nmonthd_fr_mmonth_or_none(mmonth):
  """
  Transforms a mmonth (which is just a monthnumber preceded (prefixed) by "M") into a nmonth (the month's number)
  """
  if mmonth is None:
    return None
  try:
    smonth = mmonth.lower().lstrip('m')
    nmonth = int(smonth)
    return nmonth
  except ValueError:
    return None


def get_refmonthdate_fr_mmonth_n_year_or_none(mmonth, year):
  """
  Transforms a mmonth (which is just a monthnumber preceded (prefixed) by "M") into a nmonth (the month's number)
    and, complemented with year, returns a refmonthdate
  """
  if mmonth is None:
    return None
  nmonth = get_nmonthd_fr_mmonth_or_none(mmonth)
  if nmonth is None:
    return None
  return make_refmonthdate_for_year_n_month(year, nmonth)


def make_refmonthdate_for_year_n_month(year, nmonth):
  if year is None or nmonth is None:
    return None
  try:
    year = int(year)
    nmonth = int(nmonth)
    return datetime.date(year=year, month=nmonth, day=1)
  except ValueError:
    pass
  return None


def make_current_refmonthdate() -> datetime.date:
  today = datetime.date.today()
  current_refmonthdate = datetime.date(year=today.year, month=today.month, day=1)
  return current_refmonthdate


def make_refmonthdate_or_current(refmonthdate: datetime.date | None) -> datetime.date | None:
  refmonthdate = make_refmonthdate_or_none(refmonthdate)
  if isinstance(refmonthdate, datetime.date):
    return refmonthdate
  return make_current_refmonthdate()


def make_refmonth_or_m_minus_2(p_refmonthdate: datetime.date | None) -> datetime.date | None:
  """
  Gets refmonthdate from input or, if it becomes None, make a refmonthdate of the M-2 type

  The M-2 type
  ============
    The M-2 type is a refmonthdate two months before the current refmonthdate
  """
  refmonthdate = make_refmonth_or_none(p_refmonthdate)
  if refmonthdate is not None:
    return refmonthdate
  curr_refmonth = make_current_refmonthdate()
  refmonth_m_minus_2 = curr_refmonth - relativedelta(months=2)
  return refmonth_m_minus_2


def make_refmonth_or_none(refmonth: datetime.date | None) -> datetime.date | None:
  """
  Notice: differently from make_date_or_none(), this function does not include the 'day' field in a date,
    though it returns a date with day=1
  """
  if refmonth is None:
    return None
  if isinstance(refmonth, datetime.date):
    if refmonth.day == 1:
      return refmonth
    return datetime.date(year=refmonth.year, month=refmonth.month, day=1)
  try:
    y = int(refmonth.year)
    m = int(refmonth.month)
    return datetime.date(year=y, month=m, day=1)
  except (AttributeError, TypeError, ValueError):
    # pass on for a new try below
    pass
  try:
    ppp = str(refmonth).split(' ')
    pp = ppp[0].split('-')
    year = int(pp[0])
    month = int(pp[1])
    return datetime.date(year=year, month=month, day=1)
  except (IndexError, ValueError):
    pass
  return None


def make_refmonth_or_current(str_or_date_refmonth=None):
  refmonthdate = make_refmonth_or_none(str_or_date_refmonth)
  if refmonthdate is not None:
    return refmonthdate
  today = datetime.date.today()
  return datetime.date(year=today.year, month=today.month, day=1)


def make_refmonth_ini_n_fim_w_year_forbid_future(year=None):
  today = datetime.date.today()
  if year is None:
    year = today.year
  if year > today.year:
    return None, None
  refmonth_ini = make_refmonthdate_for_year_n_month(year, 1)
  if year >= today.year:
    month_to = today.month if today.month < 12 else 12
  else:
    month_to = 12
  refmonth_fim = make_refmonthdate_for_year_n_month(year, month_to)
  return refmonth_ini, refmonth_fim


def make_refmonth_ini_n_fim_w_year(year=None):
  today = datetime.date.today()
  if year is None:
    year = today.year
  refmonth_ini = make_refmonthdate_for_year_n_month(year, 1)
  refmonth_fim = make_refmonthdate_for_year_n_month(year, 12)
  return refmonth_ini, refmonth_fim


def make_refmonth_ini_n_fim_w_yearrange_forbid_future(yearini, yearfim=None):
  today = datetime.date.today()
  if yearini is None:
    return None, None
  if yearfim is None:
    yearfim = today.year
  try:
    yearini = int(yearini)
    if yearini > today.year:
      return None, None
    yearini = yearini if yearini <= today.year else today.year
  except ValueError:
    pass
  try:
    yearfim = int(yearfim)
    yearfim = yearfim if yearfim <= today.year else today.year
    # swap if yearini > yearfim
    if yearini > yearfim:
      tmpyear = yearini
      yearini = yearfim
      yearfim = tmpyear
  except ValueError:
    pass
  refmonth_ini, refmonth_fim_yearini = make_refmonth_ini_n_fim_w_year_forbid_future(yearini)
  _, refmonth_fim = make_refmonth_ini_n_fim_w_year_forbid_future(yearfim)
  if refmonth_fim is None:
    refmonth_fim = refmonth_fim_yearini
  return refmonth_ini, refmonth_fim


def trans_monthrange_into_dailydaterange_or_none(monthrangetuple):
  try:
    month_ini, month_fim = tuple(monthrangetuple)
    month_ini = make_refmonth_or_none(month_ini)
    month_fim = make_refmonth_or_none(month_fim)
    if month_ini is None or month_fim is None:
      return None, None
    date_ini = month_ini
    date_fim = get_monthslastdate_via_addition(month_fim)
    return date_ini, date_fim
  except (IndexError, TypeError, ValueError):
    pass
  return None, None


def trans_monthrange_into_dailydaterange_or_current(monthrangetuple):
  dateini, datefim = trans_monthrange_into_dailydaterange_or_none(monthrangetuple)
  if dateini and datefim:
    return dateini, datefim
  today = datetime.date.today()
  dateini = datetime.date(year=today.year, month=today.month, day=1)
  datefim = get_monthslastdate_via_calendar(today)
  return dateini, datefim


def transform_month_n_year_to_refmonthdate(month, year):
  try:
    return datetime.date(year=year, month=month, day=1)
  except ValueError:
    pass
  return None


def transform_mmonth_to_refmonthdate(mmonth, year):
  try:
    month_n = int(mmonth.lstrip('M').strip())
    return transform_month_n_year_to_refmonthdate(month_n, year)
  except (AttributeError, ValueError):
    pass
  return None


def trans_year_into_dailydaterange(year=None):
  try:
    year = int(year)
  except (TypeError, ValueError):
    today = datetime.date.today()
    year = today.year
  dateini = datetime.date(year=year, month=1, day=1)
  datefim = datetime.date(year=year, month=12, day=31)
  return dateini, datefim


def get_monthslastday_via_calendar(pdate: datetime.date | None) -> int | None:
  if pdate is None:
    return None
  try:
    year = pdate.year
    month = pdate.month
    last_day_in_month = calendar.monthrange(year, month)[1]
    return last_day_in_month
  except AttributeError:
    pass
  return None


def get_monthslastdate_via_calendar(pdate: datetime.date | None) -> datetime.date | None:
  indate = cnv.make_date_or_none(pdate)
  if indate is None:
    return None
  lastday = get_monthslastday_via_calendar(pdate)
  if lastday is None:
    return None
  try:
    if pdate.day == lastday:
      return pdate
    outdate = datetime.date(year=pdate.year, month=pdate.month, day=lastday)
    return outdate
  except AttributeError:
    pass
  return None


def get_monthslastday_via_addition(pdate: datetime.date | None) -> int | None:
  indate = get_monthslastdate_via_addition(pdate)
  if indate is None:
    return None
  try:
    return indate.day
  except AttributeError:
    pass
  return None


def get_monthslastdate_via_addition(pdate: datetime.date | None) -> datetime.date | None:
  indate = cnv.make_date_or_none(pdate)
  if indate is None:
    return None
  if indate.day > 1:
    date_set_on_first_day_of_month = datetime.date(indate.year, indate.month, 1)
  else:
    date_set_on_first_day_of_month = indate
  date_on_first_day_of_next_month = date_set_on_first_day_of_month + relativedelta(months=1)
  monthslastday_date = date_on_first_day_of_next_month - relativedelta(days=1)
  return monthslastday_date


def make_refmonthdate_or_none(refmonthdate: datetime.date | None) -> datetime.date | None:
  if refmonthdate is None:
    return None
  if isinstance(refmonthdate, datetime.date):
    if refmonthdate.day == 1:
      return refmonthdate
    return datetime.date(year=refmonthdate.year, month=refmonthdate.month, day=1)
  try:
    refmonthdate = str(refmonthdate).strip(' \t\r\n')
    ppp = refmonthdate.split(' ')
    pp = ppp[0].split('-')
    year = int(pp[0])
    month = int(pp[1])
    return datetime.date(year=year, month=month, day=1)
  except (AttributeError, TypeError, ValueError):
    pass
  return None


def spawn_inidate_n_fimdate_fr_refmonth(refmonthdate: datetime.date | None) -> tuple:
  if refmonthdate is None:
    return None, None
  inidate = refmonthdate  # notice datetime.date 'variables' are immutable
  last_day_in_month = get_monthslastday_via_calendar(refmonthdate)
  try:
    fimdate = datetime.date(year=inidate.year, month=inidate.month, day=last_day_in_month)
    return inidate, fimdate
  except AttributeError:
    pass
  return None, None


def adhoctest1():
  """
  """
  y, m, d = 2012, 2, 3
  attrs_obj = ClassWithYearMonthDay(year=y, month=m, day=d)
  expected_refmonthdate = attrs_obj.as_refmonthdate()
  pdate = datetime.date(year=y, month=m, day=d)
  returned_refmonthdate = make_refmonth_or_none(pdate)
  print('expected_refmonthdate (done with ClassWithYearMonthDay)', expected_refmonthdate)
  print('returned_refmonthdate', returned_refmonthdate)
  inidt, fimdt = spawn_inidate_n_fimdate_fr_refmonth(expected_refmonthdate)
  scrmsg = f"spawn_inidate_n_fimdate_fr_refmonth({expected_refmonthdate}) -> {inidt} | {fimdt}"
  print(scrmsg)
  monthslastdate = get_monthslastdate_via_calendar(pdate)
  scrmsg = f"get_monthslastdate_via_calendar({pdate}) -> {monthslastdate}"
  print(scrmsg)
  monthslastdate = get_monthslastdate_via_addition(pdate)
  scrmsg = f"get_monthslastdate_via_addition({pdate}) -> {monthslastdate}"
  print(scrmsg)
  monthslastday = get_monthslastday_via_calendar(pdate)
  scrmsg = f"get_monthslastday_via_calendar({pdate}) -> {monthslastday}"
  print(scrmsg)
  monthslastday = get_monthslastday_via_addition(pdate)
  scrmsg = f"get_monthslastday_via_addition({pdate}) -> {monthslastday}"
  print(scrmsg)


def adhoctest2():
  yearini, yearfim = 2020, 2024
  refmonth_ini, refmonth_fim = make_refmonth_ini_n_fim_w_yearrange_forbid_future(yearini, yearfim)
  scrmsg = f"yearini={yearini} | yearfim={yearfim} | refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  print(scrmsg)
  yearini, yearfim = 2020, 2028
  refmonth_ini, refmonth_fim = make_refmonth_ini_n_fim_w_yearrange_forbid_future(yearini, yearfim)
  scrmsg = f"yearini={yearini} | yearfim={yearfim} | refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  print(scrmsg)
  yearini, yearfim = 2027, 2029
  refmonth_ini, refmonth_fim = make_refmonth_ini_n_fim_w_yearrange_forbid_future(yearini, yearfim)
  scrmsg = f"yearini={yearini} | yearfim={yearfim} | refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  print(scrmsg)
  yearini, yearfim = 2025, 2034
  refmonth_ini, refmonth_fim = make_refmonth_ini_n_fim_w_yearrange_forbid_future(yearini, yearfim)
  scrmsg = f"yearini={yearini} | yearfim={yearfim} | refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  print(scrmsg)


def adhoctest3():
  """
  how to calculate number of months between two dates in Python?
  """
  pdate1 = cnv.make_date_or_none('2020-02-1')
  pdate2 = cnv.make_date_or_none('2021-10-31')
  n_months_in_bw = calc_n_completemonths_between_dates(pdate1, pdate2)
  scrmsg = f"{pdate2} - {pdate1} = n_months_in_bw={n_months_in_bw}"
  print(scrmsg)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest3()
