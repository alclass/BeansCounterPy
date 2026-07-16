#!/usr/bin/env python3
"""
lib/datesetc/refmonth_fs.py
  Contains monthly and refmonthly date functions.

Quick Comparison: Iterator vs Generator
  Iterator[YieldType]:
    Perfect for standard data streams and loops.
  Generator[YieldType, SendType, ReturnType]:
    Mandatory for coroutines, .send() pipelines, or explicit returns.

# from sqlalchemy.testing import exclude
# import lib.texts.textfs as txfs  # txfs.cleanup_str_leaving_only_numbers_or_dashes
"""
import calendar
from collections.abc import Iterator
import copy
import datetime
from typing import Union, Any
from dateutil.relativedelta import relativedelta
import lib.datesetc.datefs as dtfs
import lib.datesetc.datefs as dfs  # dfs.transform_strdate_to_date
import lib.datesetc.datehilofs as hilo  # dfs.transform_strdate_to_date
MONTHS = [
  'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez',
]


def get_3letter_extmes(nmonth):
  try:
    return MONTHS[nmonth-1]
  except (IndexError, TypeError):
    pass
  return None


def calc_n_calendar_months_in_between(
    date1: datetime.date | None, date2: datetime.date | None,
  ):
  """
  # Example Usage
  start = datetime(2023, 10, 15)
  end = datetime(2026, 7, 12)
  print(get_calendar_months(start, end))  # Output: 33
  """
  # Ensure date2 is the later date
  if date1 is None:
    return None
  if date2 is None:
    return None
  d1 = min(date1, date2)
  d2 = max(date1, date2)
  # Calculate difference based entirely on year and month values
  return (d2.year - d1.year) * 12 + d2.month - d1.month


def partition_monthlydays_wi_monthrange(inidate, findate):
  """
  Example:
    input:
      inidate = "2026-01-10"
      findate = "2026-04-07"
    output:
      [22, 28, 31, 7]
    Meaning:
      The output is the number of days available in each month
        in the monthrange inidate-findate
      i.e., there are:
        22 days in 2026-01 (from day 10 inclusive to 31 also included)
        28 days in 2026-02 (the whole month)
        31 days in 2026-03 (the whole month)
        07 days in 2026-04 (up to day 7 inclusive)
  """
  inidate = dtfs.make_date_or_raise(inidate)
  findate = dtfs.make_date_or_today(findate)
  if findate < inidate:
    errmsg = f"findate ({findate}) cannot be less than inidate ({inidate})"
    raise ValueError(errmsg)
  outlist = []
  curdate = copy.copy(inidate)
  while curdate < findate:
    lastdayinmonth = calendar.monthrange(curdate.year, curdate.month)[1]
    ndays = lastdayinmonth - curdate.day + 1
    outlist.append(ndays)
    curdate = make_next_refmonth_or_raise(curdate)
  # at this point, outlist is complete but
  # the last element may need correction
  if findate.day != 1:
    # okay, it needs correction
    _ = outlist.pop()  # pop last element out
    ndays = findate.day  # correct number of days in last month
    outlist.append(ndays)
  return outlist


def find_dateborders_fr_ndayslist_n_refmonths(
    ndayslist: list,
    inirefmonth: datetime.date | str,
    finrefmonth: datetime.date | str,
  ) -> tuple:
  """
  case 1: ndayslist contains only sole number
  case 2: ndayslist contains two numberfs
  case 3: ndayslist contains more than two numberfs
  """
  # copy ndayslist to avoid (outside) side effects
  if ndayslist is None:
    return None, None
  if len(ndayslist) == 0:
    return None, None
  inirefmonth = make_refmonth_or_none(inirefmonth)
  if inirefmonth is None:
    return None, None
  amount = ndayslist[0]
  ndaysinmonth = calendar.monthrange(inirefmonth.year, inirefmonth.month)[1]
  onday = ndaysinmonth - amount + 1
  inidate = datetime.date(inirefmonth.year, inirefmonth.month, onday)
  if len(ndayslist) == 1:
    findate = datetime.date(inirefmonth.year, inirefmonth.month, ndaysinmonth)
    return inidate, findate
  # at this point, finrefmonth must exist and be greater inirefmonth
  finrefmonth = make_refmonth_or_none(finrefmonth)
  if finrefmonth is None:
    return None, None
  if inirefmonth >= finrefmonth:
    return None, None
  amount = ndayslist[-1]
  findate = datetime.date(finrefmonth.year, finrefmonth.month, amount)
  # before returning, check consistency
  n_months_in_between = calc_n_months_involved(finrefmonth, inirefmonth)
  if len(ndayslist) != n_months_in_between:
    errmsg = f"Erro: len(ndayslist)(={len(ndayslist)}) != n_months_in_between(={n_months_in_between})"
    errmsg += f"\n\tinirefmonth={inirefmonth} | inirefmonth={finrefmonth}"
    raise ValueError(errmsg)
  return inidate, findate


