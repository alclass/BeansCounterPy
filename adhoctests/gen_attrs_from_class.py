#!/usr/bin/env python3
""""
scraper_monthly_rendextracts.py
  Organizes the month range and then calls extractFromWithinAFundoReport.py month to month
"""
import models.fundos.extractFromWithinAFundoReport as fundoReport


def get_attrs_as_dict():
  pdict = vars(fundoReport.WithinFundoExtractScraper())
  for elem in pdict:
    print(elem, '||||||||', pdict[elem])
  # print(fundoreport.WithinFundoExtractScraper.__dict__)


def get_attrs_as_list():
  attrs = fundoReport.WithinFundoExtractScraper.attrs()
  for attr in attrs:
    print(attr)
  print(len(attrs), 'attributes')


if __name__ == '__main__':
  # get_attrs_as_dict()
  get_attrs_as_list()
