#!/usr/bin/env python3
"""
extractdistributor.py
  Chooses function/method for calling depending upon which bank function/method calling it related.
This is because report extracts are not standardized, each one has its own. Consider this an experimental sketch.

TO-DO: it is needed for system to have an interface-like approach that is assymetric by now.
  Strategy to-try:
  1 the 'mounting' process, so to say, should be the following:
  1-1  choose bank (by bank3letter)
  1-2  choose refmonth range

Because data finding from textfiles is different by bank, a method with the same name (conventioned)
  might be called dynamically (ie, either by eval() or by a handler() (ie, handler followed by ())

Initial sketch: it's in commands.show.to_corretc_list_triple_rends_from_db.py
"""
import models.banks.banksgeneral as bkgen  # contains BANK which is mostly a static/classmethod class
import models.banks.cef.extractCefFiDataFromXml as extrCef
import models.banks.bb.bbScraperWithFileText as extrBB
# extractor = extrCef.XMLDataExtractor(yearfolderpath)


def find_methodcall_on_bank3letter(bank3letter):
  """
  For CEF/cef:
    extractor = extrCef.XMLDataExtractor(yearfolderpath)
  For BB/bdb:

  """
  extract_method_handler = None
  if bank3letter == bkgen.BANK.BANK3LETTER_BDB:
    extract_method_handler = extrBB.SpecificBBExtract  # to instantiate with filepath that contains the scrapetext
  elif bank3letter == bkgen.BANK.BANK3LETTER_CEF:
    extract_method_handler = extrCef.CefFiXMLDataExtractor  # yearprefixed_folderpath
  return extract_method_handler


def distributor(bank3letter='cef', refmonthini=None, refmonthfim=None):
  # step 1 get bank's data rootdirpath
  folderpath = bkgen.BANK.get_bank_fi_folderpath_by_its3letter(bank3letter)
  # step 2 get a discoverer/finder object based bank's class handler (each bank has its own class, this )
  finder = bkgen.BANK.get_pathentries_finderobj_by_bank3letter(bank3letter)
  finder.__init__(folderpath)
  scraper_classhandler = find_methodcall_on_bank3letter(bank3letter)
  scraper_classhandler(finder.greater_yearprefix_folderpath)
  for folderpath in finder.gen_folderpaths_within_yearrange_or_wholeinterval(refmonthini, refmonthfim):
    extractor = scraper_classhandler(folderpath)
    print(folderpath)
    for i, fundo in enumerate(extractor.fundos):
      print(i+1, folderpath)
      print(fundo.name, 'mês', fundo.prct_rend_mes, 'ano', fundo.prct_rend_desdeano, '12m', fundo.prct_rend_12meses)


def process():
  distributor()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