def mount_ndays_n_refmonth_tuplelist(inidate, findate):
  ndayslist = partition_monthlydays_wi_monthrange(inidate, findate)
  monthborders = find_dateborders_fr_ndayslist_n_refmonths(ndayslist, inidate, findate)
  inirefmonth, finrefmonth = monthborders
  refmonths = get_monthrange_as_list(inirefmonth, finrefmonth)
  tuplelist = [(ndayslist[i], refmonths[i]) for i in range(len(ndayslist))]
  return tuplelist


def calc_n_months_involved(findate, inidate):
  """
  Notice parameters are inverted, i.e., it's (findate, inidate) instead of (inidate, findate)
    because it's the order one would use in subtraction
  This function considers a part month as a month
  Example: (2025-12-15, 2026-1-14) counts 2 months

  relatdelta = findate - inidate
  return int(relatdelta.months) + 1

  """
  inidate = dtfs.make_date_or_none(inidate)
  findate = dtfs.make_date_or_none(findate)
  inirefmonth = make_refmonth_or_none(inidate)
  finrefmonth = make_refmonth_or_none(findate)
  if inirefmonth is None or finrefmonth is None:
    return 0
  if inirefmonth > finrefmonth:
    errmsg = f"Error: inirefmonth {inirefmonth} > finrefmonth {finrefmonth}"
    raise ValueError(errmsg)
  if inirefmonth == finrefmonth:
    return 1
  delta = calc_n_calendar_months_in_between(findate, inidate)
  if delta is None:
    return None
  return delta + 1


def calc_int_n_months_inbetween(
    inidate: datetime.date, findate: datetime.date,
  ):
  """
  Calculates the integer floor number of months between inidate and findate
  This function is inclusive of both dates

  Take care with the order of the parameters.

  Obs: this function is
       Step-1 in finding the elapsed time
       im integer number of months between 2 dates,
       the Step-2 function finds the fraction remaining if any
       (consider these two functions private, accessing by a distributor-function)

  Example of I/O in this function:
  e1 when inidate=2026-01-01, findate=2026-01-31 (added one to it)
    return tuple is (1, 0) i.e., elapsed 1 full month and no fraction
  e2 when inidate=2026-01-01, findate=2026-04-31
    return tuple is (3, 0.5) i.e., elapsed 3 full months and 1/2 fraction
  e3 when inidate=2026-01-01, findate=2026-12-31
    return tuple is (12, 0) i.e., elapsed 12 full months and no fraction

  Notice about input parameters and "outside object mutation":
    The beginning lines:
        inidate = dtfs.make_date_or_raise(inidate)
        findate = dtfs.make_date_or_today(findate)
      technically do not mutate these objects (in the) outside,
      but client callers must take notice of findate
        becoming 'today', when it's not date-convertible,
        inside this function.

  # this 'entrance' is done in the distributor-fucntion
  inidate = dtfs.make_date_or_raise(inidate)
  findate = dtfs.make_date_or_today(findate)
  if findate < inidate:
    errmsg = f"findate ({findate}) cannot be less than inidate ({inidate})"
    raise ValueError(errmsg)
  """
  # Because of the inclusiveness of these 2 dates,
  # one (day) has to be added to findate
  # no mutation happens (in the) outside, because 'date' type is immutable
  # this odd-one only happens in Step-1, not in Step-2
  findate = findate + relativedelta(days=1)
  # Get the full breakdown relative delta
  datesdelta = relativedelta(findate, inidate)
  # Combine the years into months, plus any remaining months
  total_months = (datesdelta.years * 12) + datesdelta.months
  return total_months


