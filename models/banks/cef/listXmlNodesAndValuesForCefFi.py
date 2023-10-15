#!/usr/bin/env python3
"""
"""
# import copy
import os
import xml.etree.ElementTree as eT
import models.banks.fundoAplic as fAplic
import models.banks.banksgeneral as bkge
CEF_BANK3LETTER = bkge.BANK.BANK3LETTER_CEF


def parse_xml_file(xmlfilepath):
  """

  """
  xmlfilename = os.path.split(xmlfilepath)[-1]
  print('extract_data for', xmlfilename)
  xmltree = eT.parse(xmlfilepath)
  xmlroot = xmltree.getroot()
  seq1 = 0
  fundo = fAplic.FundoAplic()  # instantiate an empty FunooAplic obj
  fundo.bank3letter = CEF_BANK3LETTER  # instantiate an empty FunooAplic obj
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


def adhoctest():
  pass


def process():
  pass


if __name__ == '__main__':
  """
  adhoctest()
  process()
  """
  pass
