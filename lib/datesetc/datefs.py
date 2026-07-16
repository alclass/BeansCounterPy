#!/usr/bin/env python3
""""
lib/datesetc/datefs.py
  Module with date & time (helper) functions
  BeansCounterPy_PrdPrj

"""
from collections.abc import Iterator
import copy
import datetime
from typing import Any
import lib.datesetc as init  # init.ALLOWED_DATE_SEPARATORS
ALLOWED_DATE_SEPARATORS = init.ALLOWED_DATE_SEPARATORS


def str_has_char_in_list(p_str, str_or_list):
  bool_list = list(map(lambda c: c in str_or_list, p_str))
  if True in bool_list:
    return True
  return False


def date_to_str_4y_dash_2m_dash_2d(pdate: datetime.date | None) -> str | None:
  """
  Stringifies datetime.date objects
    but also any object that has attributes (implements the interface) year, month, day
    (these conversions are done via reuse function make_make_date_or_none())

  Application:
    a1 any string (str) use
    a2 for JSON serializing datetime.date once json.dumps() needs passing a serializing function
  """
  if pdate is None:
    return None
  # 1st try: pass it to make_date_or_none(), if None, pass ahead to 2nd try, if not None, form the returing string
  pdate = make_date_or_none(pdate)
  if pdate is None:
    return None
  try:
    # at this point, pdate is either None or of type datetime.date
    # if None, the AttributeError raised jumps over this chunk (try-block)
    year, month, day = pdate.year, pdate.month, pdate.day
    strdate = f"{year}-{month:02d}-{day:02d}"
    return strdate
  except AttributeError:
    # basically pdate got None
    pass
  return None


def transform_strdate_yyyymmdd_to_date_sep_by(strdate, sepchar='-'):
  try:
    strdate = str(strdate)
    pp = strdate.split(sepchar)
    yyyy = int(pp[0])
    mm = int(pp[1])
    dd = int(pp[2])
    outdate = datetime.date(year=yyyy, month=mm, day=dd)
    return outdate
  except (IndexError, ValueError) as _:
    pass
  return None


def transform_strdate_ddmmyyyy_to_date_sep_by(strdate, sepchar='/'):
  try:
    strdate = str(strdate)
    pp = strdate.split(sepchar)
    dd = int(pp[0])
    mm = int(pp[1])
    yyyy = int(pp[2])
    outdate = datetime.date(year=yyyy, month=mm, day=dd)
    return outdate
  except (IndexError, ValueError) as _:
    pass
  return None


def transform_strdate_mmddyyyy_to_date_sep_by(strdate, sepchar='/'):
  try:
    strdate = str(strdate)
    pp = strdate.split(sepchar)
    mm = int(pp[0])
    dd = int(pp[1])
    yyyy = int(pp[2])
    outdate = datetime.date(year=yyyy, month=mm, day=dd)
    return outdate
  except (IndexError, ValueError) as _:
    pass
  return None


def inspect_n_get_sepchar_in_strdate(strdate):
  if strdate.find('-') > -1:
    return '-'
  if strdate.find('/') > -1:
    return '/'
  if strdate.find('.') > -1:
    return '.'
  return ''


