#!/usr/bin/env python3
"""
art/immeub/cdutra/cond/dldBalancetesMensaisCondCDutraFromFF.py

  downloads a month range (month_ini to month_fim)
    of monthly ledgers for the condominium
  (it's a simple and probably non-reusable script
    non-reusable, because it was elaborated for a particular case)

Usage:
      $<this_script> --mesini [<yyyy-mm>]  --mesfim [<yyyy-mm>]

Both parameters are optional, they default to:
  --mesfim => the current month or another related to given mesini
  --mesini => the month before the current one or another related to given mesfim
  Obs:
    a) if one refmonth (ini|fim) is given and the other not, the missing one will be related to the given one
    b) @see also method treat_refdates() below in class Downloader for all cases (given and None)

(previous) usage (deprecated):
    $<this_script> -refini="[<mm/yyyy>]"  -reffim="[<mm/yyyy>]"

Parameters:
  -refini means the first refmonthdate mm/yyyy beginning the time range
  -reffim means the last refmonthdate mm/yyyy ending the time range
  Both parameters are optional.
    ->defaulting:
      -reffim gets the current month if not given.
      -refini gets -reffim's previous month if not given.

Example:
    $<this_script> -refini="07/2023"  -reffim="09/2023"

It will try to download and save the following files
  on the script's working directory:
    2023-09 Balancete Mensal Cond CDutra.html
    2023-08 Balancete Mensal Cond CDutra.html
    2023-07 Balancete Mensal Cond CDutra.html

Notice on dates
 1) their server may have a limit on how past a month-ledger can be obtained
    (previously, it allowed 6 months past; it's been observed
      about a year maybe more on date (2023-09))
 2) a "future" file, ie a not filled-in one, will come up as empty

Notice on the "real estate code":

 1) the "real estate code" was withdrawn from the script and is necessary for running it;
 2) the code is a number used as a string to be inserted in the download URL;
 3) the code may be manually set hardcoded (in constant DEFAULT_IMMEUBCODE)
    or, maybe better, put in a config file.
"""
import argparse
import copy
import datetime
from dateutil.relativedelta import relativedelta  # for adding & subtracting months in dates
import lib.datesetc.refmonths_mod as rmd
import os
import sys
parser = argparse.ArgumentParser(description="Baixa balancete mensal CDutra")
parser.add_argument("--mesini", type=str,
                    help="mês referência inicial")
parser.add_argument("--mesfim", type=str, default=None,
                    help="mês referência final")
args = parser.parse_args()


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


explain_name = 'balancete sintético mensal Cond CDutra'
DEFAULT_IMMEUBCODE = '0154'
filename_to_interpol = "{year}-{month:02d} " + explain_name + ".html"
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
    """
    Garantees that both refmonth_ini and refmonth_fim are set.
    (The algorithm below shows how None values are treated -- how the default months are applied if needed.)
    Obs: this method does not impede future dates.
    """
    self.refmonth_ini = rmd.make_refmonthdate_or_none(self.refmonth_ini)
    self.refmonth_fim = rmd.make_refmonthdate_or_none(self.refmonth_fim)
    if self.refmonth_ini is None:
      # okay, refmonth_ini will now depend on refmonth_fim
      if self.refmonth_fim is None:
        # okay, make refmonth_fim be current month
        self.refmonth_fim = rmd.make_current_refmonthdate()
      # okay, refmonth_fim is at this point set and refmonth_ini is it minus one month
      self.refmonth_ini = self.refmonth_fim - relativedelta(months=1)
      # okay, the two are set, let's return
      return
    # alright, at this point, refmonth_ini is set, but we still have to check refmonth_fim
    if self.refmonth_fim is None:
      # okay, make it one month later from refmonth_ini
      self.refmonth_fim = self.refmonth_ini + relativedelta(months=1)
      # okay, the two are set, let's return
      return
    # okay, at this point, both ini and fim were set, let's test which is greater
    if self.refmonth_ini > self.refmonth_fim:
      # and swap them if ini is greater than fim
      tmp_rmd = self.refmonth_fim
      self.refmonth_fim = self.refmonth_ini
      self.refmonth_ini = tmp_rmd

  def treat_immeubcode(self):
    error_msg_to_interpol = (
        'Error: the real estate code is missing or malformed (%s), program can not continue.'
        ' Please, enter it into the configuration file available (preferable) or'
        ' into the script itself hardcoded (constant DEFAULT_IMMEUBCODE).'
    )
    if self.immeubcode is None:
      try:
        self.immeubcode = DEFAULT_IMMEUBCODE
        return
      except NameError:
        error_msg = error_msg_to_interpol % "not defined"
        print(error_msg)
        sys.exit(1)
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


def get_args_old():
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


def get_args():
  mesini = args.mesini
  mesfim = args.mesfim
  return mesini, mesfim


def process():
  refmonth_ini, refmonth_fim = get_args()
  d = Downloader(refmonth_ini, refmonth_fim)
  d.process()


if __name__ == '__main__':
  process()
