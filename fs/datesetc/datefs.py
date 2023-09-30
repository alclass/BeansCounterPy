#!/usr/bin/env python3
""""
datefs.py
  Module with date & time (helper) functions
"""
import datetime
from dateutil.relativedelta import relativedelta


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


def inspect_sepchar_in_strdate(strdate):
  if strdate.find('-') > -1:
    return '-'
  if strdate.find('/') > -1:
    return '/'
  if strdate.find('.') > -1:
    return '.'
  return ''


def inspect_yyyyddmm_positions_in_strdate(strdate):
  try:
    _ = int(strdate[:4])  # [0123] 4 56 7 89
    # when year is first, it can only be yyyymmdd (not yyyyddmm)
    return 'yyyymmdd'
  except ValueError:
    pass
  try:
    leftmost = int(strdate[0:2])  # [01] 2 34 5 6789
    if leftmost > 12:  # it can only be ddmmyyyy
      return 'ddmmyyyy'
  except ValueError:
    pass
  try:
    middle = int(strdate[3:5])  # 01 2 [34] 5 6789
    if middle > 12:  # it can only be ddmmyyyy
      return 'mmddyyyy'
    # in doubt, fallback to ddmmyyyy
    return 'ddmmyyyy'
  except ValueError:
    pass
  # unconclusive
  return None


def transform_strdate_to_date_with_fieldpos(strdate, fieldpos='yyyymmdd', sepchar=None):
  if sepchar is None:
    sepchar = inspect_sepchar_in_strdate(strdate)
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


def transform_strdate_to_date(strdate):
  if strdate is None:
    return None
  if type(strdate) == datetime.date:
    return strdate
  try:
    strdate = str(strdate)
    if len(strdate) != 10:
      # client caller in case of dates such as 1/1/yyyy should call transform_strdate_to_date_with_fieldpos()
      return None
    sepchar = inspect_sepchar_in_strdate(strdate)
    fieldpos = inspect_yyyyddmm_positions_in_strdate(strdate)
    if fieldpos is None:
      # yyyymmdd or mmddyyyy or ddmmyyyy could not be found
      return None
    if fieldpos == 'yyyymmdd':
      return transform_strdate_yyyymmdd_to_date_sep_by(strdate, sepchar)
    elif fieldpos == 'ddmmyyyy':
      return transform_strdate_ddmmyyyy_to_date_sep_by(strdate, sepchar)
    elif fieldpos == 'mmddyyyy':
      return transform_strdate_mmddyyyy_to_date_sep_by(strdate, sepchar)
  except (IndexError, ValueError) as _:
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


def transform_yyyydashmm_to_daterange_in_refmonth_dict(str_refmonth_range_dict):
  refmonth_range_dict = {}
  for e in str_refmonth_range_dict:
    yyyy_mm = str_refmonth_range_dict[e]
    refmonth_range_dict[e] = transform_yyyydashmm_to_date(yyyy_mm)
  return refmonth_range_dict


def test_some():
  # 1 pass None
  pdate = transform_strdate_to_date_or_today()
  print('None =>', pdate)
  # 2 pass a dd/mm/yyyy
  strdate = '1/1/1999'
  pdate = transform_strdate_to_date_or_today(strdate)
  print(strdate, ' =>', pdate)
  # 3 pass a non-consistent date dd/mm/yyyy expecting None (may go to unittest later on)
  strdate = '31/11/2999'
  pdate = transform_strdate_to_date(strdate)
  print(strdate, ' =>', pdate)
  # 4 pass a consistent date (though welll in the future) dd/mm/yyyy expecting a valid date
  strdate = '31/10/2999'
  pdate = transform_strdate_to_date(strdate)
  print(strdate, ' =>', pdate)


def validate_refmonthdate_or_none(refmonthdate=None):
  if refmonthdate is None:
    return None
  if type(refmonthdate) != datetime.date:
    refmonthdate = transform_strdate_to_date(str(refmonthdate))
  if refmonthdate.day != 1:
    return datetime.date(refmonthdate.year, refmonthdate.month, 1)
  return refmonthdate


def validate_refmonthdate_or_morerecent(refmonthdate=None):
  """
  refmonthdate is a date that has day=1
  """
  if refmonthdate is None:
    refmonthdate = datetime.date.today()
    return validate_refmonthdate_or_morerecent(refmonthdate)
  if type(refmonthdate) != datetime.date:
    refmonthdate = transform_strdate_to_date_or_today(str(refmonthdate))
  if refmonthdate.day != 1:
    return datetime.date(refmonthdate.year, refmonthdate.month, 1)
  return refmonthdate


def validate_refmonthdate_ini_fim_or_1monthbefore(refmonthdate_ini, refmonthdate_fim):
  """"
  There are 2 rules to be followed here:
    r1 refmonthdates are dates that have day=1
    r2 for one to be less than the other, if dateini is equal or more than datefim, suffice have ini = fim - 1month
  """
  refmonthdate_fim = validate_refmonthdate_or_morerecent(refmonthdate_fim)
  refmonthdate_ini = validate_refmonthdate_or_none(refmonthdate_ini)
  if refmonthdate_ini >= refmonthdate_fim:
    # notice both dates have day=1, so, if ini is equal or more,
    # suffice have ini be fim diminished from one month
    refmonthdate_ini = refmonthdate_fim - relativedelta(months=1)
  return refmonthdate_ini, refmonthdate_fim


if __name__ == '__main__':
  test_some()
