#!/usr/bin/env python3
"""
adhoctests/pandasadhoc/pandas1renamecols.py
import prettytable
"""
import math
import string
import numpy as np
import pandas as pd
import statistics as st
pd.set_option('display.max_columns', None)


def show_std():
  data = [6, 5, 9]
  expected = 2.081666
  std = st.stdev(data)
  avg = st.mean(data)
  items = [(n - avg) ** 2 for n in data]
  s = sum(items)
  sdcalc = math.sqrt(s/(len(data)-1))
  print(data, 'st.stdev => ', std, 'expected', expected, 'avg', avg, 'sdcalc', sdcalc)
  data = [4, 2, 6]
  expected = 2
  std = st.stdev(data)
  avg = st.mean(data)
  items = [(n - avg) ** 2 for n in data]
  s = sum(items)
  sdcalc = math.sqrt(s/(len(data)-1))
  print(data, 'st.stdev => ', std, 'expected', expected, 'avg', avg, 'sdcalc', sdcalc)


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
  # 3 forms of deleting a column:
  # 1 del[] in-place
  # 2 pop() in-place and getting the deleted Series|DF
  # 3 drop() generates another df without the "deleted" (it's more of a copying without the "deleted")
  del lin['avg']
  print(lin.to_frame().T)
  popped = lin.pop('sum')
  print('popped', popped)
  print(lin.to_frame().T)
  dropped = lin.drop(index=['min', 'max'])
  print('dropped:')
  print(dropped.to_frame().T)
  print(lin.to_frame().T)


def drop_adhoctest():
  arr = np.array([
    [2, 2, 9, 3],
    [8, 1, 2, 3],
    [1, 10, 1, 3],
  ],)
  print(arr)
  df = pd.DataFrame(arr, columns=list('ABCD'))
  print(df)
  sh = df.shape[-1]
  print('shape', sh)
  # df = df.rename(columns={'A': 0, 'B': 1, 'C': 2, 'D': 3})
  df.columns = list(range(sh))
  # df = df.drop(columns=['B', 'C'])
  print(df)
  df = df.drop([2, 3], axis=1)
  print(df)


def process():
  """
  experiment_with_df_adding_columns_n_rows()
  show_std()
  create_df2()
  """
  drop_adhoctest()
  return


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
