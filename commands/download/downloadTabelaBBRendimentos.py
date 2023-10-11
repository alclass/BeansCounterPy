#!/usr/bin/env python3
import datetime
import os
import sys
import time
# URL_BB_RENTAB_DIA = 'http://www21.bb.com.br/portalbb/rentabilidade/index.jsp?tipo=01'
URL_BB_RENTAB_DIA = 'https://www37.bb.com.br/portalbb/tabelaRentabilidade/rentabilidade/gfi7,802,9085,9089,1.bbx'
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


def main():
  today = datetime.date.today()
  table_filename = '%s bb rendimento.htm' % today
  if os.path.isfile(table_filename):
    print('Today\'s table (', table_filename, ') has already been downloaded.')
    sys.exit(0)
  url = URL_BB_RENTAB_DIA
  comm = 'wget -c ' + url
  ret_val = os.system(comm)
  # retVal = 0
  if ret_val == 0:
    print('Download OK')
  else:
    print('A problem occurred. Table could not be downloaded.')
    sys.exit(0)

  print('Renaming table to', table_filename)
  os.rename('index.jsp?tipo=01', table_filename)
  print('retVal', ret_val)
  if os.path.isfile(table_filename):
    print('Rename OK.')
  else:
    print('Could not rename.')


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


if __name__ == '__main__':
  """
  # main()
  adhoctest()
  """
  pass
