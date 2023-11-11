#!/usr/bin/env python3
"""
commands/transform/pandas_read_csv_bbfireports.py

"""
import datetime
import os.path

import models.banks.bb.fi.fibb_daily_results_html_to_csv_via_pandas_transform as trnsf  # .WithPandasHtmlToCsvConverter
import models.banks.bankpathfinder as pthfnd  # .BankOSFolderFileFinder
import pandas as pd
ACOES = pthfnd.BankOSFolderFileFinder.ACOES
RFDI = pthfnd.BankOSFolderFileFinder.RFDI
RFLP = pthfnd.BankOSFolderFileFinder.RFLP
typres = [ACOES, RFDI, RFLP]
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 2)


class Analyser:

  def __init__(self, pdate):
    self.csver = trnsf.WithPandasHtmlToCsvConverter(pdate)
    self.csvfiles = []
    self.dfdict = {}

  def find_csv_filepaths(self):
    for typre in typres:
      fpath = self.csver.get_csv_filepath_by_typre(typre)
      self.csvfiles.append(fpath)

  def rename_columns2(self, typre, df):
    df = df.rename(index=int, axis='colums')  # , axis='columns')
    print(df)

  def rename_columns(self, typre, df):
    """
    self.dfdict[typre] = rendf
    print('rendf.to_frame().T')
    """
    colrenamedict = {
      'Rentabilidade (%)': 'onday',
      'Rentabilidade (%).1': 'acc_month',
      'Rentabilidade (%).2': 'prevmonth',
      'Rentabilidade (%).3': 'inyear',
      'Rentabilidade (%).4': 'in12m',
      'Rentabilidade (%).5': 'in24m',
      'Rentabilidade (%).6': 'in36m',
    }
    for typre in typres:
      if typre == ACOES:
        colrenamedict['Ações'] = 'name'
      else:
        colrenamedict['Unnamed: 0_level_0'] = 'name'
    # a different approach
    colnames = ['name', 'onday', 'acc_month', 'prevmonth', 'inyear', 'in12m', 'in24m', 'in36m']
    afterpos = len(colnames)
    columnsize = df.shape[-1]
    print('n colnames', afterpos, 'columnsize', columnsize)
    df.columns = list(range(columnsize))
    columns_to_drop = [0] + list(range(afterpos+1, columnsize))
    df = df.drop(columns=columns_to_drop, axis=1)
    print(df.to_string())

  def read_pandas(self):
    for csv_filepath in self.csvfiles:
      df = pd.read_csv(csv_filepath)
      csv_filename = os.path.split(csv_filepath)[-1]
      typre = None
      if csv_filename.find(ACOES) > -1:
        typre = ACOES
      elif csv_filename.find(RFDI) > -1:
        typre = RFDI
      elif csv_filename.find(RFLP) > -1:
        typre = RFLP
      # self.rename_columns(typre, df)
      self.rename_columns(typre, df)

  def report(self):
    for typre in self.dfdict:
      df = self.dfdict[typre]
      print('typre', typre)
      # print('columns', df.columns)
      # print('df', df[3:5])

  def process(self):
    self.find_csv_filepaths()
    self.read_pandas()
    # self.report()

  def __str__(self):
    return str(self.csvfiles)


def adhoctest():
  pass


def process():
  pdate = datetime.date.today()
  print(pdate)
  analyzer = Analyser(pdate)
  analyzer.process()
  # print(analyzer)


if __name__ == '__main__':
  """
  adhoctest()
  pass
  """
  process()
