#!/usr/bin/env python3
"""
list_triple_rends_from_db.py
  lists the triples rends, ie no mês, no ano, nos últimos 12 meses, on bank and refmonth range.
  Data may be fetched from db (sqlite for the time being) or files depending on their availability.
    Data sources (sqlite or datafiles) may change as this system grows a bit.
"""
import datetime
import sys
import fs.db.dbasfolder.discover_levels_for_datafolders as disc
import fs.datesetc.datefs as dtfs
import models.banks.banksgeneral
import models.banks.extractdistributor as extrdistr

DEFAULT_BANK3LETTER = 'bdb'
DEFAULT_YEAR = 2023


class TripleRendLister:

  def __init__(self, bank3letter, refmonthdate_ini, refmonthdate_fim):
    self.bank3letter = bank3letter
    self.refmonthdate_ini = refmonthdate_ini
    self.refmonthdate_fim = refmonthdate_fim
    self.bankpathdiscoverer = disc.FolderYearMonthLevelDiscovererForBankAndKind(self.bank3letter)

  def treat_ini_params(self):
    nonelist = []
    if self.bank3letter is None or not models.banks.banksgeneral.BANK.is3letter_available(self.bank3letter):
      nonelist.append('banklist')
    if self.refmonthdate_ini is None or type(self.refmonthdate_ini) != datetime.date:
      nonelist.append('refmonthdate_ini')
    if self.refmonthdate_fim is None or type(self.refmonthdate_fim) != datetime.date:
      nonelist.append('refmonthdate_fim')
    if len(nonelist) > 0:
      error_msg = 'Error: one or more params (%s) are missing for TripleRendLister.' % str(nonelist)
      raise ValueError(error_msg)

  def fetch_month_triplerend(self, refmonth):
    year = refmonth.year
    yearfolderpath = self.bankpathdiscoverer.get_folderpath_by_year(year)
    methodcall_hanldler = extrdistr.find_methodcall_on_bank3letter(self.bank3letter)
    extractor.process()
    for fundo in extractor.fundos:
      print('-'*40)
      print('name', fundo.name)
      print('refmonthdate', fundo.refmonthdate)
      print('prct_rend_mes', fundo.prct_rend_mes)
      print('prct_rend_desdeano', fundo.prct_rend_desdeano)
      print('prct_rend_12meses', fundo.prct_rend_12meses)

  def roll_refmonths(self):
    for refmonth in dtfs.generate_monthrange(self.refmonthdate_ini, self.refmonthdate_fim):
      self.fetch_month_triplerend(refmonth)

  def process(self):
    self.roll_refmonths()


def get_args_or_defaults():
  bank3letter = DEFAULT_BANK3LETTER
  refmonthdate_ini, refmonthdate_fim = None, None
  for arg in sys.argv:
    if arg in ['-h', '--help']:
      print(__doc__)
      sys.exit(0)
    elif arg.startswith('-b3l='):
      bank3letter = arg[len('-b3l='):]
    elif arg.startswith('-dmdini='):
      refmonthdate_ini = arg[len('-dmdini='):]
    elif arg.startswith('-dmdfim='):
      refmonthdate_fim = arg[len('-dmdfim='):]
  yyyydashmms = (refmonthdate_ini, refmonthdate_fim)
  rmdrange = dtfs.transform_yyyydashmm_to_daterange_from_strlist_or_recentyear(yyyydashmms)
  argdict = {'bank3letter': bank3letter, 'rmdrange': rmdrange}
  return argdict


def process():
  argdict = get_args_or_defaults()
  bank3letter = argdict['bank3letter']
  refmonthdate_ini, refmonthdate_fim = argdict['rmdrange']
  triple = TripleRendLister(bank3letter, refmonthdate_ini, refmonthdate_fim)
  triple.process()


def adhoctest():
  args = get_args_or_defaults()
  print(args)


if __name__ == '__main__':
  """
  """
  adhoctest()
  process()

