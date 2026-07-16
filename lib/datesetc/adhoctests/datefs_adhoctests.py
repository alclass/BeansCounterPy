#!/usr/bin/env python3
""""
lib/datesetc/datefs.py

from collections import namedtuple
adhoc2_nt = namedtuple('Adhoc2NT', ['explain_msg', 'pstr', 'expects'])
"""
import datetime
import lib.datesetc.datefs as dtfs
from collections import namedtuple
adhoc2nt = namedtuple('Adhoc2NT', ['explain_msg', 'pstr', 'expects'])


def printout_adhoc2(adhoc_n, descr, pstr, posmarker, pdate):
  scrmsg = f"{adhoc_n} input => pstr={pstr} | output => tuple(posmarker={posmarker}, pdate {pdate})"
  ostr = f"{descr}\n\t{scrmsg}"
  print(ostr)


def adhoctest1():
  strdate = "2020-02-1"  # at one moment, this strdate was getting None as datetime.date
  exp_date = dtfs.datetime.date(2020, 2, 1)
  ret_date = dtfs.make_date_or_none(strdate)
  scrmsg = f"input {strdate} | expected {exp_date} | output {ret_date}"
  print(scrmsg)


def adhoctest2():
  """
  Adhoc test hypotheses for inspect_n_get_datewsep_fieldorder_fr_str(pstr):
  """
  testlist = []
  explain_templ = "if pstr is {pstr}, return {expects}"
  # 1
  pstr = None  # though unconclusive in field-positions, date is possible
  expects = (None, None)
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 2
  pstr = 'a-non-date'  # though unconclusive in field-positions, date is possible
  expects = (None, None)
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 3
  pstr = '2024-12-12' # convention says that when year begins, it's always yyyymmdd
  expects = ('yyyymmdd', datetime.date(2024, 12, 12))
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 4
  pstr = '12-12-2024' # though unconclusive in field-positions, date is possible
  expects = (None, datetime.date(2024, 12, 12))
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 5
  pstr = '12-11-2024'  # unconclusive day/month
  expects = (None, None)
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 6
  pstr = '11-12-2024'  # unconclusive day/month
  expects = (None, None)
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 7
  pstr = '13-12-2024'
  expects = ('ddmmyyyy', datetime.date(2024, 12, 13))
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 8
  pstr = '12-13-2024'
  expects = ('mmddyyyy', datetime.date(2024, 12, 13))
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  print('='*40)
  for i,  tst_nt in enumerate(testlist):
    testn = i + 1
    adhoc_n = f'adhoc{testn}'
    descr = f"{f'adhoc{testn}'} => {tst_nt.explain_msg}"
    pstr = tst_nt.pstr
    posmarker, pdate = dtfs.inspect_n_get_datewsep_fieldorder_fr_str(pstr)
    dtfs.printout_adhoc2(adhoc_n, descr, pstr, posmarker, pdate)


def adhoctest3():
  # 1 pass None
  pdate = dtfs.transform_strdate_to_date_or_today()
  print('None =>', dtfs.datetostr(pdate))
  # 2 pass a dd/mm/yyyy
  strdate = '1/1/1999'
  pdate = dtfs.transform_strdate_to_date_or_today(strdate)
  print(strdate, ' =>', dtfs.datetostr(pdate))
  # 3 pass a non-consistent date dd/mm/yyyy expecting None (may go to unittest later on)
  strdate = '31/11/2999'
  pdate = dtfs.transform_strdate_to_date(strdate)
  print(strdate, ' =>', dtfs.datetostr(pdate))
  # 4 pass a consistent date (though welll in the future) dd/mm/yyyy expecting a valid date
  strdate = '31/10/2999'
  pdate = dtfs.transform_strdate_to_date(strdate)
  print(strdate, ' =>', dtfs.datetostr(pdate))


def adhoctest4():
  strdate = "20200131"  # at one moment, this strdate was getting None as datetime.date
  exp_date = datetime.date(2020, 1, 31)
  ret_date = dtfs.make_date_or_none(strdate)
  scrmsg = f"input {strdate} | expected {exp_date} | output {ret_date}"
  print(scrmsg)
  strdate = "2020-1-1"  # at one moment, this strdate was getting None as datetime.date
  exp_date = datetime.date(2020, 1, 1)
  ret_date = dtfs.make_date_or_none(strdate)
  scrmsg = f"input {strdate} | expected {exp_date} | output {ret_date}"
  print(scrmsg)
  strdate = "202011"  # at one moment, this strdate was getting None as datetime.date
  exp_date = None
  ret_date = dtfs.make_date_or_none(strdate)
  scrmsg = f"input {strdate} | expected {exp_date} | output {ret_date}"
  print(scrmsg)





def adhoctest5():
  """
  Adhoc test hypotheses for inspect_n_get_datewsep_fieldorder_fr_str(pstr):
  """
  testlist = []
  explain_templ = "if pstr is {pstr}, return {expects}"
  # 1
  pstr = None  # though unconclusive in field-positions, date is possible
  expects = (None, None)
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 2
  pstr = 'a-non-date'  # though unconclusive in field-positions, date is possible
  expects = (None, None)
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 3
  pstr = '2024-12-12'  # convention says that when year begins, it's always yyyymmdd
  expects = ('yyyymmdd', datetime.date(2024, 12, 12))
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 4
  pstr = '12-12-2024'  # though unconclusive in field-positions, date is possible
  expects = (None, datetime.date(2024, 12, 12))
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 5
  pstr = '12-11-2024'  # unconclusive day/month
  expects = (None, None)
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 6
  pstr = '11-12-2024'  # unconclusive day/month
  expects = (None, None)
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 7
  pstr = '13-12-2024'
  expects = ('ddmmyyyy', datetime.date(2024, 12, 13))
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  # 8
  pstr = '12-13-2024'
  expects = ('mmddyyyy', datetime.date(2024, 12, 13))
  explain_msg = explain_templ.format(pstr=pstr, expects=expects)
  elem = adhoc2nt(
    pstr=pstr, explain_msg=explain_msg, expects=expects,
  )
  testlist.append(elem)
  print('='*40)
  for i,  tst_nt in enumerate(testlist):
    testn = i + 1
    adhoc_n = f'adhoc{testn}'
    descr = f"{f'adhoc{testn}'} => {tst_nt.explain_msg}"
    pstr = tst_nt.pstr
    posmarker, pdate = inspect_n_get_datewsep_fieldorder_fr_str(pstr)
    printout_adhoc2(adhoc_n, descr, pstr, posmarker, pdate)


def adhoctest6():
  # 1 pass None
  pdate = transform_strdate_to_date_or_today()
  print('None =>', datetostr(pdate))
  # 2 pass a dd/mm/yyyy
  strdate = '1/1/1999'
  pdate = transform_strdate_to_date_or_today(strdate)
  print(strdate, ' =>', datetostr(pdate))
  # 3 pass a non-consistent date dd/mm/yyyy expecting None (may go to unittest later on)
  strdate = '31/11/2999'
  pdate = transform_strdate_to_date(strdate)
  print(strdate, ' =>', datetostr(pdate))
  # 4 pass a consistent date (though welll in the future) dd/mm/yyyy expecting a valid date
  strdate = '31/10/2999'
  pdate = transform_strdate_to_date(strdate)
  print(strdate, ' =>', datetostr(pdate))



if __name__ == '__main__':
  """
  adhoctest3()
  adhoctest2()
  """
  adhoctest4()