def inspect_n_get_datewsep_fieldorder_fr_str(strdate):
  """
  Inspects the logical positions of yyyy, mm, and mm from a strdate and returns
    a tuple with the position-marker string and the datetime.date object derived

  History:
    In the first version of this function, the datetime.date was not returned, but
    as it had to be instanciated because of verifying its consistency,
    datetime.date became also returned.

  This function tries to find the ordering yyyymmdd, ddmmyyyy, etc.
    by inferring int's from the string.
  However, this logic imposes some limitations, they are:
    limitation 1 - the incoming string must have 10 digits, the separator character is not inspected here
    limitation 2 - year must have 4 integer digits
                   if year begins the string, date can only be yyyymmdd, not yyyyddmm,
                   in this case, it's a convention set here
    limitation 3 - year is never in the middle, another convention, it's either in the beginning or the end
    limitation 4 - when differentiating day and month, day must be greater than 12, except in yyyymmdd,
                   otherwise their positions are unconclusive (@see algorithm below inside function)
    limitation 5 - dd (day) and mm (month) must have 2 digits each
  """
  if strdate is None or len(strdate) != 10:
    return None, None
  try:
    # for this 1st try, year is in the beginning of the string
    year = int(strdate[:4])  # [0123] - 56 - 89
    # when year is first, positions can only be, by convention, yyyymmdd (not yyyyddmm)
    # so there is no unconclusiveness if both day and month are less than 13
    # but the whole date (the fields altogether) must still be consistent
    month = int(strdate[5:7])  # [0123] - 56 - 89
    day = int(strdate[8:10])  # [0123] - 56 - 89
    # datetime, if date is inconsistent, raises ValueError
    pdate = datetime.date(year=year, month=month, day=day)
    return 'yyyymmdd', pdate
  except ValueError:
    pass  # on for the next try
  try:
    # in this 2nd try, year must end the string
    # (by convention, it starts or ends the string, year is never in the middle)
    year = int(strdate[6:10])
    leftmost = int(strdate[0:2])  # [01] - 34 - 6789
    if leftmost > 12:  # it can only be ddmmyyyy
      # guarantee that fields are integer and month is within range
      day = leftmost
      month = int(strdate[3:5])
      pdate = datetime.date(year=year, month=month, day=day)
      return 'ddmmyyyy', pdate
    middle = int(strdate[3:5])  # 01 - [34] - 6789
    if middle > 12:
      day = middle
      month = int(strdate[0:2])
      pdate = datetime.date(year=year, month=month, day=day)
      return 'mmddyyyy', pdate
    # at this point, both day and month are less than 13,
    # so positions are unconclusive in the definition of the marker:
    # doubt between ddmmyyyy or mmddyyyy
    unconclusive_marker = None
    if leftmost == middle:
      dd_mm_equal = middle
      pdate = datetime.date(year=year, month=dd_mm_equal, day=dd_mm_equal)
      return unconclusive_marker, pdate
  except ValueError:
    pass
  return None, None


def transform_strdate_to_date_with_fieldpos(strdate, fieldpos='yyyymmdd', sepchar=None):
  if sepchar is None:
    sepchar = inspect_n_get_sepchar_in_strdate(strdate)
  if fieldpos == 'yyyymmdd':
    return transform_strdate_yyyymmdd_to_date_sep_by(strdate, sepchar)
  elif fieldpos == 'ddmmyyyy':
    return transform_strdate_ddmmyyyy_to_date_sep_by(strdate, sepchar)
  elif fieldpos == 'mmddyyyy':
    return transform_strdate_mmddyyyy_to_date_sep_by(strdate, sepchar)
  return None


def transform_strdate_to_date_with_fieldpos_n_sep(strdate, fieldpos='yyyymmdd', sepchar='-'):
  if strdate is None:
    return None
  strdate = str(strdate)
  if len(strdate) == 10:
    return transform_strdate_to_date_with_fieldpos(strdate, fieldpos, sepchar)
  if len(strdate) not in [8, 9, 10]:
    return None
  # it's possible to be missing some "left zero" eg 1/1/yyyy should be 01/01/yyyy
  pp = strdate.split(sepchar)
  if fieldpos.startswith('yyyy'):
    changed = False
    if len(pp[1]) == 1:
      pp[1] = '0' + pp[1]
      changed = True
    if len(pp[2]) == 1:
      pp[2] = '0' + pp[2]
      changed = True
    if not changed:
      # unconclusive
      return None
    strdate = sepchar.join(pp)
    if len(strdate) != 10:
      return None
    else:
      return transform_strdate_to_date_with_fieldpos(strdate, fieldpos, sepchar)
  # at this point on, fieldpos is either ddmmyyyy or mmddyyyy, both are treated equally
  changed = False
  if len(pp[0]) == 1:
    pp[0] = '0' + pp[0]
    changed = True
  if len(pp[1]) == 1:
    pp[1] = '0' + pp[1]
    changed = True
  if not changed:
    # unconclusive
    return None
  strdate = sepchar.join(pp)
  if len(strdate) != 10:
    return None
  else:
    return transform_strdate_to_date_with_fieldpos(strdate, fieldpos, sepchar)


