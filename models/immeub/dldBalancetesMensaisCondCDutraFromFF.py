#!/usr/bin/env python3
"""
dldBalancesMensaisCondCDutraFromFF.py
  downloads a month range (month_ini to month_fim) of monthly ledgers for the condominium
  (it's a simple and probably non-reusable script for it was elaborated for a particular case)

Usage:
    $dldBalancesMensaisCondCDutraFromFF.py -refini="[<mm/yyyy>]"  -reffim="[<mm/yyyy>]"

Parameters:
  -refini means the first refmonthdate mm/yyyy beginning the time range
  -reffim means the last refmonthdate mm/yyyy ending the time range
  Both parameters are optional.
    ->defaulting:
      -reffim gets the current month if not given.
      -refini gets -reffim's previous month if not given.

Example:
    $dldBalancesMensaisCondCDutraFromFF.py -refini="07/2023"  -reffim="09/2023"

It will try to download and save the following files on the script's working directory:
  2023-09 Balancete Mensal Cond CDutra.html
  2023-08 Balancete Mensal Cond CDutra.html
  2023-07 Balancete Mensal Cond CDutra.html

Notice on dates
 1) their server may have a limit on how past a month-ledger can be obtained
    (previously, it allowed 6 months past; it's been observed about a year maybe more on date (2023-09))
 2) a "future" file, ie a not filled-in one, will come up as empty

Notice on the "real estate code"
 1) the "real estate code" was withdrawn from the script and is necessary for running it;
 2) the code is a number used as a string to be inserted in the download URL;
 3) the code may be manually set hardcoded (in constant DEFAULT_IMMEUBCODE)
    or, maybe better, put in a config file.
"""
import copy
import datetime
from dateutil.relativedelta import relativedelta  # for adding & subtracting months in dates
import os
import sys
import fs.datesetc.datefs as dtfs
import settings as sett
CDUT_IMMEUBCODE_IN_FF = sett.CDUT_IMMEUBCODE_IN_FF


def extract_ref_from_cli(clistr):
  pos = clistr.find('period=')
  if pos > -1:
    posini = pos + len('period=')
    strmmdashyyyy = clistr[posini: posini+8]
    return strmmdashyyyy
  return 'refmonth not found'


def transform_str_to_date_or_none(pdate):
  if pdate is None:
    return None
  try:
    pdate = str(pdate)
    pp = pdate.split('/')
    mm = int(pp[0])
    yyyy = int(pp[1])
    return datetime.date(year=yyyy, month=mm, day=1)
  except (IndexError, ValueError):  # there is no AttributeError hear for None is tested above
    pass
  return None


# DEFAULT_IMMEUBCODE = None  # for the time being, code must be hardcoded here
filename_to_interpol = "{year}-{month:02d} Balancete Mensal Cond CDutra.html"
cli_to_interpol = ('wget -c "https://fernandoefernandes.com.br/'
                   'ffnet_sys/sefudoff.php?cod={immeubcode}&period={month:02d}/{year}"'
                   ' -O "' + filename_to_interpol + '"')


class Downloader:
  def __init__(self, refmonth_ini=None, refmonth_fim=None, p_immeubcode=None):
    self.refmonth_ini = refmonth_ini
    self.refmonth_fim = refmonth_fim
    self.commandlines = []
    self.treat_refdates()
    print('refmonth_ini =',  self.refmonth_ini, 'refmonth_fim =', self.refmonth_fim)
    self.immeubcode = p_immeubcode
    self.treat_immeubcode()

  def treat_refdates(self):
    self.refmonth_fim = dtfs.make_date_w_day1_or_w_current_months_firstday(self.refmonth_fim)
    self.refmonth_ini = dtfs.make_date_w_day1_or_w_current_months_firstday(self.refmonth_ini)

  def treat_immeubcode(self):
    error_msg_to_interpol = (
        'Error: the real estate code is missing or malformed (%s), program can not continue.'
        ' Please, enter it into the configuration file available (preferable) or'
        ' into the script itself hardcoded (constant CDUT_IMMEUBCODE_IN_FF).'
    )
    if self.immeubcode is None:
      try:
        self.immeubcode = CDUT_IMMEUBCODE_IN_FF
        return
      except NameError:
        error_msg = error_msg_to_interpol % "not defined"
        print(error_msg)
        sys.exit(1)
        # raise ValueError(error_msg)
    try:
      self.immeubcode = str(self.immeubcode)
      _ = int(self.immeubcode)  # as for now, these codes are integers, though used as string here
    except ValueError:
      error_msg = error_msg_to_interpol % str(self.immeubcode)
      raise ValueError(error_msg)

  def prep_commandlines(self):
    current_date = copy.copy(self.refmonth_fim)
    while current_date >= self.refmonth_ini:
      year = current_date.year
      month = current_date.month
      filename = filename_to_interpol.format(year=year, month=month)
      if os.path.isfile(filename):
        print('OBS file', filename, 'is already present on folder.')
      else:
        cli = cli_to_interpol.format(year=year, month=month, immeubcode=self.immeubcode)
        self.commandlines.append(cli)
      current_date = current_date - relativedelta(months=1)

  def confirm_downloads(self):
    if len(self.commandlines) == 0:
      print('No files to download.')
      return False
    for clistr in self.commandlines:
      print(clistr)
    print('-'*40)
    scrmsg = 'Confim the %d downloads above? (*Y/n) [ENTER] means yes ' % len(self.commandlines)
    ans = input(scrmsg)
    if ans in ['Y', 'y', '']:
      return True
    return False

  def do_download(self):
    for clistr in self.commandlines:
      extract_ref_from_cli(clistr)
      print('Downloading ref ', )
      retval = os.system(clistr)
      if retval == 0:
        print('downloaded, going to next if not the last one')

  def process(self):
    self.prep_commandlines()
    if self.confirm_downloads():
      self.do_download()


def get_args():
  """
  Example: -refini="01/2023" -reffim="05/2023"
  @see also __doc__ above
  :return:
  """
  refmonth_ini, refmonth_fim = None, None
  for arg in sys.argv:
    if arg.startswith('-h') or arg.startswith('--help'):
      print(__doc__)
      sys.exit(0)
    elif arg.startswith('-refini='):
      refmonth_ini = arg[len('-refini='):]
    elif arg.startswith('-reffim='):
      refmonth_fim = arg[len('-reffim='):]
  return refmonth_ini, refmonth_fim


def process():
  refmonth_ini, refmonth_fim = get_args()
  if refmonth_ini is None:
    refmonth_ini = dtfs.make_date_w_day1_or_w_current_months_firstday()
  d = Downloader(refmonth_ini, refmonth_fim)
  d.process()


if __name__ == '__main__':
  process()
