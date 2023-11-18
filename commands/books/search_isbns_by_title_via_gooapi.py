#!/usr/bin/env python3
"""
commands/books/search_isbns_by_title_via_gooapi.py

Note on the "open" (ie, without a token) API limitation used by this script:
  According to the GoogleBook API docs, two limits are observed, ie:
    1  up to (at most) 5000 requests per day
    2  up to (at most) 10 requests with a second
  Because this script's usage is well less than the maximum allowed
    -- and for simplying it somehow -- it will not treat this particular issue.

When running, at about row 186 (well less than 5000):

requests.exceptions.ConnectionError:
  HTTPSConnectionPool(host='www.googleapis.com', port=443):
  Max retries exceeded with
    url: /books/v1/volumes?q=title:Hands-On+Neuroevolution+with+Python
    (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object
     at 0x7fce7d619360>: Failed to establish a new connection:
     [Errno -3] Temporary failure in name resolution'))

 => it seems a DNS failure not exactly a limitation issue
"""
import os
import time
import pandas as pd
import requests
import commands.books.ibsn_n_file_helperfunctions as isbnfs
API_URL_to_interpole = 'https://www.googleapis.com/books/v1/volumes?q=title:{title_with_pluses}'
INTERVAL_INBETWEEN_APICALLS_IN_SEC = 2
pd.set_option('display.max_rows', 100)


class ISBNSearcher:

  def __init__(self):
    self.n_jsonfiles_saved = 0
    self.n_rows = None
    self.instanceseq = 0
    self.n_rows_original = None
    self._n_rows_with_isbn = None
    self.df = None
    self.bookdata_excelfilepath = None
    self.set_excelpath_or_raise()
    self.process()

  @property
  def n_rows_with_isbn(self):
    if self._n_rows_with_isbn is None:
      try:
        self._n_rows_with_isbn = self.n_rows_original - self.n_rows
      except (TypeError, ValueError):
        pass
    return self._n_rows_with_isbn  # may return None

  def set_excelpath_or_raise(self):
    excelfilepath = isbnfs.get_bookdata_filepath()
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
    self.n_rows = self.n_rows_original = self.df.shape[0]

  def remove_rows_with_isbn(self):
    self.df = self.df[pd.isna(self.df['isbn'])]  # ie keep rows for which isbn is NaN
    self.n_rows = self.df.shape[0]
    print('n_rows', self.n_rows, 'originally', self.n_rows_original)
    print('n rows with isbn', self.n_rows_with_isbn)

  def read_excel_to_pandas_df(self):
    print('Reading from', self.bookdata_excelfilepath)
    self.df = pd.read_excel(self.bookdata_excelfilepath)
    self.dataframe_postread_cleanup()
    self.remove_rows_with_isbn()

  @staticmethod
  def form_json_filename(seq, title):
    return f'{seq:03} {title}.json'

  def form_json_filepath(self, seq, title):
    jsonfilename = self.form_json_filename(seq, title)
    dirpath = isbnfs.get_bookdata_dirpath()
    jsonfilepath = os.path.join(dirpath, jsonfilename)
    return jsonfilepath

  def jsonfile_exists(self, seq, title):
    try:
      jsonfilepath = self.form_json_filepath(seq, title)
      return os.path.isfile(jsonfilepath)  # returns True or False depending on file existence
    except TypeError:
      pass
    return False

  def save_json_response_from_api(self, seq, title, json_payload):
    jsonfilepath = self.form_json_filepath(seq, title)
    fd = open(jsonfilepath, 'w', encoding='utf-8')
    fd.write(json_payload)
    fd.close()
    self.n_jsonfiles_saved += 1

  def get_n_save_json_response_from_api(self, seq, title, url):
    print(seq, 'of', self.n_rows, 'calling API request for [', title, ']')
    req = requests.get(url)
    json_payload = req.text  # req.content
    self.save_json_response_from_api(seq, title, json_payload)
    jsonfilename = self.form_json_filename(seq, title)
    print(seq, 'of', self.n_rows, 'Written', self.n_jsonfiles_saved, 'th json file: ', jsonfilename)

  def call_googlebook_api_to_search_isbn_by_title(self, seq, title):
    if self.jsonfile_exists(seq, title):
      svd = self.n_jsonfiles_saved
      print(
        'i', self.instanceseq, 'r', seq, 'of', self.n_rows, 'saved =', svd,
        '[', title, '] is already recorded on disk. Going next.'
      )
      return
    print('i', self.instanceseq, 'r', seq, 'of', self.n_rows, '=>', title)
    title_with_pluses = title.replace(' ', '+')
    url = API_URL_to_interpole.format(title_with_pluses=title_with_pluses)
    print(url)
    self.get_n_save_json_response_from_api(seq, title, url)
    print('Waiting', INTERVAL_INBETWEEN_APICALLS_IN_SEC, 'seconds.')
    time.sleep(INTERVAL_INBETWEEN_APICALLS_IN_SEC)

  def roll_rows_for_each_booktitle(self):
    for row in self.df.iterrows():
      # row is a 2D-tuple, first elem is 1-based-index int, second elem is a Series representing the row
      seq = row[0]
      self.instanceseq += 1
      series = row[1]
      try:
        title = series.title
      except (AttributeError, TypeError):
        continue
      self.call_googlebook_api_to_search_isbn_by_title(seq, title)

  def process(self):
    self.read_excel_to_pandas_df()
    self.roll_rows_for_each_booktitle()


def adhoctest():
  pass


def process():
  ISBNSearcher()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