def make_date_or_none(pdate: Any | None) -> datetime.date | None:
  """
  """
  if pdate is None:
    return None
  if isinstance(pdate, datetime.date):
    # if it's alreay a datetime.date, return it back right away
    return pdate

  # 1st try: pdate may implement integer-convertible attributes year, month, day
  # the 'interface check (and get)' (year, month, day)
  odate = transform_obj_impl_year_month_day_to_date(pdate)
  if odate is not None:
    return odate
  # pdate was not mutated in the former function
  return transform_strdate_to_date(pdate)


def make_date_or_raise(pdate: Any | None) -> datetime.date:
  if pdate is not None:
    odate = make_date_or_none(pdate)
    if odate is not None:
      return odate
  # falling back here means either pdate is None (first 'if' False) or odate is None (second 'if' False)
  errmsg = f"{pdate} is not transformable to Python-date"
  raise ValueError(errmsg)


def make_date_or_today(pdate: Any | None) -> datetime.date:
  odate = make_date_or_none(pdate)
  if odate is None:
    today = datetime.date.today()
    return today
  return odate


def transform_obj_impl_year_month_day_to_date(impl_obj: Any) -> datetime.date | None:
  """
  Tries to instantiate a datetime.date either from?
    1 an object that 'implements' year, month, day
    2 a dict-like object that contains keys 'year', 'month', 'day'

  """
  try:  # 1st try tries to get date from an object implementing year, month, day
    year = int(impl_obj.year)
    month = int(impl_obj.month)
    day = int(impl_obj.day)
    pdate = datetime.date(year=year, month=month, day=day)
    return pdate
  except (AttributeError, TypeError, ValueError):
    # AttributeError if impl_obj is None
    # TypeError if an attribute of impl_obj is None
    # ValueError if an attribute is not int-convertible
    pass
  try:  # 2nd try tries to get date from a dict-like object having keys 'year', 'month', 'day'
    year = int(impl_obj['year'])
    month = int(impl_obj['month'])
    day = int(impl_obj.day['day'])
    pdate = datetime.date(year=year, month=month, day=day)
    return pdate
  except (KeyError, TypeError, ValueError):
    # KeyError if impl_obj['key'] does not have the key
    # TypeError if an attribute of impl_obj is None
    # ValueError if an attribute is not int-convertible
    pass
  return None


def inspect_datefieldorder_by_sep(sep: str, strdate: str | None) -> tuple:
  """
  If datetime.date is obtainable, return it also

  Conventions:
    1 if year begins string, field order is yyyymmdd
    2 year is never in the middle position (i.e., aayyyyaa does not exist)
    3 when year ends strings, it can either be ddmmyyyy or mmddyyyy
      an ambiguity may happen here only if both day and month are less than 13 and not equal

  Limitations:
    1 if all fields are less than 31, date cannot be inferred
    2 as 3 above, there may be ambigyity when year ends string
    The two ambigyities above makes this return (None, None)

    @see also cases/hypotheses in the unittest for this function
  """
  if strdate is None:
    return None, None
  try:
    pp = strdate.split(sep)
    year = int(pp[0])
    month = int(pp[1])
    day = int(pp[2])
    if year > 31:
      # the convention when year begins string requires yyyymmdd
      # no ambiguity here
      pdate = datetime.date(year=year, month=month, day=day)
      ret_tuple = ('yyyymmdd', pdate)
      return ret_tuple
    pos1, pos2, pos3 = year, month, day
    if pos3 > 31:
      # need to know where day and month are
      if pos1 > 12 and pos2 < 13:
        year, month, day = pos3, pos2, pos1
        pdate = datetime.date(year=year, month=month, day=day)
        ret_tuple = ('ddmmyyyy', pdate)
        return ret_tuple
      elif pos2 > 12 and pos3 < 13:
        year, month, day = pos2, pos1, pos3
        pdate = datetime.date(year=year, month=month, day=day)
        ret_tuple = ('ddmmyyyy', pdate)
        return ret_tuple
  except (AttributeError, IndexError, ValueError):
    pass
  ret_tuple = None, None
  return ret_tuple


