#!/usr/bin/env python3
"""
models/banks/bankpropsmod.py
"""


class BankProps:

  ACCOUNT_KEY = 'ac'
  FI_FUNDOS_KEY = 'fi'
  REND_RESULTS_KEY = 're'
  TYPECATS = [ACCOUNT_KEY, FI_FUNDOS_KEY, REND_RESULTS_KEY]
  FILESUFFIXDICT = {
    REND_RESULTS_KEY: 'BB rendimentos no dia',
    FI_FUNDOS_KEY: 'FI extrato BB',
    ACCOUNT_KEY: 'CC extrato BB',
  }
  FOLDERSUFFIXDICT = {
    REND_RESULTS_KEY: 'BB FI Ren Diá htmls',
    FI_FUNDOS_KEY: 'FI Extratos Mensais BB',
    ACCOUNT_KEY: 'CC Extratos Mensais BB',
  }
  ACOES = 'Ações'
  RFDI = 'RFDI'
  RFLP = 'RFLP'
  SUBTYPERES = [ACOES, RFDI, RFLP]


def adhoctest():
  pass


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
