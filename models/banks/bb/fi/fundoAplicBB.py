#!/usr/bin/env python3
""""
fundoAplicBB.py
  Contains class FundoAplicBB which is a specialization of parent class fAplic.FundoAplic
  Parent class is general, this one is polymorphic for bank 'bdb'.
  Remember that this polymorphism is due to the fact that banks publish different data files,
    that need different approaches to their scraping.
"""
import models.banks.fundoAplic as fAplic
import models.banks.banksgeneral as bkge
import models.banks.bb.fi.bbScraperWithFileText as bbScrp

# import fs.os.oshilofunctions as hilo
# finder (DatePrefixedOSEntriesFinder) comes from fs/db/dbasfolder/lookup_monthrange_convention_from_basedatafolder_on.py


def get_fundo_by_filepath_n_refmonthdate(filepath, refmonthdate):
  scrapetext = open(filepath, encoding='latin1').read()
  fundo = bbScrp.BBExtractScraperWithFileText(scrapetext, refmonthdate)
  return fundo


class FundoAplicBB(fAplic.FundoAplic):

  BANK3LETTER = 'bdb'

  def __init__(self):
    self.finder = bkge.BANK.get_pathentries_finderobj_by_bank3letter(self.BANK3LETTER)
    # self.finder is an os-entries look-up class object, it finds folders, data files and daterange
    super().__init__()
    self.bank3letter = self.BANK3LETTER
    self.refmonthdate_ini = None
    self.refmonthdate_fim = None

  def transpose_fundo_here(self, fundo):
    pdict = self.outdict()
    for attr in pdict:
      value = eval('fundo.' + attr)
      pdict[attr] = value

  def scrape_by_refmonthdate(self, refmonthdate):
    filepath = self.finder.find_yearmonthfilepath_by_yearmonth(refmonthdate)
    if filepath is None:
      return False
    fundo = get_fundo_by_filepath_n_refmonthdate(filepath, refmonthdate)
    fundo.refmonthdate = refmonthdate
    if fundo.do_triple_rends_exist():
      self.transpose_fundo_here(fundo)


def adhoctest():
  bbfundo = FundoAplicBB()
  bbfundo.scrape_by_refmonthdate('2023-02-01')
  print('bbfundo', bbfundo)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
