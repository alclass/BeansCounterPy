#!/usr/bin/env python3
import os, sys, time

monthList = 'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'.split('|')
monthDict = {}; cMonth = 0
for m3 in monthList:
  cMonth+=1
  monthDict[m3] = cMonth
  
def getDate():
  strDateList = time.ctime().split()
  year = strDateList[-1]
  monthInt = monthDict[strDateList[1].lower()]
  month = str(monthInt).zfill(2)
  day = strDateList[2]
  dateStr = year + '-' + month + '-' + day.zfill(2)
  # print 'Today\'s date is', dateStr
  return dateStr

def main():
  date = getDate()
  tableFilename = '%s bb rendimento.htm' %(date)
  if os.path.isfile(tableFilename):
    print ('Today\'s table (', tableFilename, ') has already been downloaded.')
    sys.exit(0)
  url = 'http://www21.bb.com.br/portalbb/rentabilidade/index.jsp?tipo=01'
  comm = 'wget -c ' + url
  retVal = os.system(comm)
  # retVal = 0
  if retVal == 0:
    print ('Download OK')
  else:
    print ('A problem occurred. Table could not be downloaded.')
    sys.exit(0)

  print ('Renaming table to', tableFilename)
  retVal = os.rename('index.jsp?tipo=01', tableFilename)
  print ('retVal', retVal)
  if os.path.isfile(tableFilename):
    print ('Rename OK.')
  else:
    print ('Could not rename.')

if  __name__ == '__main__':
  main()
