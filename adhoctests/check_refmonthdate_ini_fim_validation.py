#!/usr/bin/env python3
""""


"""
import lib.datesetc.datefs as dtfs


def validate_dates(refmonthdate_ini, refmonthdate_fim):
  refmonthdate_ini, refmonthdate_fim = dtfs.validate_refmonthdate_ini_fim_or_1monthbefore(
      refmonthdate_ini,
      refmonthdate_fim
  )
  print("Result")
  print('ini', refmonthdate_ini, 'fim', refmonthdate_fim)


def adhoc_test():
  refmonthdate_fim = '2023-01-07'
  refmonthdate_ini = '2023-10-17'
  print('ini', refmonthdate_ini, 'fim', refmonthdate_fim)
  validate_dates(refmonthdate_ini, refmonthdate_fim)


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
  print(strdate, 'transform_strdattransform_strdate_to_date', pdate)


if __name__ == '__main__':
  # adhoc_test()
  adhoc_test_date_with_fieldpos()