def transform_strdate_to_date_wo_seps(strdate: str) -> datetime.date | None:
  """
  Transforms a str to date under the following hypothesis:
    h1 string must have 8 number digits
    h2 under the convention yyyymmdd (this is a convention the called must abide to)

  On object mutation:
    strdate is not mutated (on the) outside
    (and also Python str's are immutable)
  """
  if strdate and len(strdate) != 8:
    return None
  if str_has_char_in_list(strdate, ALLOWED_DATE_SEPARATORS):
    # this is an 'explanatory' check, logically the try below would take care of this part
    return None
    # there is only one option if it's 8-char and no separators
  try:
    year = int(strdate[0:4])
    month = int(strdate[4:6])
    day = int(strdate[6:8])
    pdate = datetime.date(year=year, month=month, day=day)
    return pdate
  except (IndexError, ValueError):
    pass
  return None


def transform_strdate_to_date(strdate: Any | None) -> datetime.date | None:
  """
  The ending part of this function may be obsolete.
  A unittest has been created and some adhoctests also.
  TODO clean up the ending of this function and rerun the tests.
  """
  if strdate is None:
    return None
  try:
    strdate = str(strdate)
    strdate = strdate.strip(' \t\r\n')
    if 8 > len(strdate) > 10:
      return None
    pdate = transform_strdate_to_date_wo_seps(strdate=strdate)
    if pdate is not None:
      return pdate
    # client caller in case of dates such as 1/1/yyyy should call transform_strdate_to_date_with_fieldpos()
    sep = inspect_n_get_sepchar_in_strdate(strdate=strdate)
    ordermarker, pdate = inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    if pdate is not None:
      return pdate
    # strdate = txfs.cleanup_str_leaving_only_numbers_or_dashes(strdate)
    # the next 'if' is to stop the IDE from complaining that strdate might be None
    fieldpos, pdate = inspect_n_get_datewsep_fieldorder_fr_str(strdate)
    if pdate is not None:
      # in the updated version of 'inspect', datetime.date was included in its return
      return pdate
    if fieldpos is None:
      # yyyymmdd or mmddyyyy or ddmmyyyy could not be found
      return None
    # it's possible that function 'inspect' will already have date returned by this point
    # the code below is a kind of 'legacy'
    sepchar = inspect_n_get_sepchar_in_strdate(strdate)
    if fieldpos == 'yyyymmdd':
      return transform_strdate_yyyymmdd_to_date_sep_by(strdate, sepchar)
    elif fieldpos == 'ddmmyyyy':
      return transform_strdate_ddmmyyyy_to_date_sep_by(strdate, sepchar)
    elif fieldpos == 'mmddyyyy':
      return transform_strdate_mmddyyyy_to_date_sep_by(strdate, sepchar)
  except (IndexError, ValueError):
    pass
  return None


def transform_strdate_to_date_or_today(strdate=None):
  pdate = transform_strdate_to_date(strdate)
  if pdate is None:
    return datetime.date.today()
  return pdate


def transform_yyyydashmm_to_date(strdate):
  try:
    pp = strdate.split('-')
    yyyy = int(pp[0])
    mm = int(pp[1])
    outdate = datetime.date(year=yyyy, month=mm, day=1)
    return outdate
  except (AttributeError, IndexError, ValueError) as _:
    pass
  return None


