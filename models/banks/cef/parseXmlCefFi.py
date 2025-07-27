#!/usr/bin/env python3
"""
The context to be solved here is to extract data from xml that has been converted original from pdf

  A refpage for XML parsing in Python
  https://www.geeksforgeeks.org/xml-parsing-python/

What is the difference between PyMuPDF and PDFtoText?
  1 PyMuPDF — Extracts text from PDF files, removes unnecessary spaces from the text,
    maintains the original structure of the document.
  2 PDFminer — Preserves the structure of PDF file text but not the table structure.
  3 PDFtoText — Comparatively most preferred as it preserves table and original structure.
PyMuPDF, PDFminer, PDFtoText
"""
# import copy
import os
import lib.db.dbasfolder.lookup_monthrange_convention_from_basedatafolder_on as fndr
import lib.os.osfunctions as osfs
import models.banks.banksgeneral as bkge
import models.banks.cef.listXmlNodesAndValuesForCefFi as prsXml  # prsXml.parse_xml_file
# import models.banks.fundoAplic as fAplic
CEF_BANK3LETTER = bkge.BANK.BANK3LETTER_CEF


class CefFiXMLDataFileExtractor:
  """
  Measuring line positions

observed: 2023-08 Especial RF LP 94528,97 Extrato Mensal CEF.xml
----------------------------------
8 text CAIXA FIC EXPERTISE RF CREDITO PRIV  # Fundo
10 seq1 1,2242 # No Mês(%)
12 seq1 8,6302 # No Ano(%)
14 seq1 13,3508 # Nos Últimos 12 Meses(%)
16 seq1 7,492091 # Cota em: 31/07/2023
18 seq1 7,583812 # Cota em: 31/08/2023
24 seq1 00.360.305/0001-04 # CNPJ da Administradora
45 seq1 12.464,572458 Qtde de Cotas
----------------------------------
28 seq2 93.385,71C saldo anterior
29 seq2  1.143,26C Rendimento Bruto no Mês
30 seq2 saldo bruto 94.528,97C
31 seq2 0,00  # resgate bruto em trânsito
32 seq2 12.464,572458  cotas ini
37 seq2 text 0,00 # Rendimento Base
39 seq2 text 0,00 # IRRF
  """

  CEF_BANK3LETTER = bkge.BANK.BANK3LETTER_CEF

  def __init__(self, xmlfilepath=None):
    self.fundo = None
    self.xmlfilepath = xmlfilepath
    self.treat_filepath()

  @property
  def xmlfilename(self):
    if self.xmlfilepath is None:
      return None
    try:
      filename = os.path.split(self.xmlfilepath)[-1]
      return filename
    except (IndexError, TypeError):
      pass
    return None

  def treat_filepath(self):
    if self.xmlfilepath is None or not os.path.isfile(self.xmlfilepath):
      error_msg = 'Error: filepath  does not exist.\n'
      error_msg += '\t Filename = [%s].' % self.xmlfilename
      error_msg += '\t Filepath = [%s].' % self.xmlfilepath
      raise OSError(error_msg)

  def parse_xmlfile(self):
    """
    prsXml.parse_xml_file
    """
    prsXml.parse_xml_file(self.xmlfilepath)

  def outdict(self):
    _outdict = {
      'filepath': self.xmlfilepath,
      'fundo': self.fundo,
    }
    return _outdict

  def __str__(self):
    outstr = "<obj XMLDataExtractor filename=%s>\n" % self.xmlfilename
    outstr += str(self.fundo)
    outstr += '================\n'
    return outstr


class XMLFolder:

  def __init__(self, folderpath=None):
    self.fundo = None
    self.folderpath = folderpath
    self.xmlfilenames = []
    self.treat_folderpath()

  def treat_folderpath(self):
    if self.folderpath is None or not os.path.isdir(self.folderpath):
      error_msg = 'Error: filepath does not exist [%s].' % self.folderpath
      raise OSError(error_msg)

  def load_xmlfiles_from_folder(self):
     filenames = os.listdir(self.folderpath)
     filenames = osfs.find_filenames_from_path(filenames)
     self.xmlfilenames = sorted(filter(lambda f: f.endswith('.xml'), filenames))

  @property
  def total_files(self):
    return len(self.xmlfilenames)

  def form_filepath_from_filename(self, filename):
    return os.path.join(self.folderpath, filename)


def parse_all_xmlfiles(refmonthini, refmonthfim):
  basedirpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(CEF_BANK3LETTER)
  finder = fndr.DatePrefixedOSEntriesFinder(rootdirpath=basedirpath)
  for i, xmlfilepath in enumerate(
      finder.gen_filepaths_within_daterange_or_wholeinterval(
        refmonthini,
        refmonthfim,
        dot_ext='xml'
      )
  ):
    if i == 5:
      break
    print('='*40)
    extractor = CefFiXMLDataFileExtractor(xmlfilepath)
    print(i + 1, 'Extracting xmlfilename', extractor.xmlfilename)
    print('\trefmonthini', refmonthini, 'refmonthfim', refmonthfim)
    print('\txmlfilepath', xmlfilepath)
    extractor.parse_xmlfile()


def adhoctest():
  """
  # yearmonthfolderpath = finder.find_yearprefix_folderpath_by_year(year)
  # xmlfilepaths = finder.gen_filepaths_within_daterange_or_wholeinterval()
  """
  basedirpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(CEF_BANK3LETTER)
  finder = fndr.DatePrefixedOSEntriesFinder(rootdirpath=basedirpath)
  seq = 0
  for xmlfilepath in finder.gen_filepaths_within_daterange_or_wholeinterval(dot_ext='xml'):
    seq += 1
    if seq == 3:
      break
    filename = os.path.split(xmlfilepath)[-1]
    print(seq, filename, 'xmlfilepath', xmlfilepath)
    print('=' * 40)


def process():
  refmonthini = '2023-06'
  refmonthfim = None
  parse_all_xmlfiles(refmonthini, refmonthfim)


if __name__ == '__main__':
  """
  adhoctest()
  pass
  """
  process()
