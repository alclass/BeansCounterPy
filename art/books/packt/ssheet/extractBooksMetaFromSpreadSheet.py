#!/usr/bin/env python3
"""
art/books/packt/ssheet/extractBooksMetaFromSpreadSheet.py
  Extracts metadata from Packt's (selected/owned) books from a spreadsheet (Calc or Excel via pandas)
  previously:
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
import art.books.packt.ssheet.functions_packt_books_data_excel_json_pandas as isbnfs
from art.books.packt.folders import BookInfoDC
# URL_to_interpole = 'https://subscription.packtpub.com/search?query={isbn13}/1'
# URL_to_interpole = 'https://www.packtpub.com/product/atitle/{isbn13}/1'
URL_to_interpole = 'https://subscription.packtpub.com/book/data/{isbn13}/'
BROWSER_COMM = 'xdg-open'
BROWSER_CLI_TO_INTERPOL = '{browsercomm} "{url}"'
# e.g. https://subscription.packtpub.com/book/business-other/9781788837361
PACKTS_URL_PREFIX = "https://subscription.packtpub.com/book/"


def extract_knowledgearea_n_isbn13(url: str) -> tuple:
  try:
    remaining = url[len(PACKTS_URL_PREFIX):]
    pp = remaining.split('/')
    packts_midurl_ka = pp[0]
    isbn13 = pp[1]
    if len(isbn13) != 13:
      warnmsg = f'isbn13 {isbn13} has not 13 chars'
      print(warnmsg)
    return packts_midurl_ka, isbn13
  except (AttributeError, IndexError, TypeError):
    pass
  return None, None


def ask_continuation(scrseq):
  scrmsg = f'At i={scrseq}. Continue another page opening (Y/n) [ENTER] means Yes.'
  ans = input(scrmsg)
  if ans in ['y', 'y', '']:
    return True
  else:
    return False


class PacktsSpreadSheetReader:

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
    """
    title	pubdate	authors	url
    ('Unnamed: 0', empty-column)
    ('Unnamed: 1', 'seq') ('Unnamed: 2', 'title') ('Unnamed: 3', 'year') ('Unnamed: 4', 'authors') ('Unnamed: 5', 'url')
    """
    self.df = pd.read_excel(self.dateprefixed_excelfilepath)
    self.n_rows = self.df.shape[0]
    # Rename specific columns
    self.df = self.df.rename(columns={"Unnamed: 1": "seq"})
    self.df = self.df.rename(columns={"Unnamed: 2": "title"})
    self.df = self.df.rename(columns={"Unnamed: 3": "year"})
    self.df = self.df.rename(columns={"Unnamed: 4": "authors"})
    self.df = self.df.rename(columns={"Unnamed: 5": "url"})

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

  def generate_all_records(self):
    for idx, row in enumerate(self.df.iterrows()):
      if idx < 2:
        # ignore idx 0 and 1
        continue
      try:
        series = self.df.loc[idx]
        title = series['title']
        authors = series['authors']
        year = series['year']
        url = series['url']
        packts_midurl_ka, isbn13 = extract_knowledgearea_n_isbn13(url)
        if isbn13:
          self.n_isbns += 1
        bookinfo_dc = BookInfoDC(
          title=title,
          year=year,
          authors=authors,
          isbn13=isbn13,
          packts_midurl_ka=packts_midurl_ka
        )
        yield bookinfo_dc

      except (AttributeError, TypeError):
        self.n_rows_w_na += 1
        print('AttributeError, TypeError', self.n_rows_w_na)
        continue

  def print_all_records(self):
    for i, bookinfo_dc in enumerate(self.generate_all_records()):
      line = f"{bookinfo_dc}"
      seq = i + 1
      print(seq, line)

  def roll_isbns_if_any(self):
    for row in self.df.iterrows():
      seq = row[0]
      self.instanceseq += 1
      series = row[1]
      try:
        isbn13 = series.isbn13
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
    self.print_all_records()
    # self.consume_frame_popping_series()
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
  bpo = PacktsSpreadSheetReader()
  print(bpo)


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
