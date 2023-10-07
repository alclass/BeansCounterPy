#!/usr/bin/env python3
# --*-- encoding: utf8 --*--
import glob, os, sys, time, MySQLdb
import extraiRendimentoDoDiaBB

def transformFloat(dayIndex):
  strFloat = dayIndex.replace(',','.')
  try:
    dayIndexFloat = float(strFloat)
    return dayIndexFloat
  except ValueError:
    return None

dictFundos = {}
def pickUpSqlAllFundos():
  conn = MySQLdb.connect(host='x64', port=3306, user='webuser', \
                       passwd='webpass', db='bizIn')
  cursor = conn.cursor()
  sql = "select * from `fundos`"
  cursor.execute(sql)
  records = cursor.fetchall()
  codFundo = None
  # print 'records', records
  nOfRecs = 0
  for record in records:
    if len(record) > 0:
      codFundo = record[0]
      fundoNome = record[1]
      fundoNome = extraiRendimentoDoDiaBB.convertTextFromIso88591ToUtf8(fundoNome)
      # codBanco = record[2]
      dictFundos[fundoNome] = codFundo
      nOfRecs += 1
      print 'cod/Nome', codFundo, fundoNome
  print nOfRecs, 'records were found.'
  # return codFundo
  
def pickUpSqlCodFundo(fundoNome):
  conn = MySQLdb.connect(host='x64', port=3306, user='webuser', \
                       passwd='webpass', db='bizIn')
  cursor = conn.cursor()
  sql = "select `codFundo` from `fundos` where `nome` = '" + fundoNome + "'"
  cursor.execute(sql)
  results = cursor.fetchall()
  codFundo = None
  print 'results', results
  if len(results) > 0:
    record = results[0]
    if len(record) > 0:
      codFundo = record[0]
      dictFundos[fundoNome] = codFundo
      print 'cod/Nome', codFundo, fundoNome
      return codFundo
  print 'A problem occurred, could not find codFundo for fundoNome =', fundoNome
  return None

def pickUpCodFundo(fundoNome):
  try:
    codFundo = dictFundos[fundoNome]
    return codFundo
  except KeyError:
    codFundo = pickUpSqlCodFundo(fundoNome)
  return codFundo

def sqlinsertDatums(date, datumList):
  for datum in datumList:
    fundoNome, dayIndex = datum
    codFundo = pickUpCodFundo(fundoNome)
    if codFundo == None:
      return
    dayIndexFloat = transformFloat(dayIndex)
    if dayIndexFloat == None:
      return
    sql = '''insert into `dayIndexArchive` (`date`, `codFundo`, `dayIndex`)
        values ('%s','%s','%s');''' %(date, str(codFundo), dayIndexFloat)
    outSqlFile.write(sql + '\n')
    print sql    

pickUpSqlAllFundos()

outSqlFilename = 'outSqlFile.sql'
outSqlFile = open(outSqlFilename, 'w')

htmlFiles=glob.glob('2008-*.htm')
print htmlFiles
htmlFiles.sort()
for h in htmlFiles:
  print h

if  __name__ == '__main__':
  
  for html in htmlFiles:
    date = html[0:10]
    datumList = extraiRendimentoDoDiaBB.extractColumn(date)
    print '='*40
    print date
    print '='*40
    sqlinsertDatums(date, datumList)

outSqlFile.close()
