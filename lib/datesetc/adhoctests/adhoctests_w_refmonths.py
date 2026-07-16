#!/usr/bin/env python3
""""
lib/datesetc/adhoctests/adhoctests_w_refmonths.py
  Performs adhoc-tests on refmonths

"""
import datetime
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs


def list_refmonths_in_range(refmonth_ini=None, refmonth_fim=None):
  refmonth_ini, refmonth_fim = rmfs.getverify_refmonthrangetuple_or_default(
      refmonth_ini,
      refmonth_fim
  )
  p_input = f"refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  plist = rmfs.get_monthrange_as_list(
      refmonth_ini,
      refmonth_fim
  )
  ostr = f"""1 list_refmonths_in_range {p_input}
  plist = {plist}"""
  print(ostr)
  refmonth_ini, refmonth_fim = '202403', '202405'
  p_input = f"refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  refmonth_ini, refmonth_fim = rmfs.getverify_refmonthrangetuple_or_default(
      refmonth_ini,
      refmonth_fim
  )
  plist = rmfs.get_monthrange_as_list(
      refmonth_ini,
      refmonth_fim
  )
  ostr = f"""2 list_refmonths_in_range {p_input}
  plist = {plist}"""
  print(ostr)


def ahdoc_getverify_refmonth_range(refmonth_ini=None, refmonth_fim=None):
  p_input = f"refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  refmonth_ini, refmonth_fim = rmfs.getverify_refmonthrangetuple_or_default(
      refmonth_ini,
      refmonth_fim
  )
  p_output = f"refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  ostr = f""" => ahdoc_validate_refmonth_range({p_input}):
  return = ({p_output})
  """
  print(ostr)
  refmonth_ini, refmonth_fim = '202403', '202405'
  p_input = f"refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  refmonth_ini, refmonth_fim = rmfs.getverify_refmonthrangetuple_or_default(
      refmonth_ini,
      refmonth_fim
  )
  p_output = f"refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  ostr = f""" => ahdoc_validate_refmonth_range({p_input}):
  return = ({p_output})
  """
  print(ostr)


def adhoc_fillin_refmonths_fr_ndayslist():
  ndayslist = [3, 3]
  inidate = '202512'
  findate = '20261'
  dateborders = rmfs.find_dateborders_fr_ndayslist_n_refmonths(ndayslist, inidate, findate)
  ostr = f""" => adhoc_fillin_refmonths_fr_ndayslist()
  input => ndayslist = {ndayslist} | inirefmonth = {inidate} | finrefmonth = {findate} 
  output (date borders) = {dateborders}
  """
  print(ostr)


def adhoc_test():
  refmonthdate_fim = '2023-01-07'
  refmonthdate_ini = '2023-10-17'
  print('ini', refmonthdate_ini, 'fim', refmonthdate_fim)
  ahdoc_getverify_refmonth_range(refmonthdate_ini, refmonthdate_fim)


def adhoc_test_date_with_fieldpos():
  """
  fieldpos = 'yyyymmdd'
  strdate = '2023-01-07'
  pdate = dtfs.transform_strdate_to_date_with_fieldpos(strdate, fieldpos)
  print(strdate, fieldpos, 'transform_strdate_to_date_with_fieldpos', pdate)
  fieldpos = 'ddmmyyyy'
  strdate = '01-07-2023'
  pdate = dtfs.transform_strdate_to_date_with_fieldpos(strdate, fieldpos)
  print(strdate, fieldpos, 'transform_strdate_to_date_with_fieldpos', pdate)
  fieldpos = 'ddmmyyyy'
  strdate = '01/07/2023'
  pdate = dtfs.transform_strdate_to_date_with_fieldpos(strdate, fieldpos)
  print(strdate, fieldpos, 'transform_strdate_to_date_with_fieldpos', pdate)
  strdate = '5.4.2023'
  fieldpos = 'mmddyyyy'
  pdate = dtfs.transform_strdate_to_date_with_fieldpos_n_sep(strdate, fieldpos, sepchar='.')
  print(strdate, fieldpos, 'transform_strdtransform_strdate_to_date_with_fieldpos_n_sep', pdate)
  strdate = '13/11/2023'
  fieldpos = 'ddmmyyyy'
  pdate = dtfs.transform_strdate_to_date_with_fieldpos(strdate, fieldpos)
  print(strdate, fieldpos, 'transform_strdate_to_date_with_fieldpos', pdate)
  """
  strdate = '11/13/2023'
  pdate = dtfs.transform_strdate_to_date(strdate)
  scrmsg = f"{strdate} => transform_strdattransform_strdate_to_date({pdate})"
  print(scrmsg)


def adhoctest1():
  """
  Adhoc test hypotheses for inspect_n_get_datewsep_fieldorder_fr_str(pstr):
  """
  ahdoc_getverify_refmonth_range()
  list_refmonths_in_range()
  adhoc_fillin_refmonths_fr_ndayslist()
  inidate = datetime.date(2026, 1, 31)
  findate = datetime.date(2027, 1, 1)  # in the future in the time of writing
  # ----------------------
  ret_n_months = rmfs.calc_n_months_involved(findate, inidate)
  ostr = f""" => calc_n_months_involved(finidate={findate}, inidate={inidate})
  returned {ret_n_months}
  """
  print(ostr)
  ret_n_months = rmfs.calc_n_calendar_months_in_between(findate, inidate)
  ostr = f""" => calc_n_calendar_months_in_between(finidate={findate}, inidate={inidate})
  returned {ret_n_months}
  """
  print(ostr)
  ret_n_months = rmfs.calc_int_n_months_inbetween(inidate, findate)
  ostr = f""" => calc_int_n_months_inbetween(inidate={inidate}, finidate={findate})
  returned {ret_n_months}  # here the order of parameters is taken into account
  """
  print(ostr)


def adhoctest10():
  """
  """
  y, m, d = 2012, 2, 3
  attrs_obj = rmfs.ClassWithYearMonthDay(year=y, month=m, day=d)
  expected_refmonthdate = attrs_obj.as_refmonthdate()
  pdate = datetime.date(year=y, month=m, day=d)
  returned_refmonthdate = rmfs.make_refmonth_or_none(pdate)
  strdate = dtfs.date_to_str_4y_dash_2m_dash_2d(expected_refmonthdate)
  print('expected_refmonthdate (done with ClassWithYearMonthDay)', strdate)
  strdate = dtfs.date_to_str_4y_dash_2m_dash_2d(returned_refmonthdate)
  print('returned_refmonthdate', strdate)
  inidt, fimdt = rmfs.spawn_inidate_n_fimdate_fr_refmonth(expected_refmonthdate)
  scrmsg = f"spawn_inidate_n_fimdate_fr_refmonth({expected_refmonthdate}) -> {inidt} | {fimdt}"
  print(scrmsg)
  monthslastdate = rmfs.get_monthslastdate_via_calendar(pdate)
  scrmsg = f"get_monthslastdate_via_calendar({pdate}) -> {monthslastdate}"
  print(scrmsg)
  monthslastdate = rmfs.get_monthslastdate_via_addition(pdate)
  scrmsg = f"get_monthslastdate_via_addition({pdate}) -> {monthslastdate}"
  print(scrmsg)
  monthslastday = rmfs.get_monthslastday_via_calendar_or_none(pdate)
  scrmsg = f"get_monthslastday_via_calendar({pdate}) -> {monthslastday}"
  print(scrmsg)
  monthslastday = rmfs.get_monthslastday_via_addition(pdate)
  scrmsg = f"get_monthslastday_via_addition({pdate}) -> {monthslastday}"
  print(scrmsg)


def adhoctest2():
  yearini, yearfim = 2020, 2024
  refmonth_ini, refmonth_fim = rmfs.make_refmonthtuple_w_yearsinifin(yearini, yearfim)
  scrmsg = f"yearini={yearini} | yearfim={yearfim} | refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  print(scrmsg)
  yearini, yearfim = 2020, 2028
  refmonth_ini, refmonth_fim = rmfs.make_refmonthtuple_w_yearsinifin(yearini, yearfim)
  scrmsg = f"yearini={yearini} | yearfim={yearfim} | refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  print(scrmsg)
  yearini, yearfim = 2027, 2029
  refmonth_ini, refmonth_fim = rmfs.make_refmonthtuple_w_yearsinifin(yearini, yearfim)
  scrmsg = f"yearini={yearini} | yearfim={yearfim} | refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  print(scrmsg)
  yearini, yearfim = 2025, 2034
  refmonth_ini, refmonth_fim = rmfs.make_refmonthtuple_w_yearsinifin(yearini, yearfim)
  scrmsg = f"yearini={yearini} | yearfim={yearfim} | refmonth_ini={refmonth_ini} | refmonth_fim={refmonth_fim}"
  print(scrmsg)


def adhoctest3():
  """
  how to calculate number of months between two dates in Python?
  """
  pdate1 = dtfs.make_date_or_raise('2020-02-1')
  pdate2 = dtfs.make_date_or_raise('2021-10-31')
  n_months_in_bw = rmfs.calc_n_completemonths_between_dates(pdate1, pdate2)
  scrmsg = f"{pdate2} - {pdate1} = n_months_in_bw={n_months_in_bw}"
  print(scrmsg)


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
  inirefmonth = '2023-01-15'
  finrefmonth = '2023-08-11'
  generator = rmfs.generate_monthrange(p_refmonth_ini=inirefmonth, p_refmonth_fim=finrefmonth)
  src_msg = 'adhoc test generator refmonthdate_ini = %s, refmonthdate_ini = %s' % (inirefmonth, finrefmonth)
  print(src_msg)
  for i, refmonth in enumerate(generator):
    seq = i + 1
    scrmsg = f"{seq} | {refmonth}"
    print(scrmsg)
  print('transform_year_into_refmonthrange_or_recent_year()')
  rdmrange = rmfs.transform_year_into_refmonthrange_or_recent_year()
  print('\t', rdmrange)
  yyyydashmms = ('2023-01', '2023-11')
  screenmsg = 'transform_yyyydashmm_to_daterange_from_strlist(yyyydashmms=%s)' % str(yyyydashmms)
  print(screenmsg)
  yyyydashmmtuple = rmfs.transform_refmonthlist_to_a_daterangetuple(yyyydashmms)
  print('\t', yyyydashmmtuple)


if __name__ == '__main__':
  """
  adhoc_test_date_with_fieldpos()
  """
  adhoctest1()
