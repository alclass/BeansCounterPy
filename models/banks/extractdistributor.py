#!/usr/bin/env python3
"""
extractdistributor.py
  Chooses function/method for calling depending upon which bank function/method calling it related.
This is because report extracts are not standardized, each one has its own.
"""
import models.banks.banksgeneral as bkgen  # contains BANK which is mostly a static/classmethod class
import models.banks.cef.extractCefDataFromXml as extrCef
# extractor = extrCef.XMLDataExtractor(yearfolderpath)


def find_methodcall_on_bank3letter(bank3letter):
  """
  For CEF/cef:
    extractor = extrCef.XMLDataExtractor(yearfolderpath)
  For BB/bdb:

  """
  extract_method_handler = None
  if bank3letter == bkgen.BANK.BANK3LETTER_BDB:
    pass
  elif bank3letter == bkgen.BANK.BANK3LETTER_CEF:
    extract_method_handler = extrCef.XMLDataExtractor
  return extract_method_handler


def adhoctest():
  bank3letter = 'cef'
  folderpath = bkgen.BANK.get_bank_fi_folderpath_by_its3letter(bank3letter)
  finder = bkgen.BANK.get_pathentries_finderobj_by_bank3letter(bank3letter)
  classhandler = find_methodcall_on_bank3letter(bank3letter)
  mostrecentyearmonthfolderpath = finder.greater_yearmonthprefix_folderpath()
  extractor = classhandler(mostrecentyearmonthfolderpath)
  print(extractor.fundos)


def process():
  pass


if __name__ == '__main__':
  """
  """
  adhoctest()
