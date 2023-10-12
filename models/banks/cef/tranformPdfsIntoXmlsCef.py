#!/usr/bin/env python3
"""
bankFoldersDiscover.py
  envolopes module lookup_monthrange_convention_from_basedatafolder_on.py giving it BBFI's basefolder
"""
import os
import pdfquery
import fs.db.dbasfolder.discover_levels_for_datafolders as disc


class PDFScraper:

  def __init__(self, folderpath=None):
    if folderpath is None or not os.path.isdir(folderpath):
      error_msg = 'Error: folderpath %s does not exist.'
      raise OSError(error_msg)
    self.folderpath = folderpath
    filenames = os.listdir(self.folderpath)
    self.pdffilenames = list(filter(lambda f: f.endswith('.pdf'), filenames))

  @property
  def total_pdffiles(self):
    return len(self.pdffilenames)

  def transform_pdffiles_into_xml(self):
    for i, pdffilename in enumerate(self.pdffilenames):
      seq = i + 1
      print(seq, 'Processing pdf for', pdffilename)
      filepath = os.path.join(self.folderpath, pdffilename)
      xmlfilename = os.path.splitext(pdffilename)[0] + '.xml'
      xmlfilepath = os.path.join(self.folderpath, xmlfilename)
      if os.path.isfile(xmlfilepath):
        print('File already exists [%s].' % xmlfilepath)
        continue
      print('Instantiating pdf for', pdffilename)
      pdf = pdfquery.PDFQuery(filepath)
      pdf.load()
      # convert the pdf to XML
      print('Writing xml', xmlfilename)
      pdf.tree.write(xmlfilepath, pretty_print=True)

  def process(self):
    self.transform_pdffiles_into_xml()

  def outdict(self):
    _outdict = {
      'datadir_abspath': self.folderpath,
      'total_pdffiles': self.total_pdffiles,
    }
    return _outdict

  def __str__(self):
    outstr = """
    datadir_abspath = {datadir_abspath}
    n of pdf files = {total_pdffiles}
    """.format(**self.outdict())
    return outstr


def process():
  abank = 'cef'
  discoverer = disc.FolderYearMonthLevelDiscovererForBankAndKind(bank3letter=abank)
  yearmonthfolderpath = discoverer.get_folderpath_by_year(2023)
  scraper = PDFScraper(yearmonthfolderpath)
  scraper.process()
  print(scraper)


if __name__ == '__main__':
  """
  """
  process()
