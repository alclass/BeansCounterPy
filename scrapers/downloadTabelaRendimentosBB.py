#!/usr/bin/env python3
import os
import sys
import time

monthList = 'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'.split('|')
monthDict = {}
cMonth = 0
for m3 in monthList:
  cMonth += 1
  monthDict[m3] = cMonth
  

def getdate():
  str_date_list = time.ctime().split()
  year = str_date_list[-1]
  month_int = monthDict[str_date_list[1].lower()]
  month = str(month_int).zfill(2)
  day = str_date_list[2]
  date_str = year + '-' + month + '-' + day.zfill(2)
  # print 'Today\'s date is', dateStr
  return date_str


def main():
  date = getdate()
  table_filename = '%s bb rendimento.htm' % date
  if os.path.isfile(table_filename):
    print('Today\'s table (', table_filename, ') has already been downloaded.')
    sys.exit(0)
  url = 'http://www21.bb.com.br/portalbb/rentabilidade/index.jsp?tipo=01'
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


if __name__ == '__main__':
  main()
