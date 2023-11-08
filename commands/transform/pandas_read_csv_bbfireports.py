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


class Analyser:

  def __init__(self, pdate):
    self.csver = trnsf.WithPandasHtmlToCsvConverter(pdate)
    self.csvfiles = []

  def find_csv_filepaths(self):
    for typre in typres:
      fpath = self.csver.get_csv_filepath_by_typre(typre)
      self.csvfiles.append(fpath)

  def read_pandas(self):
    for csv_filepath in self.csvfiles:
      df = pd.read_csv(csv_filepath)
      csv_filename = os.path.split(csv_filepath)[-1]
      print(csv_filename, 'df head()')
      print(df.head())

  def process(self):
    self.find_csv_filepaths()
    self.read_pandas()
    pass

  def __str__(self):
    return str(self.csvfiles)


def adhoctest():
  pass


def process():
  pdate = datetime.date.today()
  print(pdate)
  analyzer = Analyser(pdate)
  analyzer.process()
  print(analyzer)


if __name__ == '__main__':
  """
  adhoctest()
  pass
  """
  process()
