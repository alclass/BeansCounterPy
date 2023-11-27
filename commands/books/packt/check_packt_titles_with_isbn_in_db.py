#!/usr/bin/env python3
"""
commands/books/check_packt_titles_with_isbn_in_db.py
"""
import os
import glob
import pandas as pd
import settings as sett
API_URL_to_interpole = 'https://www.googleapis.com/books/v1/volumes?q=title:{title_with_pluses}'
INTERVAL_INBETWEEN_APICALLS_IN_SEC = 3
pd.set_option('display.max_rows', 100)


def get_bookdata_dirpath():
  rootpath = sett.get_apps_data_rootdir_abspath()
  middlename = 'bookdata'
  bookpath = os.path.join(rootpath, middlename)
  return bookpath


def get_bookdata_filepath():
  bookdirpath = get_bookdata_dirpath()
  files = glob.glob(bookdirpath + '/*.xlsx')
  if len(files) > 0:
    return files[0]
  return None


def extract_title_from_series(series):
  """
  row is a 2D-tuple. The 2nd element is a 'payload' Series object.
  This object can be "indexed" with fieldnames (e.g. series.title).
  """
  try:
    title = series.title
    return title
  except (AttributeError, TypeError):
    pass
  return None


class ISBNLister:

  def __init__(self):
    self.n_jsonfiles_saved = 0
    self.n_rows = None
    self.df = None
    self.bookdata_excelfilepath = None
    self.set_excelpath_or_raise()
    self.process()

  def set_excelpath_or_raise(self):
    excelfilepath = get_bookdata_filepath()
    if excelfilepath is None or not os.path.isfile(excelfilepath):
      error_msg = 'Excel filepath does not exist [%s]' % str(excelfilepath)
      raise OSError(error_msg)
    self.bookdata_excelfilepath = excelfilepath

  def dataframe_postread_cleanup(self):
    """
    Steps:
    1  remove first row
    2 restablish column indices
      Obs whatever colindices are, they will become 0-based integers
          for then being renamed to known names
    3  remove first column (it's easier with the changed column indices above)
    4  rename column indices with known 'fieldnames'
    """
    self.df = self.df.drop([0], axis=0)
    colindices = list(range(0, 3))
    self.df.columns = colindices
    self.df = self.df.drop([0], axis=1)
    self.df.rename({1: 'isbn', 2: 'title'}, axis=1, inplace=True)
    self.n_rows = self.df.shape[0]

  def read_excel_to_pandas_df(self):
    print('Reading from', self.bookdata_excelfilepath)
    self.df = pd.read_excel(self.bookdata_excelfilepath)
    self.dataframe_postread_cleanup()

  def roll_rows_for_each_booktitle_with_nonisbn(self):
    df_without_isbn = self.df[pd.isna(self.df['isbn'])]
    self.roll_rows_for_given_dataframe(df_without_isbn)

  def roll_rows_for_each_booktitle_with_isbn(self):
    df_with_isbn = self.df.dropna()
    self.roll_rows_for_given_dataframe(df_with_isbn)

  def roll_rows_for_given_dataframe(self, paramdf):
    for i, row in enumerate(paramdf.iterrows()):
      # row is a 2D-tuple, first elem is 1-based-index int, second elem is a Series representing the row
      seq = row[0]
      series = row[1]
      try:
        isbn = series.isbn
        title = series.title
        if isbn:
          print(i+1, seq, isbn, title)
      except (AttributeError, TypeError):
        pass
    n_rows = paramdf.shape[0]
    print('df_rows', n_rows, 'original', self.n_rows)

  def process(self):
    self.read_excel_to_pandas_df()
    # self.roll_rows_for_each_booktitle_with_isbn()
    self.roll_rows_for_each_booktitle_with_nonisbn()


def adhoctest():
  pass


def process():
  ISBNLister()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
