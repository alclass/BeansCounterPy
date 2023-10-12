#!/usr/bin/env python3
""""
scrape_monthly_rendextracts.py
  Organizes the month range and then calls bbScraperWithFileText.py month to month
"""
import datetime
from dateutil.relativedelta import relativedelta
import fs.db.dbasfolder.lookup_monthrange_convention_from_basedatafolder_on as finder
import models.banks.banksgeneral as bkge
# from models.extractFromWithinAFundoReport import WithinFundoExtractScraper
import models.banks.bb.bbScraperWithFileText as extScr
import fs.texts.texts_scrapehelper as scrapehelper
# import settings

YEARMONTH_INI = datetime.date(year=2022, month=8, day=1)
YEARMONTH_FIM = datetime.date(year=2023, month=8, day=1)


class MonthlyRoller:

  def __init__(self, yearmonth_ini=None, yearmonth_fim=None, bank3letter=None, financkind=None):
    self.bank3letter = bank3letter
    if self.bank3letter is None or not bkge.BANK.does_bank3letter_exist(bank3letter):
      error_msg = 'Error: bank3letter [%s] does not exist.' % self.bank3letter
      raise ValueError(error_msg)
    self.financkind = financkind
    bankfibasefolderpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(self.bank3letter)
    self.pathfinder = finder.DatePrefixedOSEntriesFinder(
      rootdirpath=bankfibasefolderpath,
    )
    self.fundo_result_records = []
    self.yearmonth_ini = yearmonth_ini
    self.yearmonth_fim = yearmonth_fim
    self.treat_param_dates()

  def treat_param_dates(self):
    if self.yearmonth_ini is None or not type(self.yearmonth_ini) == datetime.date:
      self.yearmonth_ini = YEARMONTH_INI
    if self.yearmonth_fim is None or not type(self.yearmonth_fim) == datetime.date:
      self.yearmonth_fim = YEARMONTH_FIM

  def scrape_sliced_fundos_for_refmonth(self, current_yearmonth):
    fundofilepath = self.pathfinder.find_yearmonthfilepath_by_yearmonth(current_yearmonth)
    try:
      scrapetexts = scrapehelper.slice_fundofile_into_fundoscrapetexts(fundofilepath)
    except FileNotFoundError:
      return
    for scrapetext in scrapetexts:
      fundoresult = extScr.SpecificCEFExtractScraper(scrapetext, refmonthdate=current_yearmonth)
      fundoresult.process()
      # str_curr_yearmonth = '{year}-{month:02d}'.format(
      #  year=current_yearmonth.year, month=current_yearmonth.month
      # )
      # print(str_curr_yearmonth)
      # print('=' * 40)
      # print(fundoresult)
      self.fundo_result_records.append(fundoresult.datadict)

  def roll_months(self):
    current_yearmonth = self.yearmonth_ini
    while current_yearmonth <= self.yearmonth_fim:
      # print('-*-=-*-'*10)
      self.scrape_sliced_fundos_for_refmonth(current_yearmonth)
      current_yearmonth = current_yearmonth + relativedelta(months=1)

  def process(self):
    self.roll_months()

  def __str__(self):
    dateini = self.yearmonth_ini
    datefim = self.yearmonth_fim
    outstr = "<MonthlyRoller dateini={dateini} datefim={datefim}>".format(dateini=dateini, datefim=datefim)
    return outstr


if __name__ == '__main__':
  roller = MonthlyRoller(bank3letter='bdb')
  roller.process()
