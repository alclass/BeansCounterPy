#!/usr/bin/env python3
"""
adhoctests/pandasadhoc/pandas1renamecols.py
import prettytable
"""
import string
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)


def experiment_with_df_adding_columns_n_rows():
  """
  df = pd.DataFrame(arr, columns=columns)
  print(df)
  return df
  print('deleting columns C E I')
  df.drop(columns=['C', 'E', 'I'], inplace=True)
  """
  columns = list(string.ascii_uppercase)[:3]
  n_rows = 5
  arr = np.random.randint(1, 11, size=n_rows*len(columns), dtype=int)
  arr.shape = (n_rows, len(columns))
  print('arr =', arr)
  df = pd.DataFrame(arr, columns=columns)
  print('df = ')
  print(df.to_string())
  colsum = df.sum(axis=1)  # axis=1
  colavg = df.mean(axis=1)  # axis=1
  colmin = df.min(axis=1)  # axis=1
  colmax = df.max(axis=1)  # axis=1
  colstd = df.std(axis=1)  # axis=1
  colsum.name = 'sum'
  colavg.name = 'avg'
  colmin.name = 'min'
  colmax.name = 'max'
  colstd.name = 'std'
  df['sum'] = colsum
  df['min'] = colmin
  df['max'] = colmax
  df['avg'] = colavg
  df['std'] = colstd
  rowmax = df.max(axis=0)  # rowmax.index = Index(['A', 'B', 'C', 'sum', 'min', 'max', 'avg', 'std'], dtype='object')
  rowmax = rowmax.to_frame().T
  rowmin = df.min(axis=0)
  rowmin = rowmin.to_frame().T
  # df = pd.concat([df, rowmax.T], ignore_index=True, sort=False, axis=0)
  df = pd.concat([df, rowmax, rowmin], ignore_index=True)  # ignore_index=True continues df's seq-index
  print('Statistics:')
  print(df.to_string())


def create_df2():
  print('not yet pruning columns')
  print('lines')
  # lin = df.iloc[0]  # to_frame('row')
  lin = pd.Series([7, 3, 4], index=['A', 'B', 'C'])
  print(lin.to_frame().T)
  lin['sum'] = lin.sum()   # axis=1
  print(lin.to_frame().T)
  # lin['avg'] = lin.iloc[0:2].mean()  # axis=1
  lin['avg'] = lin.loc['A':'C'].mean()  # axis=1
  print(lin.to_frame().T)
  lin['min'] = lin.loc['A':'C'].min()  # axis=1
  print(lin.to_frame().T)
  lin['max'] = lin.loc['A':'C'].max()  # axis=1
  print(lin.to_frame().T)
  lin['std'] = lin.loc['A':'C'].std()  # axis=1
  print(lin.to_frame().T)


def process():
  experiment_with_df_adding_columns_n_rows()
  return


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
