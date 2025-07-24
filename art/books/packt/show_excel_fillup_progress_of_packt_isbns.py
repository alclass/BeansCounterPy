#!/usr/bin/env python3
"""
art/books/show_excel_fillup_progress_of_packt_isbns.py
  => shows progress in how many url's are still missing in the main worksheet
The worksheet basic columns are: title | publication-date | url (with the ISBN) | formerly found ISBN's

"""
import os
import pandas as pd
import art.books.packt.functions_packt_books_data_excel_json_pandas as bkfs  # bkfs.get_bookdata_dirpath
import art.books.packt.functions_dataframe as dffs  # dffs.extract_rows_that_have_at_least_one_na
API_URL_to_interpole = 'https://www.googleapis.com/books/v1/volumes?q=title:{title_with_pluses}'
INTERVAL_INBETWEEN_APICALLS_IN_SEC = 3
pd.set_option('display.max_rows', 100)


def strip_subject_area_n_isbn13_from_packts_url(url):
  """
  Example:
    https://subscription.packtpub.com/book/business-other/9781788837361
  The subject area above is "business-other"

  One reference on the subject of df['newcolumn'] = df['column'].apply(functionname)
    https://saturncloud.io/blog/how-to-create-a-new-column-based-on-the-value-of-another-column-in-pandas/
  """
  if url is None:
    return None
  isbn13 = None
  subject_area = None
  try:
    pp = url.split('/')
    lastchunk = pp[-1]
    if len(lastchunk) == 13:
      isbn13 = lastchunk
    subject_area = pp[-2]
  except (AttributeError, IndexError):
    pass
  return subject_area, isbn13


class ProgressShower:

  def __init__(self):
    self.n_jsonfiles_saved = 0
    self.df_rows_orig = None
    self._df_rows = None
    self._dfna_rows = None
    self.df = None
    self.dfna = None
    self.bookdata_excelfilepath = None
    self.set_excelpath_or_raise()
    self.process()

  @property
  def df_rows(self):
    if self._df_rows is not None:
      return self._df_rows
    if self.df is None:
      return 0
    self._df_rows = self.df.shape[0]
    return self._df_rows

  @property
  def dfna_rows(self):
    if self._dfna_rows is not None:
      return self._dfna_rows
    if self.dfna is None:
      return 0
    self._dfna_rows = self.dfna.shape[0]
    return self._dfna_rows

  @property
  def n_rows_completed(self):
    try:
      return self.df_rows - self.dfna_rows
    except TypeError:
      pass
    return None

  def set_excelpath_or_raise(self):
    excelfilepath = bkfs.get_filepath_for_isbnfilledin_packt_titles()
    if excelfilepath is None or not os.path.isfile(excelfilepath):
      error_msg = 'Excel filepath does not exist [%s]' % str(excelfilepath)
      raise OSError(error_msg)
    self.bookdata_excelfilepath = excelfilepath

  def dataframe_postread_cleanup(self):
    """
    Steps:
    1  if needed, remove first row
    2 restablish column indices
      Obs whatever colindices are, they will become 0-based integers
          for afterward being renamed to known names
    3  if needed, remove first column (it's easier with the changed column indices above)
    4  rename column indices with known 'fieldnames'

    columns: title	| pubdate	| authors	| url
      column removed: isbn13liststr (it was originated from the Google api,
      and seen a bit ineffective due to the difficulty of only searching by title
      self.df.drop(columns=['isbn13liststr'], inplace=True)
    """
    self.df = self.df.drop([0], axis=0)
    # self.df = self.df.drop([0], axis=1)
    columnnames = ['title', 'pubdate', 'authors', 'url']
    coldict = {i: colname for i, colname in enumerate(columnnames)}
    colindices = list(range(0, len(columnnames)))
    self.df.columns = colindices
    self.df.rename(coldict, axis=1, inplace=True)
    # delete last column from df
    self.df_rows_orig = self.df.shape[0]

  def read_excel_to_pandas_df(self):
    print('Reading from', self.bookdata_excelfilepath)
    self.df = pd.read_excel(self.bookdata_excelfilepath)
    self.dataframe_postread_cleanup()

  def extract_nas_from_df(self):
    """
    This method copies all rows that have at least one NaN to another dataframe (self.dfna)
    """
    self.dfna = dffs.extract_rows_that_have_at_least_one_na(self.df)

  def derive_subject_areas_n_isbns_from_urls(self):
    self.df['area_n_isbn'] = self.df['url'].apply(strip_subject_area_n_isbn13_from_packts_url)
    self.df['subject'] = self.df['area_n_isbn'].apply(lambda e: e[0])
    self.df['isbn'] = self.df['area_n_isbn'].apply(lambda e: e[1])
    self.df.drop(['area_n_isbn'], axis=1, inplace=True)
    print(self.df.to_string())

  def save_extraction_nas_from_df(self):
    excelfilename = 'Excel to fillin.xlsx'
    folderpath = bkfs.get_bookdata_dirpath()
    output_excelfilepath = os.path.join(folderpath, excelfilename)
    if os.path.isfile(output_excelfilepath):
      collision_msg = 'Cannot continue due to file existence: \n  [%s] \n' % output_excelfilepath
      collision_msg += 'Please, move or delete it and rerun.'
      raise OSError(collision_msg)
    self.dfna.to_excel(output_excelfilepath)
    excelfilename = os.path.split(output_excelfilepath)
    print('Saved file', excelfilename)

  def process(self):
    self.read_excel_to_pandas_df()
    self.extract_nas_from_df()
    self.derive_subject_areas_n_isbns_from_urls()
    # self.save_extraction_nas_from_df()

  def print_report(self):
    return print(self)

  def __str__(self):
    outstr = f"""Report:
    df_rows_orig = {self.df_rows_orig}
    df_rows (filled-in ones) = {self.df_rows}
    dfna_rows (missing ones) = {self.dfna_rows}
    n_rows_completed = {self.n_rows_completed}
    """
    return outstr


def adhoctest():
  pass


def process():
  pg = ProgressShower()
  pg.print_report()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
