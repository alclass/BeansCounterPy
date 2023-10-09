#!/usr/bin/env python3
""""
datefs.py
  Module with date & time (helper) functions
"""
import copy
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
  refmonth_list = transform_yyyydashmm_to_daterange_from_strlist(yyyydashmmstrlist)
  if refmonth_list is not None:
    return refmonth_list
  return transform_year_into_refmonthrange_or_recent_year()


def transform_yyyydashmm_to_daterange_in_refmonth_dict(str_refmonth_range_dict):
  refmonth_range_dict = {}
  for e in str_refmonth_range_dict:
    yyyydashmm = str_refmonth_range_dict[e]
    refmonth_range_dict[e] = transform_yyyydashmm_to_date(yyyydashmm)
  return refmonth_range_dict


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


def validate_refmonthdate_or_1monthbefore_the_2ndparam(refmonthdate_ini, refmonthdate_fim):
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


def make_date_with_day1(pdate=None):
  if pdate is None:
    pdate = datetime.date.today()
  if type(pdate) != datetime.date:
    try:
      pdate = str(pdate)
      pdate = transform_strdate_to_date(pdate)
      if pdate is None:
        pdate = datetime.date.today()
    except ValueError:
      pdate = datetime.date.today()
  if pdate.day == 1:
    return pdate
  odate = datetime.date(year=pdate.year, month=pdate.month, day=1)
  return odate


def make_refmonthdate_from_conventioned_filename(conventioned_filename):
  try:
    pp = conventioned_filename.split(' ')
    yearmonth = pp[0]
    ppp = yearmonth.split('-')
    year = int(ppp[0])
    month = int(ppp[1])
    refmonthdate = datetime.date(year, month, day=1)
    return refmonthdate
  except (AttributeError, IndexError, ValueError):
    pass
  return None


def generate_monthrange(refmonthdate_ini=None, refmonthdate_fim=None):
  refmonthdate_ini = make_date_with_day1(refmonthdate_ini)
  refmonthdate_fim = make_date_with_day1(refmonthdate_fim)
  today = datetime.date.today()
  refmonthtoday = make_date_with_day1(today)
  if refmonthdate_fim > refmonthtoday:
    refmonthdate_fim = refmonthtoday
  if refmonthdate_ini > refmonthtoday:
    return []
  if refmonthdate_ini > refmonthdate_fim:
    return []
  if refmonthdate_ini == refmonthdate_fim:
    return [refmonthdate_ini]
  current_refmonthdate = copy.copy(refmonthdate_ini)
  while current_refmonthdate <= refmonthdate_fim:
    yield current_refmonthdate
    current_refmonthdate = current_refmonthdate + relativedelta(months=1)
  return


def transform_year_into_refmonthrange_private(year):
  """
  The _private in function name here guarantees year is an int.
    So do not call this function outside of this module (though Python does not enforce this rule).
  """
  refmonthdate_ini = datetime.date(year=year, month=1, day=1)
  refmonthdate_fim = datetime.date(year=year, month=12, day=1)
  return refmonthdate_ini, refmonthdate_fim


def transform_year_into_refmonthrange(year):
  try:
    int_year = int(year)
    return transform_year_into_refmonthrange_private(int_year)
  except (TypeError, ValueError):  # TypeError covers year is None, ValueError covers it's not convertible to int
    pass
  return None


def transform_year_into_refmonthrange_or_recent_year(year=None):
  rdmrange = transform_year_into_refmonthrange(year)
  if rdmrange is not None:
    return rdmrange
  today = datetime.date.today()
  return transform_year_into_refmonthrange_private(today.year)


def adhoctest_some_yyyydashmm_dates():
  """
  print('test_some_yyyydashmm_dates')
  strdaterange_tuplelist = [('2022-04', '2023-04'), ('2018-10', '2020-01')]
  for strdaterange_tuple in strdaterange_tuplelist:
    monthref_ini = strdaterange_tuple[0]
    monthref_fim = strdaterange_tuple[1]
    strdaterange_dict = {'monthref_ini': monthref_ini, 'monthref_fim': monthref_fim}
    daterange_dict = transform_yyyydashmm_to_daterange_in_refmonth_dict(strdaterange_dict)
    print(strdaterange_dict, '=>', daterange_dict

  """
  refmonthdate_ini = '2023-01-15'
  refmonthdate_fim = '2023-08-11'
  generator = generate_monthrange(refmonthdate_ini=refmonthdate_ini, refmonthdate_fim=refmonthdate_fim)
  src_msg = 'adhoc test generator refmonthdate_ini = %s, refmonthdate_ini = %s' % (refmonthdate_ini, refmonthdate_fim)
  print(src_msg)
  for i, refmonthdate in enumerate(generator):
    seq = i + 1
    print(seq, refmonthdate)
  print('transform_year_into_refmonthrange_or_recent_year()')
  rdmrange = transform_year_into_refmonthrange_or_recent_year()
  print('\t', rdmrange)
  yyyydashmms = ('2023-01', '2023-11')
  screenmsg = 'transform_yyyydashmm_to_daterange_from_strlist(yyyydashmms=%s)' % str(yyyydashmms)
  print(screenmsg)
  yyyydashmmtuple = transform_yyyydashmm_to_daterange_from_strlist(yyyydashmms)
  print('\t', yyyydashmmtuple)


if __name__ == '__main__':
  """
  test_some()
  """
  adhoctest_some_yyyydashmm_dates()
