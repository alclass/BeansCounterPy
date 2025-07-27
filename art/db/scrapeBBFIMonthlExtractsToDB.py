#!/usr/bin/env python3
""""
scrape_monthly_rendextracts.py
  Organizes the month range and then calls bbScraperWithFileText.py month to month
"""
import datetime
import os.path
import models.banks.bb.fi.bbScraperWithFileText as bbScrp
import lib.os.oshilofunctions as hilo
import models.banks.banksgeneral as bkge
# from models.extractFromWithinAFundoReport import WithinFundoExtractScraper
import lib.db.dbasfolder.lookup_monthrange_convention_from_basedatafolder_on as lkup

YEARMONTH_INI = datetime.date(year=2022, month=8, day=1)
YEARMONTH_FIM = datetime.date(year=2023, month=8, day=1)
BB_BANK3LETTER = 'bdb'


class BBFIDataFilesToDBInsertor:

  def __init__(self, bank3letter=None):
    """
    # self.financkind = financkind
    """
    self.bank3letter = bank3letter
    self.treat_bank3letter()
    fibasedirpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(self.bank3letter)
    self.finder = lkup.DatePrefixedOSEntriesFinder(fibasedirpath)
    self.fundos = []
    # self.yearmonth_ini = self.finder.refmonth_ini
    # self.yearmonth_fim = self.finder.refmonth_fim

  def treat_bank3letter(self):
    if self.bank3letter is None or not bkge.BANK.does_bank3letter_exist(self.bank3letter):
      self.bank3letter = BB_BANK3LETTER
    if not bkge.BANK.does_bank3letter_exist(self.bank3letter):
      error_msg = 'Error: bank3letter [%s] does not exist.' % self.bank3letter
      raise ValueError(error_msg)

  def traverse_months(self):
    for filepath in self.finder.gen_filepaths_within_daterange_or_wholeinterval():
      filename = os.path.split(filepath)[-1]
      refmonthdate = hilo.derive_refmonthdate_from_a_yearmonthprefixedstr(filename)
      scrapetext = open(filepath, encoding='latin1').read()
      fundo = bbScrp.BBExtractScraperWithFileText(scrapetext, refmonthdate)
      if fundo.refmonthdate is None:
        continue
      print(fundo)

  def process(self):
    self.traverse_months()

  def __str__(self):
    classname = str(__class__)
    outstr = '<{classname} dateini={dateini} datefim={datefim}>\n'.format(
        classname=classname,
        dateini=self.finder.refmonthdate_ini,
        datefim=self.finder.refmonthdate_fim,
    )
    outstr += "total fundos = %d\n" % len(self.fundos)
    return outstr


def adhoctest():
  pass


def process():
  insertor = BBFIDataFilesToDBInsertor(bank3letter='bdb')
  insertor.process()
  print(insertor)


if __name__ == '__main__':
  process()
