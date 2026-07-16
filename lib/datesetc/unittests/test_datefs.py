#!/usr/bin/env python3
""""
lib/datesetc/unittests/test_datefs.py
  Unit-tests functions in datefs.py

To run Python unit tests from the terminal and display warnings, use:
 $python -W default -m unittest

By default, Python ignores and suppresses certain warnings during standard execution,
  but adding the -W default flag forces them to show up.

It forces Python to display warnings while launching test discovery in the local directory.
  python -W default -m unittest test_file.py:
    Runs tests within a specific target file.
  python -W default -m unittest -v:
    Activates verbose mode, showing specific test names alongside their warnings.

Other Warning Level Alternatives

You can swap default out for alternative warning control flags depending on your debugging goal:
  always: Prints a warning every single time it hits the triggering line of code.
  error: Converts warnings into fatal errors, instantly stopping your test execution.
  all: Alias variant of always to surface every single hidden notification.

"""
import datetime
import unittest
import lib.datesetc.datefs as dtfs  # inspect_n_get_datewsep_fieldorder_fr_str


class Empty:
  """
  To instantiate objects that may be 'grafted' (have attributes included) dynamically
  """
  pass


class TestInspectNGetDateFromStr(unittest.TestCase):
  """
  """

  def test1(self):
    """
    There are 8 hypotheses for function inspect_n_get_datewsep_fieldorder_fr_str(pstr)
    """
    explain_templ = "if pstr is {pstr}, return {expects}"
    # 1 hypothesis/subtest: None => None, None
    pstr = None
    expects = (None, None)
    explain_msg = explain_templ.format(pstr=pstr, expects=expects)
    ret_tupl = dtfs.inspect_n_get_datewsep_fieldorder_fr_str(strdate=pstr)
    self.assertEqual(expects, ret_tupl, msg=explain_msg)
    # 2 hypothesis/subtest: 'a-non-date' => None, None
    pstr = 'a-non-date'
    expects = (None, None)
    explain_msg = explain_templ.format(pstr=pstr, expects=expects)
    ret_tupl = dtfs.inspect_n_get_datewsep_fieldorder_fr_str(strdate=pstr)
    self.assertEqual(expects, ret_tupl, msg=explain_msg)
    # 3 hypothesis/subtest: '2024-12-12' => 'yyyymmdd', date(2024, 12, 12)
    pstr = '2024-12-12'  # convention says that when year begins the string, it's always yyyymmdd
    expects = ('yyyymmdd', datetime.date(2024, 12, 12))
    explain_msg = explain_templ.format(pstr=pstr, expects=expects)
    ret_tupl = dtfs.inspect_n_get_datewsep_fieldorder_fr_str(strdate=pstr)
    self.assertEqual(expects, ret_tupl, msg=explain_msg)
    # 4 hypothesis/subtest: '12-12-2024' => None, date(2024, 12, 12)
    pstr = '12-12-2024'  # though unconclusive in field-positions, date is possible for day=month
    expects = (None, datetime.date(2024, 12, 12))
    explain_msg = explain_templ.format(pstr=pstr, expects=expects)
    ret_tupl = dtfs.inspect_n_get_datewsep_fieldorder_fr_str(strdate=pstr)
    self.assertEqual(expects, ret_tupl, msg=explain_msg)
    # 5 hypothesis/subtest: '12-11-2024' => None, None
    pstr = '12-11-2024'  # unconclusive day/month
    expects = (None, None)
    explain_msg = explain_templ.format(pstr=pstr, expects=expects)
    ret_tupl = dtfs.inspect_n_get_datewsep_fieldorder_fr_str(strdate=pstr)
    self.assertEqual(expects, ret_tupl, msg=explain_msg)
    # 6 hypothesis/subtest: '11-12-2024' => None, None
    pstr = '11-12-2024'  # unconclusive day/month
    expects = (None, None)
    explain_msg = explain_templ.format(pstr=pstr, expects=expects)
    ret_tupl = dtfs.inspect_n_get_datewsep_fieldorder_fr_str(strdate=pstr)
    self.assertEqual(expects, ret_tupl, msg=explain_msg)
    # 7 hypothesis/subtest: '11-12-2024' => 'ddmmyyyy', date(2024, 12, 13)
    pstr = '13-12-2024'
    expects = ('ddmmyyyy', datetime.date(2024, 12, 13))
    explain_msg = explain_templ.format(pstr=pstr, expects=expects)
    ret_tupl = dtfs.inspect_n_get_datewsep_fieldorder_fr_str(strdate=pstr)
    self.assertEqual(expects, ret_tupl, msg=explain_msg)
    # 8 hypothesis/subtest: '12-13-2024' => 'mmddyyyy', date(2024, 12, 13)
    pstr = '12-13-2024'
    expects = ('mmddyyyy', datetime.date(2024, 12, 13))
    explain_msg = explain_templ.format(pstr=pstr, expects=expects)
    ret_tupl = dtfs.inspect_n_get_datewsep_fieldorder_fr_str(strdate=pstr)
    self.assertEqual(expects, ret_tupl, msg=explain_msg)

  def test2_obj_to_date(self):
    # 1 year, strmonth, day = 2024, '03', 31 => date(2024, 3, 31)
    year, strmonth, day = 2024, '03', 31
    expected_dt = datetime.date(year=year, month=int(strmonth), day=day)
    a_obj = Empty()
    a_obj.year = year
    a_obj.month = strmonth
    a_obj.day = day
    returned_dt = dtfs.transform_obj_impl_year_month_day_to_date(a_obj)
    self.assertEqual(expected_dt, returned_dt)
    # 2 year, strmonth, day = 2024, 12', '1' => date(2024, 12, 1)
    year, month, strday = 2013, 12, '1'
    expected_dt = datetime.date(year=year, month=month, day=int(strday))
    a_obj = Empty()
    a_obj.year = year
    a_obj.month = month
    a_obj.day = strday
    returned_dt = dtfs.transform_obj_impl_year_month_day_to_date(a_obj)
    self.assertEqual(expected_dt, returned_dt)
    # 3 year, strmonth, day = 2024, 32', '1' => None
    year, month, strday = 2013, 12, '32'
    # cannot have a date in which day is 32
    # expected_dt = datetime.date(year=year, month=month, day=int(strday))
    a_obj = Empty()
    a_obj.year = year
    a_obj.month = month
    a_obj.day = strday
    returned_dt = dtfs.transform_obj_impl_year_month_day_to_date(a_obj)
    self.assertIsNone(returned_dt)

  def test3_date_to_str(self):
    # 1 from date to str: year, month, day = 2024, 1, 1 => "2024-01-01"
    year, month, day = 2024, 1, 1
    testdate = datetime.date(year=year, month=month, day=day)
    returned_strdate = dtfs.date_to_str_4y_dash_2m_dash_2d(testdate)
    expected_strdate = f'{year}-{month:02d}-{day:02d}'
    self.assertEqual(expected_strdate, returned_strdate)
    # 2 from str to date: "2024-01-01" => date(2024, 1, 1)
    returned_date2 = dtfs.make_date_or_none(testdate)
    self.assertEqual(testdate, returned_date2)
    # 2 from date to str: 'blah' (not a 'date') => None
    returned_strdate = dtfs.date_to_str_4y_dash_2m_dash_2d(None)
    self.assertIsNone(returned_strdate)
    returned_date = dtfs.make_date_or_none(returned_strdate)
    self.assertIsNone(returned_date)

  def test4_make_dates(self):
    """

    """
    # 1 "2020-02-1" => date(2020, 2, 1)
    strdate = "2020-02-1"  # at one moment, this strdate was getting None as datetime.date
    exp_date = datetime.date(2020, 2, 1)
    ret_date = dtfs.make_date_or_none(strdate)
    self.assertEqual(exp_date, ret_date)
    # 2 "2020.2.1" => date(2020, 2, 1)
    strdate = "2020.2.1"  # at one moment, this strdate was getting None as datetime.date
    exp_date = datetime.date(2020, 2, 1)
    ret_date = dtfs.make_date_or_none(strdate)
    self.assertEqual(exp_date, ret_date)
    # 3 "2020.2.1" => date(2020, 2, 1)
    strdate = "2020.12.13"  # at one moment, this strdate was getting None as datetime.date
    exp_date = datetime.date(2020, 12, 13)
    ret_date = dtfs.make_date_or_none(strdate)
    self.assertEqual(exp_date, ret_date)
    # 4 "2.1.2000" => None
    strdate = "2.1.2020"  # at one moment, this strdate was getting None as datetime.date
    # exp_date = datetime.date(2020, 12, 13)
    ret_date = dtfs.make_date_or_none(strdate)
    self.assertIsNone(ret_date)
    # 5 "13.1.2000" => None
    strdate = "13.1.2020"  # at one moment, this strdate was getting None as datetime.date
    exp_date = datetime.date(2020, 1, 13)
    ret_date = dtfs.make_date_or_none(strdate)
    self.assertEqual(exp_date, ret_date)
    # 6 "20200131" => None
    strdate = "20200131"  # at one moment, this strdate was getting None as datetime.date
    exp_date = datetime.date(2020, 1, 31)
    ret_date = dtfs.make_date_or_none(strdate)
    self.assertEqual(exp_date, ret_date)

  def test5_inspect_datefieldorder_by_sep(self):
    # 1 '.', "2020-02-1" => yyyymmdd, date(2020, 2, 1)
    y, m, d, sep = 2020, 2, 1, '.'
    strdate = f"{y}{sep}{m:02}{sep}{d}"
    pdate = datetime.date(year=y, month=m, day=d)
    exp_tuple = ('yyyymmdd', pdate)
    ret_tuple = dtfs.inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    self.assertEqual(exp_tuple, ret_tuple)
    # 2 '-', "2020-2-01" => yyyymmdd, date(2020, 2, 1)
    y, m, d, sep = 2020, 2, 1, '-'
    strdate = f"{y}{sep}{m}{sep}{d:02}"
    pdate = datetime.date(year=y, month=m, day=d)
    exp_tuple = ('yyyymmdd', pdate)
    ret_tuple = dtfs.inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    self.assertEqual(exp_tuple, ret_tuple)
    # 3 '/', "2020/2/1" => yyyymmdd, date(2020, 2, 1)
    y, m, d, sep = 2020, 2, 1, '/'
    strdate = f"{y}{sep}{m}{sep}{d}"
    pdate = datetime.date(year=y, month=m, day=d)
    exp_tuple = ('yyyymmdd', pdate)
    ret_tuple = dtfs.inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    self.assertEqual(exp_tuple, ret_tuple)
    # 4 '/', "2020/2/32" => None, None (notice day is 32, so date is None)
    strdate, sep = "2020/2/32", '/'
    exp_tuple = (None, None)
    ret_tuple = dtfs.inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    self.assertEqual(exp_tuple, ret_tuple)
    # 5 '/', "2020/42/2" => None, None (notice month is 42, so date is None)
    y, m, d, sep = 2020, 42, 2, '/'
    strdate = f"{y}{sep}{m}{sep}{d}"
    # pdate = datetime.date(year=y, month=m, day=d)
    exp_tuple = (None, None)
    ret_tuple = dtfs.inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    self.assertEqual(exp_tuple, ret_tuple)
    # 5 '-', "31/2/2" => None, None (notice year is 31, so date is None)
    y, m, d, sep = 31, 2, 2, '-'
    strdate = f"{y}{sep}{m}{sep}{d}"
    # pdate = datetime.date(year=y, month=m, day=d)
    exp_tuple = (None, None)
    ret_tuple = dtfs.inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    self.assertEqual(exp_tuple, ret_tuple)
    # 5 '.', "32.2.2" => yyyymmdd, date(32, 2, 2) (notice year is 32, no ambiguity)
    y, m, d, sep = 32, 2, 2, '.'
    strdate = f"{y}{sep}{m}{sep}{d}"
    pdate = datetime.date(year=y, month=m, day=d)
    exp_tuple = ('yyyymmdd', pdate)
    ret_tuple = dtfs.inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    self.assertEqual(exp_tuple, ret_tuple)
    # 6 '.', "blah foo bar" => None, None
    sep = '.'
    strdate = "blah foo bar"
    exp_tuple = (None, None)
    ret_tuple = dtfs.inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    self.assertEqual(exp_tuple, ret_tuple)
    # 7 '.', None => None, None
    sep, strdate = '.', None
    exp_tuple = (None, None)
    ret_tuple = dtfs.inspect_datefieldorder_by_sep(
      sep=sep, strdate=strdate
    )
    self.assertEqual(exp_tuple, ret_tuple)

  def test6_check_n_days_w_a_dailydategenerator(self):
    # 1st hypothesis/subtest
    # input_daterangetuple = ('2023-1-1', dt(2023, 1, 7))
    # exp_dailydates = [dt(2023, 1, 1), dt(2023, 1, 2), ..., dt(2023, 1, 7)]
    dt = datetime.date
    daterangetuple = ('2023-1-1', dt(2023, 1, 7))
    ret_dailydates = list(dtfs.gen_dailydates_wi_daterangetuple(daterangetuple))
    exp_dailydates = [
      dt(2023, 1, 1),
      dt(2023, 1, 2),
      dt(2023, 1, 3),
      dt(2023, 1, 4),
      dt(2023, 1, 5),
      dt(2023, 1, 6),
      dt(2023, 1, 7),
    ]
    self.assertEqual(exp_dailydates, ret_dailydates)
    # 2nd hypothesis/subtest
    # input_daterangetuple = ('2023-1-1', dt(2023, 12, 31))
    # exp_counted_days = 365  # a non-leap year's days count
    dt = datetime.date
    daterangetuple = ('2023-1-1', dt(2023, 12, 31))
    counter = 0
    for _ in dtfs.gen_dailydates_wi_daterangetuple(daterangetuple):
      counter += 1
    exp_counted_days = 365  # a non-leap year's days count
    ret_counted_days = counter
    self.assertEqual(exp_counted_days, ret_counted_days)
