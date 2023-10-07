#!/usr/bin/env python3
"""
The context to be solved here is to extract data from xml that has been converted original from pdf

  A refpage for XML parsing in Python
  https://www.geeksforgeeks.org/xml-parsing-python/
"""
import fs.os.discover_levels_for_datafolders as disc
import fs.datesetc.datefs as dtfs
import models.fundos.cef.extractCefDataFromXml as extrCef


class TripeRendLister:

  def __init__(self, refmonthdate_ini, refmonthdate_fim):
    self.abank = 'cef'
    self.refmonthdate_ini = refmonthdate_ini
    self.refmonthdate_fim = refmonthdate_fim
    self.discoverer = disc.FolderYearMonthLevelDiscovererForBankAndKind(self.abank)

  def fetch_month_triplerend(self, refmonth):
    year = refmonth.year
    yearfolderpath = self.discoverer.get_folderpath_by_year(year)
    extractor = extrCef.XMLDataExtractor(yearfolderpath)
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


def adhoctest():
  pass


def process():
  refmonthdate_ini = '2022-01-01'
  refmonthdate_fim = '2023-08-01'
  triple = TripeRendLister(refmonthdate_ini, refmonthdate_fim)
  triple.process()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
