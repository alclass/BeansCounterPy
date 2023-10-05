#!/usr/bin/env python3
"""
discover_bbfi_datadirections.py
  envolopes module lookup_monthrange_in_datafolder.py giving it BBFI's basefolder
"""
import os
import pdfquery
import settings as sett


class PDFScraper:

  def __init__(self, datadir_abspath=None):
    self.datadir_abspath = sett.get_cef_fi_rootfolder_abspath()
    filenames = os.listdir(self.datadir_abspath)
    self.pdffilenames = list(filter(lambda f: f.endswith('.pdf'), filenames))

  @property
  def total_pdffiles(self):
    return len(self.pdffilenames)

  def transform_pdffiles_into_xml(self):
    for pdffilename in self.pdffilenames:
      filepath = os.path.join(self.datadir_abspath, pdffilename)
      print('Creating pdf for', pdffilename)
      pdf = pdfquery.PDFQuery(filepath)
      pdf.load()
      # convert the pdf to XML
      xmlfilename = os.path.splitext(pdffilename)[0] + '.xml'
      xmlfile = os.path.join(self.datadir_abspath, xmlfilename)
      print('Writing xml', xmlfilename)
      pdf.tree.write(xmlfile, pretty_print=True)

  def process(self):
    self.transform_pdffiles_into_xml()

  def outdict(self):
    _outdict = {
      'datadir_abspath': self.datadir_abspath,
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
  scraper = PDFScraper()
  scraper.process()
  print(scraper)


if __name__ == '__main__':
  """
  """
  process()
