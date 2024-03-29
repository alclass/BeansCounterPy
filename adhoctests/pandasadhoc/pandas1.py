#!/usr/bin/env python3
"""
adhoctests/pandasadhoc/pandas1.py
"""
import pandas as pd



def adhoctest():
  """
  pdict = {
    'id': 1, 'value': 1.0,
  }
  df = pd.DataFrame(pdict)
  """
  df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
  print(df)
  d2 = df.rename(columns={'A': 'e', 'B': 'f', })
  print(d2)
  print('column f name is', d2['f'].name)
  print('loc 1', d2.index)
  for line in d2:
    print(line)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
