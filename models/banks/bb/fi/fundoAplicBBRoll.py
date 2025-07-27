#!/usr/bin/env python3
""""

"""
import os.path

import models.banks.fundoAplic as fAplic
import models.banks.banksgeneral as bkge
import models.banks.bb.fi.bbScraperWithFileText as bbScrp
import lib.os.oshilofunctions as hilo
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

  def scrape_by_refmonthdate_range(self, refmonthdate_ini=None, refmonthdate_fim=None):
    for filepath in self.finder.gen_filepaths_within_daterange_or_wholeinterval(refmonthdate_ini, refmonthdate_fim):
      # recup filename from filepath
      _, filename = os.path.splitext(filepath)
      # recup refmonthdate from filename
      refmonthdate = hilo.derive_refmonthdate_from_a_yearmonthprefixedstr(filename)
      fundo = get_fundo_by_filepath_n_refmonthdate(filepath, refmonthdate)
      if fundo.do_triple_rends_exist():
        self.transpose_fundo_here(fundo)


def adhoctest():
  bbfundo = FundoAplicBB()
  bbfundo.scrape_by_refmonthdate()


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
