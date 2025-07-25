#!/usr/bin/env python3
"""
art/books/book_chosen_opener_in_browser.py
  accepts an ISBN or title from the command line and, if related book is in db,
    opens its Packt's webpage on the default browser.

Observation on books webpage URL:
The URL-Base below only works for authenticated users
  and doesn't seem to work for anonymous browsing:
    URL_to_interpole = 'https://www.packtpub.com/book/data/{isbn13}'
  Same to the URL below:
    https://subscription.packtpub.com/search?query=9781785888731

An alternative is this second option:
  URL_to_interpole = https://www.packtpub.com/product/atitle/{isbn13}'
obs: 'atitle', just the string, doesn't avoid the page-redirection at packtpub.com

https://subscription.packtpub.com/search?query=9781786469687
"""
import os
import random
import pandas as pd
import art.books.functions_packt_books_data_excel_json_pandas as isbnfs
# URL_to_interpole = 'https://subscription.packtpub.com/search?query={isbn13}/1'
# URL_to_interpole = 'https://www.packtpub.com/product/atitle/{isbn13}/1'
URL_to_interpole = 'https://subscription.packtpub.com/book/data/{isbn13}/'
BROWSER_COMM = 'xdg-open'
BROWSER_CLI_TO_INTERPOL = '{browsercomm} "{url}"'


def ask_continuation(scrseq):
  scrmsg = f'At i={scrseq}. Continue another page opening (Y/n) [ENTER] means Yes.'
  ans = input(scrmsg)
  if ans in ['y', 'y', '']:
    return True
  else:
    return False


class BookPageOpener:

  def __init__(self):
    self.n_isbns = 0
    self.n_rows_w_na = 0
    self.n_rows = 0
    self.instanceseq = 0
    self.df = None
    self.dateprefixed_excelfilepath = isbnfs.search_mostrecent_dateprefixed_excelfile_in_folder()
    self.process()

  def issue_cli_to_browser_open_bookpage(self, series):
    """
    if self.instanceseq % 3 == 0:
      if self.instanceseq < 11:
        return True
      return ask_continuation(self.instanceseq)
    return True

    """
    title = series.title
    isbn13liststr = series.isbn13liststr
    if isbn13liststr.find(', ') > -1:
      isbn13list = isbn13liststr.split(', ')
    else:
      isbn13list = isbn13liststr.strip(' \t\r\n')
    for i, isbn13 in enumerate(isbn13list):
      url = URL_to_interpole.format(isbn13=isbn13)
      n_isbns_of_title = i + 1
      print(self.instanceseq, 'n_isbns_of_title', n_isbns_of_title, isbn13, title)
      cli = BROWSER_CLI_TO_INTERPOL.format(browsercomm=BROWSER_COMM, url=url)
      print(cli)
      os.system(cli)
      if ask_continuation(self.instanceseq):
        continue
      else:
        return False
    return True

  def init_dataframe(self):
    self.df = pd.read_excel(self.dateprefixed_excelfilepath)
    self.n_rows = self.df.shape[0]

  def consume_frame_popping_series(self):
    nrows = self.df.shape[0]
    iloop = 0
    while nrows > 0:
      r = random.randint(0, nrows-1)
      idx = self.df.index[r]
      series = self.df.loc[idx]
      print(self.df.index)
      self.df.drop(idx, axis=0, inplace=True)
      print('len', nrows, ' rand =', r, ' del_idx =', idx, 'Series =>',  series.title, series.isbn13liststr)
      self.instanceseq += 1
      do_continue = self.issue_cli_to_browser_open_bookpage(series)
      _ = do_continue
      iloop += 1
      if iloop > 1000:
        break
      nrows = self.df.shape[0]

  def randomroll_isbns_if_any(self):
    n_rows = self.df.shape[0]
    iloop = 0
    while n_rows - 1 > 0:
      r = random.randint(0, n_rows-1)
      print(self.df.head())
      print('df_rows', n_rows, 'randint', r)
      series = self.df.iloc[r]
      print('series', series)
      # idxloc = self.df[self.df.iloc[r]]
      self.df.drop(series.seq, axis=0, inplace=True)  # axis=0,
      print('after dropping a row, df_rows =', n_rows)
      iloop += 1
      if iloop > 1000:
        break
      n_rows = self.df.shape[0]

  def roll_isbns_if_any(self):
    for row in self.df.iterrows():
      seq = row[0]
      self.instanceseq += 1
      series = row[1]
      try:
        isbn13 = series.isbn
        title = series.title
        print(seq, isbn13, title)
        # do_continue = self.issue_cli_to_browser_open_bookpage(seq, isbn13, title)
        do_continue = True
        if not do_continue:
          break
      except (AttributeError, TypeError):
        self.n_rows_w_na += 1
        continue

  def process(self):
    if not self.dateprefixed_excelfilepath:
      print('There is no date prefixed excel file available (eg "2023-11-17 data.xlsv").')
      print('Data folder looked up:', isbnfs.get_bookdata_dirpath())
      return False
    self.init_dataframe()
    self.consume_frame_popping_series()
    # self.randomroll_isbns_if_any()
    # self.roll_isbns_if_any()
    return True

  def __str__(self):
    return f"""BookPageOpener:
    n_isbns = {self.n_isbns}
    n_rows_w_na = {self.n_rows_w_na}
    df_rows = {self.n_rows}
    instanceseq = {self.instanceseq}
    dateprefixed_excelfilepath = {self.dateprefixed_excelfilepath}
    """


def adhoctest():
  pass


def process():
  bpo = BookPageOpener()
  print(bpo)


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