def calc_floatfraction_elapsed_inbetween_months(inidate, findate, n_int_months_inbetween):
  """
  This function is not correct and was discontinued due to another solution at the time
  TODO correct this function when possible

  The floatfraction_elapsed_inbetween_months depends on that
    'calculated whole-integer' should be been already issued (called),
    because this function calculated the fraction complement if it happens.

  Examples:

    ex1: inidate, findate = 2026-01-01, 2026-01-31
    This example show one full month elapsed
      and then its fractional amount should be 0.0

    ex2: inidate, findate = 2026-01-01, 2026-04-15
    This example show three full months elapsed
      and then, notice, half of April as its fractional amount,
      which is then another 1/2 (half)
    This function calculates this fractional 'part':
    The integer part is 3, the float part is 0.5.
    The two together are tuple (3, 0,5) or 3.5 (the sum of the two parts).
  """
  if n_int_months_inbetween < 0:
    errmsg = f"n_int_months_inbetween(={n_int_months_inbetween}) cannot be negative"
    raise ValueError(errmsg)
  midledate = inidate + relativedelta(months=n_int_months_inbetween)
  midledate = midledate + relativedelta(days=1)
  datedelta = findate - midledate
  ndays = datedelta.days
  # By convention, the remaining days should consider the number of days in the last month
  totaldays_in_lastmonth = calendar.monthrange(findate.year, findate.month)[1]
  inbetween_months_elapsed_fraction = ndays / totaldays_in_lastmonth
  return inbetween_months_elapsed_fraction


def months_inbetween_return_int_n_float(inidate, findate):
  """
  This function returns a tuple with the following:
    a) the first element is an int representing the number of whole months between inidate and findate
    b) the second number is a fraction that duration-complements, if any, the above int

  "distributor-function"
  ======================

  This function is also a distributor-function to the 2 ones called from here
  """
  inidate = dtfs.make_date_or_raise(inidate)
  findate = dtfs.make_date_or_today(findate)
  if findate < inidate:
    errmsg = f"findate ({findate}) cannot be less than inidate ({inidate})"
    raise ValueError(errmsg)
  n_int_inbetween = calc_int_n_months_inbetween(inidate, findate)
  n_float_in_borders = calc_floatfraction_elapsed_inbetween_months(inidate, findate, n_int_inbetween)
  duration_elapsed_tuple = (n_int_inbetween, n_float_in_borders)
  return duration_elapsed_tuple


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

  def as_refmonthdate(self) -> datetime.date | None:
    try:
      y, m = int(self.year), int(self.month)
      dt = datetime.date(year=y, month=m, day=1)
      return dt
    except (TypeError, ValueError):
      pass
    return None


def is_date_in_refmonth(pdate: datetime.date | str, refmonthdate: datetime.date | str) -> bool:
  pdate = dfs.make_date_or_none(pdate)
  refmonthdate = make_refmonth_or_none(refmonthdate)
  if pdate is None or refmonthdate is None:
    return False
  try:
    if pdate.year == refmonthdate.year and pdate.month == refmonthdate.month:
      return True
  except AttributeError:
    pass
  return False


def calc_refmonth_plus_n(pdate, n):
  pdate = hilo.make_date_or_none(pdate)
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


def calc_n_completemonths_between_dates_or_raise(
    start_date: Union[str, datetime.date], end_date: Union[str, datetime.date]
  ) -> int | None:
  n_months = calc_n_completemonths_between_dates(start_date, end_date)
  if n_months is None:
    errmsg = f"{start_date} & {end_date} fail to derive number of months in-between"
    raise ValueError(errmsg)


def calc_n_completemonths_between_dates(
    start_date: Union[str, datetime.date], end_date: Union[str, datetime.date]
  ) -> int | None:
  start_date = dfs.make_date_or_none(start_date)
  if start_date is None:
    return None
  end_date = dfs.make_date_or_none(end_date)
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