def transform_yyyydashmm_to_daterange_from_strlist(yyyydashmmstrlist):
  """

  """
  try:
    yyyydashmmstrlist = list(yyyydashmmstrlist)
    if None in yyyydashmmstrlist:
      # this variable may be itself a list, okay, but
      # inside there may be None's, so this 'if' is necessary for caughting the excepting
      raise TypeError
  except (TypeError, ValueError):  # TypeError covers year is None, ValueError covers it's not convertible to int
    return None
  refmonth_range_list = []
  for yyyydashmm in yyyydashmmstrlist:
    refmonthdate = transform_yyyydashmm_to_date(yyyydashmm)
    refmonth_range_list.append(refmonthdate)
  return list(refmonth_range_list)


def transform_yyyydashmm_to_daterange_from_strlist_or_recentyear(yyyydashmmstrlist):
  """
  This function should be moved to module refmonth_fs
  """
  refmonth_list = transform_yyyydashmm_to_daterange_from_strlist(yyyydashmmstrlist)
  if refmonth_list is not None:
    return refmonth_list
  # the commented function below is not here anymore
  # return transform_year_into_refmonthrange_or_recent_year()
  return []


def transform_yyyydashmm_to_daterange_in_refmonth_dict(str_refmonth_range_dict):
  refmonth_range_dict = {}
  for e in str_refmonth_range_dict:
    yyyydashmm = str_refmonth_range_dict[e]
    refmonth_range_dict[e] = transform_yyyydashmm_to_date(yyyydashmm)
  return refmonth_range_dict


def transform_strdate_or_yyyymm_to_date_day1(pdate):
  if pdate is None:
    return None
  if isinstance(pdate, datetime.date):
    if pdate.day == 1:
      return pdate
    return datetime.date(year=pdate.year, month=pdate.month, day=1)
  try:
    pdate = str(pdate).strip(' \t\r\n')
    ppp = pdate.split(' ')
    pp = ppp[0].split('-')
    year = int(pp[0])
    month = int(pp[1])
    pdate = datetime.date(year=year, month=month, day=1)
    return pdate
  except ValueError:
    pass
  return None


def return_date_or_recup_it_from_str(pdate):
  if pdate is None:
    return None
  if isinstance(pdate, datetime.date):
    return pdate
  try:
    pdate = str(pdate)
    pp = pdate.split('-')
    year = int(pp[0])
    month = int(pp[1])
    pdate = datetime.date(year=year, month=month, day=1)  # in case str is just yyyy-mm, ie it misses -dd
    try:
      day = int(pp[2])
      pdate = datetime.date(year=year, month=1, day=day)
      return pdate
    except (IndexError, ValueError):
      return pdate
  except (IndexError, ValueError):
    pass
  return None


def datetostr(pdate: datetime.date | None) -> str | None:
  """
  return datetime.date.strftime(pdate, '%Y-%m-%d')
  """
  return date_to_str_4y_dash_2m_dash_2d(pdate)


def gen_dailydates_wi_daterangetuple(p_daterangetuple: tuple) -> Iterator[datetime.date]:
  """
    Generates all daily dates within a date range,
      i.e., all daily dates inclusive between (inidate, findate)

  Example:
    p_daterangetuple = ('2024-1-1', '2024-1-7')
  The generated output (list) will be:
    ['2024-1-1', '2024-1-2', '2024-1-3', ..., '2024-1-7']
      i.e., all daily dates inclusive between ('2024-1-1', '2024-1-7')
  """
  if p_daterangetuple is None:
    return
  p_daterangetuple = list(p_daterangetuple)
  dtrange = map(lambda o: make_date_or_none(o), p_daterangetuple)
  dtrange = filter(lambda o: o is not None, dtrange)
  dtrange = list(dtrange)
  if len(dtrange) != 2:
    return
  dtrange.sort()
  inidate = dtrange[0]
  findate = dtrange[-1]
  curdate = copy.copy(inidate)
  while curdate <= findate:
    yield curdate
    curdate += datetime.timedelta(days=1)
  return



def adhoctest1():
  scrmsg = """The adhoctests were moved to their own module in subpackage 'adhoctests'.
  The unit-tests are also in their own module and subpackage ('unittests')."""
  print(scrmsg)


def process():
  pass


if __name__ == '__main__':
  """
  adhoctest1()
  process()
  """
  adhoctest1()
