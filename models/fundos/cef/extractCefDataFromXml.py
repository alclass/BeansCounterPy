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
import fs.datesetc.datefs as dtfs
import models.fundos.fundoAplic as fAplic


class XMLDataExtractor:
  """

  """
  CREDRF = 'credrf'
  ESPECIAL = 'especial'
  LINENUMBERDICT_S1 = {  # LTTextLineHorizontal
    ESPECIAL: {
      4: 'name',
      10: 'prct_rend_mes',
      12: 'prct_rend_desdeano',
      14: 'prct_rend_12meses',
      15: 'data_saldo_ant',
      16: 'valor_cota_ant',
      17: 'data_saldo_atu',
      18: 'valor_cota_atu',
      24: 'cnpj',
      39: 'aplicacoes',
      40: 'resgates',
      41: 'ir',
      42: 'iof',  # 43: 'tx_de_saida',  # not in db
    },
    CREDRF: {
      8: 'name',
      10: 'prct_rend_mes',
      12: 'prct_rend_desdeano',
      14: 'prct_rend_12meses',
      15: 'data_saldo_ant',
      16: 'valor_cota_ant',
      17: 'data_saldo_atu',
      18: 'valor_cota_atu',
      24: 'cnpj',
      39: 'aplicacoes',
      40: 'resgates',
      41: 'ir',
      42: 'iof',  # 43: 'tx_de_saida',  # not in db
    }
  }
  LINENUMBERDICT_S2 = {  # LTTextBoxHorizontal
    ESPECIAL: {
      11: 'data_saldo_atu',
      28: 'saldo_anterior',
      29: 'rendimento_bruto',
      30: 'saldo_bruto',
      32: 'qtd_cotas_ant',
    },
    CREDRF: {
      11: 'data_saldo_atu',
      28: 'saldo_anterior',
      29: 'rendimento_bruto',
      30: 'saldo_bruto',
      32: 'qtd_cotas_ant',
    },
  }

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
      # seqfile = i + 1
      # print(seqfile, 'extract_data for', xmlfilename)
      fundoqual = self.CREDRF
      if xmlfilename.lower().find('especial') > -1:
        fundoqual = self.ESPECIAL
      xmlfilepath = self.form_filepath_from_filename(xmlfilename)
      xmltree = eT.parse(xmlfilepath)
      xmlroot = xmltree.getroot()
      seq1 = 0
      fundo = fAplic.FundoAplic()  # instantiate an empty FunooAplic obj
      fundo.refmonthdate = dtfs.make_refmonthdate_from_conventioned_filename(xmlfilename)  # may get None from here
      for item in xmlroot.findall('./LTPage/LTTextBoxHorizontal/LTTextLineHorizontal'):
        _ = item  # item will used in the eval() below; this line is for the IDE!
        seq1 += 1
        if seq1 in self.LINENUMBERDICT_S1[fundoqual]:
          exec('fundo.' + self.LINENUMBERDICT_S1[fundoqual][seq1] + ' = item.text')
      seq2 = 0
      for item in xmlroot.findall('./LTPage/LTTextLineHorizontal/LTTextBoxHorizontal'):
        _ = item  # item will used in the eval() below; this line is for the IDE!
        seq2 += 1
        if seq2 in self.LINENUMBERDICT_S2[fundoqual]:
          exec('fundo.' + self.LINENUMBERDICT_S2[fundoqual][seq2] + ' = item.text')
      # if seq1 == 0 and seq2 == 0:
        # print('\tnothing found for both seq1 & seq2')
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
  # print(extractor)


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
