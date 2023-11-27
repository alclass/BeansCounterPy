#!/usr/bin/env python3
"""
commands/books/transf_excel_booklisting_to_json.py
"""
import os.path
import pandas as pd
import commands.books.functions_packt_books_data_excel_json_pandas as pkfs


class Converter:

  def __init__(self):
    self.bookslisting_excel_fp = pkfs.get_bookslisting_excel_filepath()
    self.bookslisting_json_fp = pkfs.get_bookslisting_json_filepath()
    self.df = None
    self.has_converted = False

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
      return True
    else:
      scrmsg = f"Json file [{self.bookslisting_json_fn}] already exists, not reconverting it."
      print(scrmsg)
      return False

  def convert(self):
    self.has_converted = self.transform_excel_to_json()

  def __str__(self):
    outstr = f"""
    Excel filename = {self.bookslisting_excel_fn}
    Json filename = {self.bookslisting_json_fn}
    Base folder = {self.basefolder}
    N of rows = {self.n_rows}
    Json convertion run = {self.has_converted}
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
