#!/usr/bin/env python3
"""
art/books/transf_excel_booklisting_to_json.py
"""
import datetime
import os
import pandas as pd
import art.books.packt.functions_packt_books_data_excel_json_pandas as pkfs


class Converter:

  def __init__(self):
    self.bookslisting_excel_fp = pkfs.get_bookslisting_excel_filepath()
    self.bookslisting_json_fp = pkfs.get_bookslisting_json_filepath()
    self.df = None
    self.bool_converted_to_json = False
    self.convert_msg = 'n/a'

  @property
  def basefolder(self):
    return os.path.split(self.bookslisting_excel_fp)[0]

  @property
  def bookslisting_excel_fn(self):
    bookslisting_excel_fn = os.path.split(self.bookslisting_excel_fp)[-1]
    return bookslisting_excel_fn

  @property
  def bookslisting_json_fn(self):
    bookslisting_json_fn = os.path.split(self.bookslisting_json_fp)[-1]
    return bookslisting_json_fn

  @property
  def n_rows(self):
    if self.df is not None:
      return self.df.shape[0]
    return None

  def read_df_from_excelfile(self):
    scrmsg = f"Reading Excel file [{self.bookslisting_excel_fn}]"
    print(scrmsg)
    self.df = pd.read_excel(self.bookslisting_excel_fp)

  def transform_excel_to_json(self):
    if self.df is None:
      self.read_df_from_excelfile()
    if not os.path.isfile(self.bookslisting_json_fp):
      scrmsg = f"Writing json [{self.bookslisting_json_fn}]"
      print(scrmsg)
      self.df.to_json(self.bookslisting_json_fp)
      self.bool_converted_to_json = True
      now = datetime.datetime.now()
      self.convert_msg = 'converted to json @ ' + str(now)
      return True
    else:
      scrmsg = f"Json file [{self.bookslisting_json_fn}] already exists, not reconverting it."
      now = datetime.datetime.now()
      self.convert_msg = 'target file exists so convertion could not happen @ ' + str(now)
      print(scrmsg)
      return False

  def convert(self):
    self.bool_converted_to_json = self.transform_excel_to_json()

  def __str__(self):
    outstr = f"""
    Excel filename = {self.bookslisting_excel_fn}
    Json filename = {self.bookslisting_json_fn}
    Base folder = {self.basefolder}
    N of rows = {self.n_rows}
    Json has been converted = {self.bool_converted_to_json}
    convert msg = {self.convert_msg}
    """
    return outstr


def adhoctest2():
  pass


def process():
  converter = Converter()
  converter.convert()
  print(converter)


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
