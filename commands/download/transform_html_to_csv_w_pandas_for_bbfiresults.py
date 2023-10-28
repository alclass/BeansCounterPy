#!/usr/bin/env python3
"""
commands/download/transform_html_to_csv_w_pandas_for_bbfiresults.py
  scrapes the HTML of BB rendimentos diários

https://scrapeops.io/python-web-scraping-playbook/best-python-html-parsing-libraries/

import requests
from lxml import html
url = 'https://quotes.toscrape.com/'
response = requests.get(url)
tree = html.fromstring(response.content)
quotes = tree.xpath('//div[@class="quote"]')
for quote in quotes:
    text = quote.xpath('.//span[@class="text"]/text()')[0]
    author = quote.xpath('.//small[@class="author"]/text()')[0]
    print(text)
    print(author)

"""
import datetime
import os
import shutil
import pandas as pd
import commands.download.convert_comma_to_point_as_decimal as commapoint
import fs.datesetc.datefs as dtfs


class WithPandasHtmlToCsvConverter:

  folderpath = (
    '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
    '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/'
    'BB FI Rendimentos Diários htmls/'
  )
  deccomma_html_filename_to_interpol = '{date} BB rendimentos no dia comma-sep.html'
  decpoint_html_filename_to_interpol = '{date} BB rendimentos no dia point-sep.html'
  csvfilename_to_interpol = '{date} {typ} BB rendimentos diários.csv'
  ACOES = 'Ações'
  RFDI = 'RFDI'
  RFLP = 'RFLP'
  csv_types = [ACOES, RFDI, RFLP]

  def __init__(self, pdate=None):
    self.date = pdate or datetime.date.today()
    self.df_list = None  # Data Frame List
    self.treat_date()

  def treat_date(self):
    if not isinstance(self.date, datetime.date):
      self.date = dtfs.return_date_or_recup_it_from_str(self.date)
      if not isinstance(self.date, datetime.date):
        error_msg = 'Error: program could not transform input date [%d] to object date' % self.date
        raise ValueError

  @property
  def deccomma_html_filename(self):
    return self.deccomma_html_filename_to_interpol.format(date=str(self.date))

  @property
  def decpoint_html_filename(self):
    return self.decpoint_html_filename_to_interpol.format(date=str(self.date))

  def get_csvfilename(self, typ='LP'):
    if typ not in self.csv_types:
      error_msg = 'Error: tipo (%s) relatório não disponível.' % str(typ)
      raise ValueError(error_msg)
    filename = self.csvfilename_to_interpol.format(date=str(self.date), typ=typ)
    return filename

  def get_filepath(self, filename):
    return os.path.join(self.folderpath, filename)

  def write_csvfile(self, df_table, typ):
    csvfilename = self.get_csvfilename(typ)
    filepath = self.get_filepath(csvfilename)
    if not os.path.isfile(filepath):
      print('Writing csv_output', csvfilename)
      df_table.to_csv(filepath)
    else:
      print('csv_output already exists, not disk-rewriting it.', csvfilename)

  def to_csv(self):
    # table RFDI
    df_table = self.df_list[-3]
    self.write_csvfile(df_table, self.RFDI)
    # table RFLP
    df_table = self.df_list[-2]
    self.write_csvfile(df_table, self.RFLP)
    # table ACOES
    df_table = self.df_list[-1]
    self.write_csvfile(df_table, self.ACOES)

  def to_pandas(self):
    print('Reading input_html to pandas:', self.decpoint_html_filename)
    filepath = self.get_filepath(self.decpoint_html_filename)
    self.df_list = pd.read_html(filepath)

  def backup_html_if_not_already(self):
    input_htmlfilepath = self.get_filepath(self.deccomma_html_filename)
    bakfolderpath = os.path.join(self.folderpath, 'bak')
    bakfilepath = os.path.join(bakfolderpath, self.deccomma_html_filename)
    if not os.path.isdir(bakfolderpath):
      os.makedirs(bakfolderpath)
    if not os.path.isfile(bakfilepath):
      print('Backing up', self.deccomma_html_filename)
      shutil.copy(input_htmlfilepath, bakfilepath)
    else:
      print('Already backed up', self.deccomma_html_filename)

  def convert_numbers_comma_to_point(self):
    input_filepath = self.get_filepath(self.deccomma_html_filename)
    output_filepath = self.get_filepath(self.decpoint_html_filename)
    commapoint.SingleFileConverter(input_filepath, output_filepath)

  def check_input_file_exists(self):
    filepath = self.get_filepath(self.deccomma_html_filename)
    if not os.path.isfile(filepath):
      scrmsg = (
        'Input file [%s] is missing.\n'
        '  Please, verify its existence in the appropriate folder.'
      ) % self.deccomma_html_filename
      print(scrmsg)
      return False
    return True

  def process(self):
    if not self.check_input_file_exists():
      return
    self.backup_html_if_not_already()
    self.convert_numbers_comma_to_point()
    self.to_pandas()
    self.to_csv()


def adhoctests():
  pass


def process():
  converter = WithPandasHtmlToCsvConverter()
  converter.process()


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
