#!/usr/bin/env python3
"""
models/banks/bb/fi/fibb_daily_results_html_to_csv_via_pandas_transform.py
"""
import datetime
import os
import shutil
import pandas as pd
import models.banks.bb.fi.fibb_daily_results_numbers_comma_to_point_convert as commapoint
import models.banks.bankpathfinder as pthfnd  # .BankOSFolderFileFinder
import fs.datesetc.datehilofs as hilodt
# import fs.datesetc.datefs as dtfs


class WithPandasHtmlToCsvConverter:

  deccomma_html_filename_to_interpol = '{date} BB rendimentos no dia comma-sep.html'
  decpoint_html_filename_to_interpol = '{date} BB rendimentos no dia point-sep.html'
  csvfilename_to_interpol = '{date} {typ} BB rendimentos no dia.csv'
  ACOES = pthfnd.BankOSFolderFileFinder.ACOES
  RFDI = pthfnd.BankOSFolderFileFinder.RFDI
  RFLP = pthfnd.BankOSFolderFileFinder.RFLP
  csv_types = [ACOES, RFDI, RFLP]
  TYPRE = pthfnd.BankOSFolderFileFinder.REND_RESULTS_KEY
  BDB_BANK3LETTER = 'bdb'

  def __init__(self, pdate=None):
    self.date = pdate or datetime.date.today()
    self.df_list = None  # Data Frame List
    self.treat_date()

  def treat_date(self):
    if not isinstance(self.date, datetime.date):
      self.date = hilodt.make_date_or_none(self.date)
      if not isinstance(self.date, datetime.date):
        error_msg = 'Error: program could not transform input date [%s] to object date' % str(self.date)
        raise ValueError(error_msg)

  @property
  def folderpath(self):
    """
      folderpath = (
        '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
        '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/'
        'BB FI Rendimentos Diários htmls/'
      )
    """
    pthfnder = pthfnd.BankOSFolderFileFinder(self.BDB_BANK3LETTER, self.TYPRE)
    _folderpath = pthfnder.find_or_create_l2yyyymm_folderpath_by_year_month_substr(self.date.year, self.date.month)
    return _folderpath

  @property
  def deccomma_html_filepath(self):
    return os.path.join(self.folderpath, self.deccomma_html_filename)

  @property
  def deccomma_html_filename(self):
    return self.deccomma_html_filename_to_interpol.format(date=str(self.date))

  @property
  def decpoint_html_filepath(self):
    return os.path.join(self.folderpath, self.decpoint_html_filename)

  @property
  def decpoint_html_filename(self):
    return self.decpoint_html_filename_to_interpol.format(date=str(self.date))

  def get_csvfilename(self, ptypre=None):
    typre = ptypre or self.RFLP
    if typre not in self.csv_types:
      error_msg = 'Error: tipo (%s) relatório não disponível.' % str(typre)
      raise ValueError(error_msg)
    filename = self.csvfilename_to_interpol.format(date=str(self.date), typ=typre)
    return filename

  def get_csv_filepath_by_typre(self, ptypre=None):
    typre = ptypre or self.RFLP
    filename = self.get_csvfilename(typre)
    return self.get_csv_filepath_w_filename(filename)

  def get_csv_filepath_w_filename(self, filename):
    return os.path.join(self.folderpath, filename)

  def write_csvfile(self, df_table, typ):
    csvfilename = self.get_csvfilename(typ)
    filepath = self.get_csv_filepath_w_filename(csvfilename)
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
    filepath = self.get_csv_filepath_w_filename(self.decpoint_html_filename)
    self.df_list = pd.read_html(filepath)

  def backup_html_if_not_already(self):
    """
    This method is no longer used, though is left here as reference.
    In the beginning, its function was to copy the "comma separated html" to the "bak" directory
    After that, the "comma separated htmls" were left on the processing folder with all the other files.
    """
    input_htmlfilepath = self.get_csv_filepath_w_filename(self.deccomma_html_filename)
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
    input_filepath = self.get_csv_filepath_w_filename(self.deccomma_html_filename)
    output_filepath = self.get_csv_filepath_w_filename(self.decpoint_html_filename)
    commapoint.SingleFileConverter(input_filepath, output_filepath)

  def check_input_file_exists(self):
    filepath = self.get_csv_filepath_w_filename(self.deccomma_html_filename)
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
    # self.backup_html_if_not_already()
    self.convert_numbers_comma_to_point()
    self.to_pandas()
    self.to_csv()

  def __str__(self):
    outstr = """
    date  = {date} 
    htmlfile  = {htmlfile}
    """.format(date=self.date, htmlfile=self.deccomma_html_filename)
    return outstr


def process():
  """

  """
  pdate = '2023-11-03'
  converter = WithPandasHtmlToCsvConverter(pdate)
  converter.process()


def adhoctests():
  """

  """
  pass


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
