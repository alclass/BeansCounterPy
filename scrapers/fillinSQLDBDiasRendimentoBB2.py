#!/usr/bin/env python3
# --*-- encoding: utf8 --*--
import glob
import os
import sys
import time
import MySQLdb
import extraiRendimentoDoDiaBB

class HtmlToDBTransferer:
  def __int__(self, fundocod, fundonome, dayindex):
    self.fundocod = fundocod
    self.fundonome = fundonome
    self.dayindex = dayindex

  def transform_str_to_float(self):
    strFloat = self.dayIndex.replace(',','.')
    try:
      dayIndexFloat = float(strFloat)
      return dayIndexFloat
    except ValueError:
      return None

  dictFundos = {}
  def pickup_codfundo(self):
    try:
      codfundo = self.dictFundos[fundonome]
      return codFundo
    except KeyError:
      pass
    conn = MySQLdb.connect( ... )  # TO-DO
    cursor = conn.cursor()
    print('fundoNome', fundoNome)
    sql = "select `codFundo` from `fundos` where `nome` = '" + fundoNome + "'"
    cursor.execute(sql)
    results = cursor.fetchall()
    codFundo = None
    print('results', results)
    if len(results) > 0:
      record = results[0]
      if len(record) > 0:
        codFundo = record[0]
    #dictFundos[fundoNome] = codFundo
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

  def process(self):
    self.sqlinsertDatums()


outSqlFilename = 'outSqlFile.sql'
outSqlFile = open(outSqlFilename, 'w')

htmlfilelist = glob.glob('2008-*.htm')
print(htmlfiles)
htmlFiles.sort()
for htmlfilename in htmlfilelist:
  print(htmlfilename)


if  __name__ == '__main__':
  for html in htmlFiles:
    pdate = html[0:10]
    rendimentos_ondate_dict = extraiRendimentoDoDiaBB.extractColumn(pdate)
    print('='*40)
    print(pdate)
    print('='*40)
    transferer = HtmlToDBTransferer(rendimentos_ondate_dict)
    transferer.process()

outSqlFile.close()
