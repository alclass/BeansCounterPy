#!/usr/bin/env python3
"""
commands/download/fibb_daily_results_numbers_comma_to_point_convert.py

"""
import pandas as pd
import models.banks.bb.fi.bbfi_file_find as ffnd  # ffnd.BBFIFileFinder


class ResultAnalyser:

  def __init__(self, pdate, typ):
    self.date = pdate
    self.typ = typ
    self.finder = ffnd.BBFIFileFinder(self.date, self.typ)
    self._csv_filepath = None

  @property
  def csv_filepath(self):
    if self._csv_filepath is None:
     self._csv_filepath = self.finder.get_csv_filepath_for_date_n_type_or_raise()
    return self._csv_filepath

  def read_df(self):
    print('pd.DataFrame(self.csv_filepath)', self.csv_filepath)
    df = pd.read_csv(self.csv_filepath)
    print('head =>', df.head())
    print('columns =>', df.columns)
    print(df.index[1])
    # df.plot()


def adhoctests():
  typ = ffnd.BBFIFileFinder.Props.RFLP
  pdate = '2023-10-27'
  analyser = ResultAnalyser(pdate, typ)
  analyser.read_df()


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctests()
