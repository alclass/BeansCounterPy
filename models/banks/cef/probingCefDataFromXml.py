#!/usr/bin/env python3
"""
The context to be solved here is to extract data from xml that has been converted original from pdf

  A refpage for XML parsing in Python
  https://www.geeksforgeeks.org/xml-parsing-python/
"""
# import copy
import os
import xml.etree.ElementTree as eT
import fs.db.dbasfolder.discover_levels_for_datafolders as disc
# import fs.datesetc.datefs as dtfs
# import lxml
# from lxml import ElementInclude
import models.banks.fundoAplic as fAplic


class XMLDataExtractor:
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

  CEF_BANK3LETTER = 'cef'

  def __init__(self, folderpath=None):
    if folderpath is None or not os.path.isdir(folderpath):
      error_msg = 'Error: folderpath %s does not exist.'
      raise OSError(error_msg)
    self.folderpath = folderpath
    self.xmlfilenames = []
    self.fundos = []
    self.init_xmlfilenames()

  def init_xmlfilenames(self):
    filenames = os.listdir(self.folderpath)
    self.xmlfilenames = sorted(filter(lambda f: f.endswith('.xml'), filenames))

  @property
  def total_files(self):
    return len(self.xmlfilenames)

  def form_filepath_from_filename(self, filename):
    return os.path.join(self.folderpath, filename)

  def extract_data(self):
    """

    """
    self.fundos = []
    for i, xmlfilename in enumerate(self.xmlfilenames):
      seqfile = i + 1
      print(seqfile, 'extract_data for', xmlfilename)
      xmlfilepath = self.form_filepath_from_filename(xmlfilename)
      xmltree = eT.parse(xmlfilepath)
      xmlroot = xmltree.getroot()
      seq1 = 0
      fundo = fAplic.FundoAplic()  # instantiate an empty FunooAplic obj
      fundo.bank3letter = self.CEF_BANK3LETTER  # instantiate an empty FunooAplic obj
      for item in xmlroot.findall('./LTPage/LTTextBoxHorizontal/LTTextLineHorizontal'):
        # check level 0_LTTextBoxHorizontal

        seq1 += 1
        print(seq1, item)
        print(item.text)
      seq2 = 0
      for item in xmlroot.findall('./LTPage/LTTextLineHorizontal/LTTextBoxHorizontal'):
        # check level 0_LTTextBoxHorizontal
        seq2 += 1
        print(seq2, item)
        print(item.text)
      if seq1 == 0 and seq2 == 0:
        print('\tnothing found for both seq1 & seq2')
      self.fundos.append(fundo)

  def process(self):
    self.extract_data()

  def outdict(self):
    _outdict = {
      'datadir_abspath': self.folderpath,
      'total_xmlfiles': self.total_files,
      'total_fundos': len(self.fundos),
    }
    return _outdict

  def __str__(self):
    outstr = "<obj XMLDataExtractor total_xmlfiles=%d>\n" % self.total_files
    for i, fn in enumerate(self.xmlfilenames):
      outstr += '\t' + fn + '\n'
      outstr += str(self.fundos[i])
    outstr += '================\n'
    pdict = self.outdict()
    for p in pdict:
      outstr += '{item} = {value}\n'.format(item=p, value=pdict[p])
    return outstr


def adhoctest():
  pass


def process():
  abank = 'cef'
  discoverer = disc.FolderYearMonthLevelDiscovererForBankAndKind(bank3letter=abank)
  yearmonthfolderpath = discoverer.get_folderpath_by_year(2023)
  extractor = XMLDataExtractor(yearmonthfolderpath)
  extractor.process()
  print('extractor')
  print(extractor)


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