def generate_monthrange(
    p_refmonth_ini: Any | None,
    p_refmonth_fim: Any | None,
    allow_future: bool = False
  ) -> Iterator[datetime.date]:
  """
  Yields (as an iterator) a refmonth date each in a sequence from refmonth_ini ascending to refmonthdate_fim
    both included.

  Notice that future refmonths are cut off if allow_future is False.
  Function generate_monthrange_allow_future() calls this function pre-setting allow_future as True.
  """
  refmonth_ini = make_refmonth_or_none(p_refmonth_ini)
  if refmonth_ini is None:
    # generated-list is empty
    return
  refmonth_fim = make_refmonth_or_current(p_refmonth_fim)
  refmonthtoday = make_current_refmonth()
  if refmonth_fim > refmonthtoday:
    if not allow_future:
      refmonth_fim = refmonthtoday
  # the 'caller' sent in ini > fim, an error is not raised, an empty list will return
  if refmonth_ini > refmonth_fim:
    # generated-list is empty
    return
  if refmonth_ini == refmonth_fim:
    # generated-list has only one element
    yield refmonth_fim
    return
  current_refmonth = copy.copy(refmonth_ini)
  # the next 'if' is just to stop the IDE complaining that 'current_refmonth' might be None, which was solved above
  if current_refmonth is None:
    return
  while current_refmonth <= refmonth_fim:
    # generated-list may have two elements at least or more
    yield current_refmonth
    current_refmonth = current_refmonth + relativedelta(months=1)
  return


def generate_monthrange_allow_future(
    inirefmonth: Any | None,
    finrefmonth: Any | None
  ) -> Iterator[datetime.date]:
  return generate_monthrange(inirefmonth, finrefmonth, allow_future=True)


def get_monthrange_as_list(refmonth_ini: Any | None, refmonth_fim: Any | None) -> list[datetime.date]:
  return list(generate_monthrange(refmonth_ini, refmonth_fim))


def getverify_refmonthrangetuple_or_default(p_refmonth_ini: Any | None, p_refmonth_fim: Any | None) -> tuple:
  """
  The default is following:
    if refmonth_fim is None, it will be current_refmonth
    if refmonth_ini is None, it will be refmonth_fim minus one-month
    if refmonth_fim < refmonth_ini, the two will be order-swapped
  """
  refmonth_ini = make_refmonth_or_none(p_refmonth_ini)
  refmonth_fim = make_refmonth_or_current(p_refmonth_fim)
  if refmonth_ini is None:
    refmonth_ini = refmonth_fim - relativedelta(months=1)
  if refmonth_ini <= refmonth_fim:
    return refmonth_ini, refmonth_fim
  # order-swap the two
  return refmonth_fim, refmonth_ini


def strip_m_fr_mmonthd_n_get_nmonth_or_none(mmonth):
  """
  Transforms a mmonth (which is just a monthnumber preceded
    (prefixed) by "M") into a nmonth (the month's number)

  Example:
    ex1
      input -> m9
      output -> 9
    ex2
      input -> m13
      output -> None (13 is outside {1, 12})
  """
  if mmonth is None:
    return None
  try:
    smonth = mmonth.lower().lstrip('m')
    nmonth = int(smonth)
    if 1 > nmonth > 12:
      return None
    return nmonth
  except (AttributeError, TypeError, ValueError) as _:
    pass
  return None


def get_refmonthdate_fr_mmonth_n_year_or_none(mmonth, year):
  """
  Transforms a mmonth (which is just a monthnumber preceded (prefixed) by "M") into a nmonth (the month's number)
    and, complemented with year, returns a refmonthdate

  Example:
    ex1
      input -> (m9, 2024)
      output -> dt(2024, 9, 1)
    ex2
      input -> (m13, 2024)
      output -> None (13 is outside {1, 12})

  """
  if mmonth is None:
    return None
  nmonth = strip_m_fr_mmonthd_n_get_nmonth_or_none(mmonth)
  if nmonth is None:
    return None
  return make_refmonth_w_year_n_month(year, nmonth)


def get_monthslastday_via_calendar_or_raise(pdate: datetime.date) -> int:
  day = get_monthslastday_via_calendar_or_none(pdate)
  if day is None:
    errmsg = f"{pdate} has not a month nor a day"
    raise ValueError(errmsg)
  return day


