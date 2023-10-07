#!/usr/bin/env python3
"""
The context to be solved here is to extract data from xml that has been converted original from pdf

  A refpage for XML parsing in Python
  https://www.geeksforgeeks.org/xml-parsing-python/
"""
# import copy
import os
import xml.etree.ElementTree as eT
import fs.os.discover_levels_for_datafolders as disc
# import fs.datesetc.datefs as dtfs
# import lxml
# from lxml import ElementInclude
import models.fundos.fundoAplic as fAplic


class XMLDataExtractor:

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
    self.fundos = []
    for i, xmlfilename in enumerate(self.xmlfilenames):
      seqfile = i + 1
      print(seqfile, 'extract_data for', xmlfilename)
      xmlfilepath = self.form_filepath_from_filename(xmlfilename)
      xmltree = eT.parse(xmlfilepath)
      xmlroot = xmltree.getroot()
      seq1 = 0
      fundo = fAplic.FundoAplic()  # instantiate an empty FunooAplic obj
      for item in xmlroot.findall('./LTPage/LTTextBoxHorizontal/LTTextLineHorizontal'):
        seq1 += 1
        if seq1 == 8:
          fundo.name = item.text
        elif seq1 == 10:
          fundo.rend_no_mes = item.text
        elif seq1 == 12:
          fundo.rend_no_ano = item.text
        elif seq1 == 14:
          fundo.rend_ults_12meses = item.text
        elif seq1 == 16:
          fundo.data_ini_cota = item.text
        elif seq1 == 18:
          fundo.data_fim_cota = item.text
        elif seq1 == 24:
          fundo.cnpj = item.text
        elif seq1 == 45:
          fundo.qtd_cotas = item.text
      seq2 = 0
      for item in xmlroot.findall('./LTPage/LTTextLineHorizontal/LTTextBoxHorizontal'):
        seq2 += 1
        if seq2 == 28:
          fundo.saldo_anterior = item.text
        elif seq2 == 29:
          fundo.rendimento_bruto = item.text
        elif seq2 == 30:
          fundo.saldo_atual = item.text
        elif seq2 == 31:
          fundo.resg_bru_em_trans = item.text
        elif seq2 == 32:
          fundo.qtd_cotas_anterior = item.text
        elif seq2 == 37:
          fundo.rendimento_base = item.text
        elif seq2 == 39:
          fundo.ir = item.text
        print(seq2, 'seq2', item, 'text', item.text)
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
    for fn in self.xmlfilenames:
      outstr += '\t' + fn + '\n'
    outstr += str(self.outdict())
    return outstr


def adhoctest():
  pass


def process():
  abank = 'cef'
  discoverer = disc.FolderYearMonthLevelDiscovererForBankAndKind(bank3letter=abank)
  yearmonthfolderpath = discoverer.get_folderpath_by_year(2023)
  extractor = XMLDataExtractor(yearmonthfolderpath)
  extractor.process()
  print(extractor)


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
