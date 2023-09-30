#!/usr/bin/env python3
""""


"""
import fs.texts.texts_scrapehelper as scrapehelper
import settings as sett
import models.extractFromWithinAFundoReport as extScr


def get_scrapetest(year, month, fundoname):
  fundofilepath = sett.get_bb_fi_extract_filepath_by_year_month(year, month)
  scrapetexts = scrapehelper.slice_fundofile_into_fundoscrapetexts(fundofilepath)
  for scrapetext in scrapetexts:
    if scrapetext.find(fundoname) > -1:
      return scrapetext
  return None


def process_test():
  year = 2023
  month = 4
  # refmonth = '2023-04'
  fundoname = 'RF LP Estrat Ativa'
  scrapetext = get_scrapetest(year, month, fundoname)
  fundoresults = extScr.WithinFundoExtractScraper(scrapetext)
  fundoresults.process()
  datadict = fundoresults.datadict
  print(fundoresults)


if __name__ == '__main__':
  process_test()
