#!/usr/bin/env python3
"""
table rentabfundos
----------------
0 id 1 codename 2 name 3 monthref 4 rendmes 5 rendnoano 6 rend12meses
7 saldobrutofimmes 8 saldobrutomesanterior
9 quantcotafimmes 10 quantcotamesanterior
11 rendliq 12 irrf
"""
import datetime
import os
import csv
# import sqlite3
# import unittest


mountpath = None
sqlitefilename = '.beans_counter.sqlite'
csvfolderabspath = '/home/dados/OurDocs/Banks OurDocs/Caixa CEF OurDocs/Invests (Fundos etc) CEF OurDocs/' \
                   'Fundos de Investimento CEF/Extratos Mensais Ano a Ano FIC CEF OurDocs/' \
                   '2021 Extratos Mensais FIC CEF OurDocs'
csvfilename = 'WS 2021 Extratos Mensais FIC CEF OurDocs.csv'
maintablename = 'accounts'
fieldnames_common = [
  'bancosigla', 'fundocod', 'monthref',
  'rendmes', 'rendnoano', 'rend12meses',
  'quantcotasmesanterior', 'quantcotasfimmes',
  'saldobrutomesanterior', 'saldobrutofimmes', 'rendliq', 'irrf'
]
fieldnames_db = ['id'] + fieldnames_common
fieldnames_csv = fieldnames_common + ['not_used']


def transform_brdate_to_pdate(brdate):
  try:
    pp = brdate.split('/')
    year = int(pp[2])
    if year < 100:
      year += 2000
    month = int(pp[1])
    day = int(pp[0])
    return datetime.date(year=year, month=month, day=day)
  except IndexError:
    pass
  except ValueError:
    pass
  return None


class MonthReturn:

  def __init__(self, datadict):
    self.datadict = datadict
    self.transform_numbers_n_date()

  def transform_numbers_n_date(self):
    datefield = fieldnames_csv[2]
    brdate = self.datadict[datefield]
    pdate = transform_brdate_to_pdate(brdate)
    self.datadict[datefield] = pdate
    for i in range(3, len(self.datadict)):
      fieldname = fieldnames_csv[i]
      value = self.datadict[fieldname]
      value = value.replace('.', '')
      value = value.replace(',', '.')
      value = float(value)
      self.datadict[fieldname] = value

  def getfield(self, fieldname):
    return self.datadict[fieldname]

  def __str__(self):
    outstr = str(self.datadict)
    return outstr


def read_csvdatafile(csvdatafile_abspath):
  datarows = []
  datadict = {}
  with open(csvdatafile_abspath, newline='') as fd:
    csvreader = csv.reader(fd, delimiter=';', quotechar='|')
    n_row = 0
    for row in csvreader:
      n_row += 1
      if n_row == 1:
        continue
      for i, field in enumerate(row):
        if i > len(row) - 2:
          continue
        datadict[fieldnames_csv[i]] = row[i]
        datarows.append(datadict)
  print(datadict)
  monthr = MonthReturn(datadict)
  print('rendmes', monthr.getfield('rendmes'))
  print(monthr)


def process():
  csvdatafile = os.path.join(csvfolderabspath, csvfilename)
  read_csvdatafile(csvdatafile)


if __name__ == '__main__':
  process()
