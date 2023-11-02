#!/usr/bin/env python3
"""
models/banks/bank_data_settings.py
  has config data for banks and its files and folders places (localizations)
"""


class BankProps:
  """
  keys for BANKBASEFOLDERPATHS
    ac => account balance etc
    fi => fundos etc
    re => fi rendimentos reports
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
      're':
      '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
      '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/'
      'BB FI Rendimentos Diários htmls',
    },
    33: {
      'ac': None,
      'fi': None,
      're': None,
    },
    104: {
      'ac': None,
      'fi': None,
      're': None,
    },
    237: {
      'ac': None,
      'fi': None,
      're': None,
    },
    341: {
      'ac': None,
      'fi': None,
      're': None,
    },
  }


def adhoctest():
  print("BankProps.BANKBASEFOLDERPATHS[1]['re']")
  print(BankProps.BANKBASEFOLDERPATHS[1]['re'])


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
