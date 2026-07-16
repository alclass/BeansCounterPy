#!/usr/bin/env python3
"""
models/models/bank_data_settings.py
  has config data for models and its files and folders places (localizations)
"""


class BankProps:
  """
  keys for BANKBASEFOLDERPATHS
    ac => account balance etc
    fi => fundos etc
    regex => fi rendimentos reports
  """
  SQL_TABLENAME = 'bankmonthlyfundos'
  BANK3LETTER_BDB = 'bdb'
  BANK3LETTER_CEF = 'cef'
  BANKDICT = {
    1: ('bdb', 'Banco do Brasil S.A.'),
    33: ('std', 'Banco Santander (Brasil) S.A.'),
    104: ('cef', 'Caixa Econômica Federal'),
    237: ('bra', 'Banco Bradesco S.A.'),
    341: ('ita', 'Banco Itaú S.A.'),
  }
  BANKBASEFOLDERPATHS = {
    1: {
      'ac':
      '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
      '001 BDB bankdata/CC Extratos Mensais Ano a Ano BB/',
      'fi':
      '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
      '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD',
      'regex':
      '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
      '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/'
      'BB FI Rendimentos Diários htmls',
    },
    33: {
      'ac': None,
      'fi': None,
      'regex': None,
    },
    104: {
      'ac': None,
      'fi': None,
      'regex': None,
    },
    237: {
      'ac': None,
      'fi': None,
      'regex': None,
    },
    341: {
      'ac': None,
      'fi': None,
      'regex': None,
    },
  }


def adhoctest():
  print("BankProps.BANKBASEFOLDERPATHS[1]['regex']")
  print(BankProps.BANKBASEFOLDERPATHS[1]['regex'])


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
