#!/usr/bin/env python3
"""
models/banks/bb/fi/bbfi_file_find.py

2023-10-10 RFDI BB rendimentos diários.csv
"""
# import settings as sett
import os.path
import models.banks.banksgeneral as bkgen
import models.banks.bankpropsmod as bkmd
# find_l2_or_l3_filepaths_by_year_month_opt_ext_substr
import fs.os.dateprefixed_dirtree_finder as dtfnd  # dtfnd.DatePrefixedOSFinder
import fs.datesetc.datehilofs as hilodt  # dtfnd.DatePrefixedOSFinder


class ReportProps:
  DAILY_RESULTS_MIDDLEPATH = 'BB FI Rendimentos Diários htmls'
  BCB_BANK3LETTER = 'bdb'
  ACOES = 'Ações'
  RFDI = 'RFDI'
  RFLP = 'RFLP'
  RESTYPES = [ACOES, RFDI, RFLP]
  CSV_INTERPOLATE = '{date} {typ} BB rendimentos no dia.csv'
  commapoint_htmlfilename_to_interpol = '{date} BB rendimentos no dia {commapointsep}.html'


class BBFIFileStaticFinder:

  @classmethod
  def get_basefolder_for_daily_results(cls):
    bbfi_folderpath = bkgen.BANK.get_bank_fi_folderpath_by_its3letter(ReportProps.BCB_BANK3LETTER)
    midpath = os.path.join(bbfi_folderpath, ReportProps.DAILY_RESULTS_MIDDLEPATH)
    return midpath

  @classmethod
  def form_csv_filename_for_date_n_type(cls, pdate, typ):
    if typ in ReportProps.RESTYPES:
      return ReportProps.CSV_INTERPOLATE.format(date=str(pdate), typ=typ)
    return None

  @classmethod
  def get_csv_filepath_for_date_n_type_or_raise(cls, pdate, reporttype=None):
    """
    filename = cls.form_csv_filename_for_date_n_type(pdate, reporttype)
    """
    basefolderpath = cls.get_basefolder_for_daily_results()
    dtprfx_dirtree = dtfnd.DatePrefixedOSFinder(basefolderpath)
    pdate = hilodt.make_date_with(pdate)
    ext = 'csv'
    filepaths = dtprfx_dirtree.find_l2_or_l3_filepaths_by_year_month_opt_day_ext_substr(
      pdate.year, pdate.month, pdate.day, ext, reporttype
    )
    if filepaths and len(filepaths) > 0:
      return filepaths[0]
    return None

  @classmethod
  def get_conventioned_commapoint_html_filenames(cls, pdate):
    """
    commapointsep is, for input, 'comma-sep'
    commapointsep is, for output, 'point-sep'
    """
    inputcommapointsep = 'comma-sep'
    outputcommapointsep = 'point-sep'
    conventioned_input = ReportProps.commapoint_htmlfilename_to_interpol.format(
      date=pdate, commapointsep=inputcommapointsep
    )
    conventioned_output = ReportProps.commapoint_htmlfilename_to_interpol.format(
      date=pdate, commapointsep=outputcommapointsep
    )
    return conventioned_input, conventioned_output

  @classmethod
  def get_conventioned_input_comma_html_filename(cls, pdate):
    return cls.get_conventioned_commapoint_html_filenames(pdate)[0]

  @classmethod
  def get_conventioned_output_point_html_filename(cls, pdate):
    return cls.get_conventioned_commapoint_html_filenames(pdate)[-1]


class BBFIFileFinder:

  Props = ReportProps
  UpperFinder = BBFIFileStaticFinder

  def __init__(self, pdate, reporttype=None):
    self.date = pdate
    self.reporttype = reporttype
    if self.reporttype is None:
      # default to the first one
      self.reporttype = self.Props.RFLP  # default
    self.staticfinder = BBFIFileStaticFinder()

  @property
  def csv_filename(self):
    return os.path.split(self.csv_filepath)[-1]

  @property
  def csv_filepath(self):
    return self.staticfinder.get_csv_filepath_for_date_n_type_or_raise(self.date, self.reporttype)

  def get_basefolder_for_daily_results(self):
    return self.UpperFinder.get_basefolder_for_daily_results()

  def get_csv_filepath_for_date_n_type_or_raise(self):
    return self.staticfinder.get_csv_filepath_for_date_n_type_or_raise(self.date, self.reporttype)

  def get_conventioned_commapoint_html_filenames(self):
    """
    commapointsep is, for input, 'comma-sep'
    commapointsep is, for output, 'point-sep'
    """
    conventioned_input, conventioned_output = BBFIFileStaticFinder.get_conventioned_commapoint_html_filenames(
      self.date
    )
    return conventioned_input, conventioned_output

  def get_conventioned_input_commasep_html_filename(self):
    return self.get_conventioned_commapoint_html_filenames()[0]

  def get_conventioned_output_pointsep_html_filename(self):
    return self.get_conventioned_commapoint_html_filenames()[-1]


def adhoctests():
  sfinder = BBFIFileStaticFinder()
  pdate = '2023-10-10'
  rtype = ReportProps.ACOES
  p = sfinder.form_csv_filename_for_date_n_type(pdate, rtype)
  print(p)
  p = sfinder.get_csv_filepath_for_date_n_type_or_raise(pdate, rtype)
  print(p)
  finder = BBFIFileFinder(pdate, rtype)
  p = finder.get_csv_filepath_for_date_n_type_or_raise()
  print('with finder', p)
  i, o = finder.get_conventioned_commapoint_html_filenames()
  print('input', i, 'output', o)
  sfinder = BBFIFileStaticFinder()


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctests()