def get_monthslastday_via_calendar_or_none(pdate: datetime.date | None) -> int | None:
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
  if pdate is None:
    return None
  indate = dfs.make_date_or_none(pdate)
  if indate is None:
    return None
  lastday = get_monthslastday_via_calendar_or_none(pdate)
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
  indate = dfs.make_date_or_none(pdate)
  if indate is None:
    return None
  if indate.day > 1:
    date_set_on_first_day_of_month = datetime.date(indate.year, indate.month, 1)
  else:
    date_set_on_first_day_of_month = indate
  date_on_first_day_of_next_month = date_set_on_first_day_of_month + relativedelta(months=1)
  monthslastday_date = date_on_first_day_of_next_month - relativedelta(days=1)
  return monthslastday_date


def make_refmonth_or_raise(p_refmonth: Any | None) -> datetime.date:
  refmonth = make_refmonth_or_none(p_refmonth)
  if refmonth is None:
    errmsg = f"{p_refmonth} is not a refmonthdate"
    raise ValueError(errmsg)
  return refmonth


def make_next_refmonth_or_raise(refmonth: Any | None) -> datetime.date:
  """
  Notice that a datetime.date object is immutable,
    so there are no outside side effects to worry about
  """
  refmonthdate = make_refmonth_or_raise(refmonth)
  next_refmonthdate = refmonthdate + relativedelta(months=1)
  return next_refmonthdate


def make_datetime_on_day_n_or_none(pdate: Any | None, n: int = 10) -> datetime.date | None:
  indate = dtfs.make_date_or_none(pdate)
  if indate is None:
    return None
  # at this point, indate is type datetime.date
  lastdayinmonth = calendar.monthrange(indate.year, indate.month)[1]
  if 0 > n > lastdayinmonth:
    return None
  odate = datetime.date(year=indate.year, month=indate.month, day=n)
  return odate


def make_datetime_on_day_n_or_raise(pdate: Any | None, n: int = 10) -> datetime.date:
  indate = make_datetime_on_day_n_or_none(pdate)
  if indate is None:
    errmsg = f"{pdate} is not a datetime or day (={n}) is incompatible"
    raise ValueError(errmsg)
  # at this point, indate is type datetime.date
  odate = datetime.date(year=indate.year, month=indate.month, day=n)
  return odate


def make_datetime_on_day_n_or_current(pdate: Any | None, n: int = 10) -> datetime.date:
  indate = make_datetime_on_day_n_or_none(pdate)
  if indate is None:
    indate = datetime.date.today()
  # at this point, indate is type datetime.date
  odate = datetime.date(year=indate.year, month=indate.month, day=n)
  return odate


def make_refmonth_w_year_n_month(year, nmonth):
  if year is None or nmonth is None:
    return None
  try:
    year = int(year)
    nmonth = int(nmonth)
    return datetime.date(year=year, month=nmonth, day=1)
  except ValueError:
    pass
  return None


def make_current_refmonth() -> datetime.date:
  """
  current_refmonth is dt(current_year, current_month, 1)
  Remembering that refmonth is a 'logical' type,
    i.e., it's typed datetime.date with day always equals to 1

  today = datetime.date.today()
  current_refmonthdate = datetime.date(year=today.year, month=today.month, day=1)
  return current_refmonthdate
  """
  today = datetime.date.today()
  current_refmonth = datetime.date(year=today.year, month=today.month, day=1)
  return current_refmonth


def make_refmonth_or_current_it_minus_n(p_refmonth: datetime.date | None, n: int = 2) -> datetime.date | None:
  """
  @see __doc__ for the next function
  """
  refmonth = make_refmonth_or_current(p_refmonth)
  refmonth_m_minus_n = refmonth - relativedelta(months=n)
  return refmonth_m_minus_n


def make_refmonth_it_minus_n(p_refmonth: datetime.date | None, n: int = 2) -> datetime.date | None:
  """
  Calculates the M - n refmonth where:
   M is the refmonthdate itself (or the current one if not given)
   n is an integer representing how many months before

  Example: the M-2 case
  =====================
    The M-2 type is a refmonthdate
      two months before the given (or current) refmonthdate
  """
  refmonth = make_refmonth_or_none(p_refmonth)
  if refmonth is None:
    return None
  refmonth_m_minus_n = refmonth - relativedelta(months=n)
  return refmonth_m_minus_n


