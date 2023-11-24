#!/usr/bin/env python3
"""
commands/download/fibb_daily_results_numbers_comma_to_point_convert.py

"""
import datetime
import os
import fs.datesetc.datehilofs as hilodt
import fs.os.osfunctions as osfs
import fs.re.refunctions as decpla
import models.banks.bb.fi.bbfi_file_find as ffnd  # for ffnd.BBFIFileFinder.Props.commapoint_htmlfilename_to_interpol
import models.banks.bankpathfinder as pthfnd  # .BankOSFolderFileFinder
import models.banks.bb.fi.fibb_daily_results_html_to_csv_via_pandas_transform as trnsf  # WithPandasHtmlToCsvConverter
from argparse import ArgumentParser
# TO-DO this hardcoded constant below will be changed in the future to a config class that informs the paths
DEFAULT_FOLDERPATH = (
  '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
  '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/'
  'BB FI Rendimentos Diários htmls/'
)
BDB_BANK3LETTER = 'bdb'


class SingleFileConverter:
  def __init__(self, input_filepath=None, output_filepath=None):
    self.bank3letter = BDB_BANK3LETTER
    self._date = None  # date is extracted from input_filename
    self._finder = None
    self.input_filepath = input_filepath
    self.output_filepath = output_filepath
    self.treat_filepaths()  # in case of None, it will stablish the defaults for input and/or output paths
    # self.process()  # should be called 'externally' by the object

  def treat_filepaths(self):
    """
    The treatment is the following:
      1 if input filepath does not exist, the default one (prefixed with today's date) is gotten
      2 input filename is conventioned, so it should be checked
      3 output_filepath is not checked for existence here (see next item below)
      4 in case output file is in a different directory, create/make it if it does not exist
      5 in case output_filepath already exists, processing ahead will return and not recreate it
      6 if the user wants to recreate it, she/he must delete it first
      7 if output_folderpath does not exist, it is created/made
    """
    if not os.path.isfile(self.input_filepath):
      error_msg = f'Input file [{self.input_filepath}] does not exist. Please, place it in folder and rerun.'
      raise OSError(error_msg)
    # 1 if input filepath is None, the default one (prefixed with today's date) is gotten
    if self.input_filepath is None:
      # at this point, finder may not yet have been initialized, get one with today's date (needed for the default)
      today = datetime.date.today()
      bfinder = ffnd.BBFIFileFinder(today, ffnd.BBFIFileFinder.Props.ACOES)
      input_filename = bfinder.get_conventioned_input_commasep_html_filename()
      findertypecat = pthfnd.BankOSFolderFileFinder.REND_RESULTS_KEY
      pthfinder = pthfnd.BankOSFolderFileFinder(self.bank3letter, findertypecat)
      folderpath = pthfinder.find_l2yyyymm_folderpath_by_year_month_typ(year=self.date.year, month=self.date.month)
      self.input_filepath = os.path.join(folderpath, input_filename)
    # date can be extracted after the check above, for it will look up the prefix in the input filename
    _ = self.date
    # 2 input filename is conventioned, so it should be checked
    conventioned_input, conventioned_output = self.get_conventioned_filenames()
    if self.input_filename != conventioned_input:
      error_msg = 'Error: input filename [%s] is different than conventioned  [%s]' % \
                  (self.input_filename, conventioned_input)
      raise OSError(error_msg)
    if self.output_filepath is None:
      self.set_conventioned_output_filepath()
    else:
      # 4 in case output file is in a different directory, create/make it if it does not exist
      try:
        output_folderpath, _ = os.path.split(self.output_filepath)
        if not os.path.isdir(output_folderpath):
          print('Creating directory', output_folderpath)
          os.makedirs(output_folderpath)
      except OSError:
        self.set_conventioned_output_filepath()
    output_folderpath, output_filename = os.path.split(self.output_filepath)
    if output_filename != conventioned_output:
      error_msg = 'Error: output filename [%s] is different than conventioned  [%s]' % \
                  (output_filename, conventioned_output)
      raise OSError(error_msg)

  @property
  def input_filename(self):
    return os.path.split(self.input_filepath)[-1]

  @property
  def output_filename(self):
    if self.output_filepath:
      return os.path.split(self.output_filepath)[-1]
    # it's expected this is transient until treat_filepaths() is completed
    # anyway, the conventioned filenames are the ones required!
    return self.get_conventioned_filenames()[-1]

  @property
  def finder(self):
    if self._finder is None:
      _ = self.date
      # finder here does not use the 'typ' (Report Type) parameter, but one is given for instantiation
      self._finder = ffnd.BBFIFileFinder(self.date, ffnd.BBFIFileFinder.Props.ACOES)
    return self._finder

  @property
  def date(self):
    if self._date is None:
      try:
        pp = self.input_filename.split(' ')
        pdate = pp[0]
        self._date = hilodt.make_date_or_none(pdate)
        if not isinstance(self._date, datetime.date):
          # default is today's date
          self._date = datetime.date.today()
      except TypeError:
        # when None is input in init's parameter input_filepath, date defaults to today's date
        self._date = datetime.date.today()
    return self._date

  def get_conventioned_filenames(self):
    """
    name_to_interpol = '{date} BB rendimentos no dia {commapointsep}.html'
    conventioned_input = name_to_interpol.format(date=self.date, commapointsep='comma-sep')
    conventioned_output = name_to_interpol.format(date=self.date, commapointsep='point-sep')
    return conventioned_input, conventioned_output
    """
    return self.finder.get_conventioned_commapoint_html_filenames()

  def set_conventioned_output_filepath(self):
    """
      The output html filename is named conventioned.
      At this moment, the convention is:
      input => "{date} BB rendimentos no dia {'comma-sep'}.html"
      output => "{date} BB rendimentos no dia {'point-sep'}.html"
    """
    input_folderpath, filename = os.path.split(self.input_filepath)
    _, outputfilename = self.get_conventioned_filenames()
    self.output_filepath = os.path.join(input_folderpath, outputfilename)

  def convert_numbers_comma_to_point_n_savefile(self):
    scrmsg = """SingleFileConverter: Converting comma to point from file to file: 
    input:  [{inputfilename}]
    output: [{outputfilename}]
    """.format(inputfilename=self.input_filename, outputfilename=self.output_filename)
    print(scrmsg)
    input_text = open(self.input_filepath).read()
    output_text = decpla.convert_decimalplace_comma_to_point_via_re_for(input_text)
    _ = osfs.save_file_with_text(self.output_filepath, output_text)

  def outputfile_already_exists(self):
    if os.path.isfile(self.output_filepath):
      scrmsg = 'Output file [%s] already exists. Continuing.' % self.output_filename
      print(scrmsg)
      return True
    return False

  def process(self):
    if self.outputfile_already_exists():
      return
    self.convert_numbers_comma_to_point_n_savefile()


