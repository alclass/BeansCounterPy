#!/usr/bin/env python3
""""
latin1_workaround.py
  Trying to find out a work around to the "mês" word inside a latin1 text file,
    considering a string in Python is always a UTF-8 one.

Obs:
  # this script depends on the dados folder which is not added to the code's git repo


This simple module helped show that "mÃªs" is the way mês[latin1-in-file] is printed as a UTF-8 Python string
"""
import os
import settings as sett
DEFAULT_DATADIR = ("/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/FI Extratos Mensais Ano a Ano BB OD/2023 FI "
                   "Extratos Mensais BB")
EXAMPLE_FILENAME = 'fundo_report_example.txt'
datafolder_abspath = sett.get_bb_fi_extracts_datafolder_abspath_by_year(year=2023)
test_filepath = os.path.join(datafolder_abspath, EXAMPLE_FILENAME)


def printout():
  fd = open(test_filepath, encoding='latin1')
  text = fd.read()
  print(text)


if __name__ == '__main__':
  printout()  # the purpose is to recuperate (copy) how "mês", being read from a latin1 text file, come about