def get_refmonth_fr_obj_impl_year_month_or_none(p_refmonth):
  if p_refmonth is None:
    return None
  try:
    if hasattr(p_refmonth, 'year'):
      year = int(p_refmonth.year)
      if hasattr(p_refmonth, 'month'):
        month = int(p_refmonth.year)
        return datetime.date(year=year, month=month, day=1)
  except ValueError:
    pass
  try:
    year = int(p_refmonth['year'])
    month = int(p_refmonth['month'])
    return datetime.date(year=year, month=month, day=1)
  except (KeyError, TypeError, ValueError):
    pass
  try:  # try without sep's
    _ = int(p_refmonth)
    # okay, str is composed of numberfs without sep's
    pstr = p_refmonth[:6]
    year = int(pstr[:4])
    month = int(pstr[4:6])
    return datetime.date(year=year, month=month, day=1)
  except ValueError:
    pass
  try:  # try with sep's
    sepfound = None
    pstr = str(p_refmonth)
    for sep in ['/', '-', '.']:
      if sep in pstr:
        sepfound = sep
    if sepfound is None:
      return None
    pp = pstr.split(sepfound)
    year = int(pp[0])
    month = int(pp[1])
    return datetime.date(year=year, month=month, day=1)
  except (IndexError, ValueError):
    pass
  return None


def make_refmonth_or_none(p_refmonth: Any | None) -> datetime.date | None:
  """
  Notice: refmonth or refmonthdate objects are datetime.date objects (logically) having day equal to 1

  This function relies on make_date_or_none() but, failing that, it still has to check the string cases:
    'yyyymm' | 'yyyy[sep]m[m]', which it does by calling recup_year_month_or_none(p_refmonth)
  """
  if p_refmonth is None:
    return None
  refmonth = dtfs.make_date_or_none(p_refmonth)
  if refmonth is None:
    # do not return yet, try cases 'yyyymm' | 'yyyy[sep]m[m]'
    refmonth = get_refmonth_fr_obj_impl_year_month_or_none(p_refmonth)
    if refmonth is None:
      return None
  if refmonth.day == 1:
    # return right-away
    return refmonth
  # adjust day to 1 (a refmonth is a date on day 1)
  refmonth = datetime.date(year=refmonth.year, month=refmonth.month, day=1)
  return refmonth


def make_refmonth_or_current(p_refmonth: Any | None) -> datetime.date:
  refmonth = make_refmonth_or_none(p_refmonth)
  if refmonth is not None:
    return refmonth
  # at this point, make current refmonth, i.e., today's date with day set to 1
  today = datetime.date.today()
  refmonth = datetime.date(year=today.year, month=today.month, day=1)
  return refmonth


def make_refmonth_ini_n_fim_w_year_forbid_future(year=None):
  today = datetime.date.today()
  if year is None:
    year = today.year
  if year > today.year:
    return None, None
  refmonth_ini = make_refmonth_w_year_n_month(year, 1)
  if year >= today.year:
    month_to = today.month if today.month < 12 else 12
  else:
    month_to = 12
  refmonth_fim = make_refmonth_w_year_n_month(year, month_to)
  return refmonth_ini, refmonth_fim


def gen_refmonthrange_w_year_or_currentyear(year=None):
  inirefmonth, finrefmonth = make_refmonthtuple_w_year_or_currentyear(year)
  cur_refmonth = copy.copy(inirefmonth)
  while cur_refmonth <= finrefmonth:
    yield cur_refmonth
    cur_refmonth += relativedelta(months=1)
  return


def make_refmonthtuple_w_year_or_currentyear(year=None) -> tuple:
  today = datetime.date.today()
  if year is None:
    year = today.year
  refmonth_ini = make_refmonth_w_year_n_month(year, 1)
  refmonth_fim = make_refmonth_w_year_n_month(year, 12)
  return refmonth_ini, refmonth_fim


def gen_refmonthtuple_w_yeartuple(yearini, yearfim=None, allow_future=False) -> Iterator[datetime.date]:
  inirefmonth, finrefmonth = make_refmonthtuple_w_yearsinifin(yearini, yearfim, allow_future)
  if (inirefmonth, finrefmonth) == (None, None):
    return iter(())
  return generate_monthrange(inirefmonth, finrefmonth, allow_future)


