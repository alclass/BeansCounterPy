#!/usr/bin/env python3
""""
scraper_monthly_rendextracts.py
  Organizes the month range and then calls extractFromWithinAFundoReport.py month to month
"""
import datetime
from dateutil.relativedelta import relativedelta
import settings as sett
from models.extractFromWithinAFundoReport import WithinFundoExtractScraper
import fs.texts.texts_scrapehelper as scrapehelper
YEARMONTH_INI = datetime.date(year=2022, month=8, day=1)
YEARMONTH_FIM = datetime.date(year=2023, month=8, day=1)


class MonthlyRoller:

  def __init__(self, yearmonth_ini=None, yearmonth_fim=None):
    self.yearmonth_ini = yearmonth_ini
    self.yearmonth_fim = yearmonth_fim
    self.treat_param_dates()

  def treat_param_dates(self):
    if self.yearmonth_ini is None or not type(self.yearmonth_ini) == datetime.date:
      self.yearmonth_ini = YEARMONTH_INI
    if self.yearmonth_fim is None or not type(self.yearmonth_fim) == datetime.date:
      self.yearmonth_fim = YEARMONTH_FIM

  def roll_months(self):
    current_yearmonth = self.yearmonth_ini
    while current_yearmonth <= self.yearmonth_fim:
      print('='*40)
      fundofilepath = sett.get_bb_fi_extract_filepath_by_year_month(current_yearmonth.year, current_yearmonth.month)
      scrapetexts = scrapehelper.slice_fundofile_into_fundoscrapetexts(fundofilepath)
      for scrapetext in scrapetexts:
        scraper = WithinFundoExtractScraper(scrapetext, refmonthdate=current_yearmonth)
        scraper.process()
        str_curr_yearmonth = '{year}-{month:02d}'.format(
          year=current_yearmonth.year, month=current_yearmonth.month
        )
        print(str_curr_yearmonth)
        print('='*40)
        print(scraper)
        current_yearmonth = current_yearmonth + relativedelta(months=1)

  def process(self):
    self.roll_months()

  def __str__(self):
    dateini = self.yearmonth_ini
    datefim = self.yearmonth_fim
    outstr = "<MonthlyRoller dateini={dateini} datefim={datefim}>".format(dateini=dateini, datefim=datefim)
    return outstr


if __name__ == '__main__':
  roller = MonthlyRoller()
  roller.process()