class BatchConverter:

  def __init__(self):
    self.seq = 0
    self.inputfilepaths = None
    # self.set_inputfilepaths_w_ext_from_folder_or_empty()

  def set_inputfilepaths_w_ext_from_folder_or_empty(self, pfolderpath=None, dotext=None):
    """
      It looks up files in folder with the given extension.
      For that, it calls a function in module osfs that uses built-in 'glob'.
    """
    if pfolderpath is not None and os.path.isdir(pfolderpath):
      ifolderpath = pfolderpath
    else:
      ifolderpath = DEFAULT_FOLDERPATH
    if dotext is None:
      dotext = '*.html'
    htmlpaths = osfs.retrieve_filepaths_in_folder_or_empty(ifolderpath, dotext)
    self.inputfilepaths = sorted(filter(lambda e: e.find('comma-sep') > -1, htmlpaths))

  def convert_comma_to_point_for_numbers_in_file(self, input_filepath):
    """
    print(self.seq, 'Converting', filename)
    input_text = open(inputfilepath).read()
    output_text = decpla.convert_decimalplace_comma_to_point_via_re_for(input_text)
    _ = osfs.save_file_with_text(output_filepath, output_text)
    return output_text

    """
    # pass None as output_filepath to SingleFileConverter for it will find it by convention
    self.seq += 1
    fileconverter = SingleFileConverter(input_filepath, None)
    output_filepath = fileconverter.output_filepath
    output_filename = os.path.split(output_filepath)[-1]
    if os.path.isfile(output_filepath):
      scrmsg = '%d File already exists. Not processing it. [%s]' % (self.seq, output_filename)
      print(scrmsg)
      return None
    scrmsg = 'Converting ' + str(self.seq) + ' => ' + output_filename
    print(scrmsg)
    fileconverter.process()

  def process(self):
    if self.inputfilepaths is None:
      self.set_inputfilepaths_w_ext_from_folder_or_empty()
    self.seq = 0
    for inputfilepath in self.inputfilepaths:
      self.convert_comma_to_point_for_numbers_in_file(inputfilepath)


def get_input_output_filepaths(pdate):
    pdate = hilodt.make_date_or_none(pdate)
    converter = trnsf.WithPandasHtmlToCsvConverter(pdate)
    input_filepath = converter.deccomma_html_filepath
    output_filepath = converter.decpoint_html_filepath
    return input_filepath, output_filepath


def get_args():
  """
  Suppose parameters given are: -d '2023-11-03'
  args = Namespace(date=['2023-11-03'])
  pdate = args.date[0]
  """
  parser = ArgumentParser()
  parser.add_argument(
    '-d', '--date', metavar='yearmonthday', type=str, nargs=1,
    help="the date for finding its daily exchange rate quotes",
  )
  args = parser.parse_args()
  return args


def adhoctests():
  converter = BatchConverter()
  converter.process()


def process():
  args = get_args()
  if args.date is not None:
    pdate = args.date[0]
  else:
    pdate = datetime.date.today()
  print(pdate, args)
  input_filepath, output_filepath = get_input_output_filepaths(pdate)
  sfc = SingleFileConverter(input_filepath, output_filepath)
  sfc.process()


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