def make_refmonthtuple_w_yearsinifin(yearini, yearfim=None, allow_future=False):
  today = datetime.date.today()
  if yearini is None:
    return None, None
  if yearfim is None:
    yearfim = today.year
  try:
    yearini = int(yearini)
    yearfim = int(yearfim)
    if not allow_future:
      yearini = yearini if yearini <= today.year else today.year
      yearfim = yearfim if yearfim <= today.year else today.year
    # swap if needed
    if yearini > yearfim:
      tmpyear = yearini
      yearini = yearfim
      yearfim = tmpyear
  except ValueError:
    return None, None
  inirefmonth = datetime.date(year=yearini, month=1, day=1)
  finrefmonth = datetime.date(year=yearfim, month=12, day=1)
  if not allow_future:
    current_refmonth = make_current_refmonth()
    if inirefmonth > current_refmonth:
      return None, None
    if finrefmonth > current_refmonth:
      # cut it off on current_refmonth
      finrefmonth = current_refmonth
  return inirefmonth, finrefmonth


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


def transform_year_into_refmonthrange_private(year: int) -> tuple:
  """
  private is the sense that only functions inside this module should call it
  The _private in function name here guarantees year is an int.
    So do not call this function outside of this module (though Python does not enforce this rule).
  """
  refmonthdate_ini = datetime.date(year=year, month=1, day=1)
  refmonthdate_fim = datetime.date(year=year, month=12, day=1)
  return refmonthdate_ini, refmonthdate_fim


def transform_year_into_refmonthrange(year: int) -> tuple:
  try:
    int_year = int(year)
    return transform_year_into_refmonthrange_private(int_year)
  except (TypeError, ValueError):
    # TypeError covers year is None
    # ValueError covers it's not convertible to int
    pass
  return None, None


def transform_year_into_refmonthrange_or_recent_year(year=None):
  rdmrange = transform_year_into_refmonthrange(year)
  if rdmrange is not None:
    return rdmrange
  today = datetime.date.today()
  return transform_year_into_refmonthrange_private(today.year)


def spawn_inidate_n_fimdate_fr_refmonth(refmonthdate: datetime.date | None) -> tuple:
  if refmonthdate is None:
    return None, None
  inidate = refmonthdate  # notice datetime.date 'variables' are immutable
  last_day_in_month = get_monthslastday_via_calendar_or_raise(refmonthdate)
  try:
    fimdate = datetime.date(year=inidate.year, month=inidate.month, day=last_day_in_month)
    return inidate, fimdate
  except AttributeError:
    pass
  return None, None


def transform_refmonthlist_to_a_daterangetuple(refmonthlist):
  """
  Transform a refmonth list into a daterange tuple,
    generally this operation produces a more inclusive date range.

  The input dates do not list to conform to refmonth constraint,
    any date will be reinterpreted as its equivalent refmonth
    (@see the first filter() below).

  Caution:

      If there are gaps within inirefmonth and finrefmonth as
      months not represented in the incoming list,
      they will be tacitly included in the daterange tuple.

  Example:
    input = [dt(2024, 1, 15), '2023-1-7', dt(2024, 3, 21)]
  After processing:
    output = [dt(2023, 1, 1), dt(2024, 3, 31)]

  i.e., the date range will include, logically,
    dates not in the original list.
  """
  if refmonthlist is None or len(refmonthlist) == 0:
    return ()
  as_date_list = map(lambda o: make_refmonth_or_none(o), refmonthlist)
  as_date_list = filter(lambda o: make_refmonth_or_none(o) is not None, as_date_list)
  as_date_list = list(as_date_list)
  if len(as_date_list) == 0:
    return ()
  as_date_list.sort()
  inidate = as_date_list[0]
  finrefmonth = as_date_list[-1]
  lastdayinmonth = calendar.monthrange(finrefmonth.year, finrefmonth.month)[1]
  findate = datetime.date(year=finrefmonth.year, month=finrefmonth.month, day=lastdayinmonth)
  daterange = (inidate, findate)
  return daterange


def process():
  """
  This module contains library functions
  """
  print('This module contains library functions')


def adhoctest1():
  print('The adhoctests are in its separated module.')


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
