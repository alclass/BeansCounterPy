#!/usr/bin/env python3
""""
"""
import os.path

# datadir = '/home/grayacer/OurDocs/Banks OD/Banco do Brasil BB OD/Investimentos (Fundos etc) BB OD/Fundos de Investimentos BB OD/FI Extratos Mensais Ano a Ano BB OD/2023 FI Extratos Mensais BB'
DEFAULT_DATADIR = '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/FI Extratos Mensais Ano a Ano BB OD/2023 FI Extratos Mensais BB'
DEFAULT_FILENAME = '2023-04 FI extrato BB.txt'


class BBFundoExtractScraper:

  def __init__(self, datadir=None, txtfilename=None):
    self.datadir = None
    self.txtfilename = None
    self.txtfile = None
    self.txttrunks = []
    self.lines = []
    self.adjust_dir_n_file(datadir, txtfilename)

  def adjust_dir_n_file(self, datadir=None, txtfilename=None):
    self.datadir = datadir or DEFAULT_DATADIR
    self.txtfilename = txtfilename or DEFAULT_FILENAME
    if not os.path.isdir(self.datadir):
      error_msg = 'Directory [%s] does not exist.' % self.datadir
      raise OSError(error_msg)
    self.txtfile = os.path.join(self.datadir, self.txtfilename)
    if not os.path.isfile(self.txtfile):
      error_msg = 'File [%s] does not exist.' % self.txtfile
      raise OSError(error_msg)

  def readon_til_next_dashedline(self):
    txttrunk = ''
    past_the_second_dashedline = False
    while len(self.lines) > 0:
      line = self.lines.pop()
      if past_the_second_dashedline:
        return txttrunk
      if line.startswith('============='):
        past_the_second_dashedline = True
        continue
      txttrunk += line + '\n'
    return txttrunk

  def txtfile_to_linelist(self):
    text = open(self.txtfile, encoding='latin1').read()
    self.lines = text.split('\n')
    self.lines.reverse()
    pass

  def process(self):
    self.txtfile_to_linelist()
    self.txttrunks = []
    while 1:
      if len(self.lines) == 0:
        break
      line = self.lines.pop()
      if line.startswith('============='):
        txttrunk = self.readon_til_next_dashedline()
        self.txttrunks.append(txttrunk)

  def __str__(self):
    outstr = 'Number of fundos = ' + str(len(self.txttrunks))
    return outstr



if __name__ == '__main__':
  fundo_extractor = BBFundoExtractScraper()
  fundo_extractor.process()
  print(fundo_extractor)