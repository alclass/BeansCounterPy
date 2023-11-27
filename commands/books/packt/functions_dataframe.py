#!/usr/bin/env python3
"""
commands/books/functions_dataframe.py
  => helper/util functions for the getting of Packt's book isbn's et al.
"""
import os.path

import numpy as np
import pandas as pd


def create_n_get_nparray_test():
  """
  create a 4 x 3 [1, 20]-randint array

  choice = random. choice(1, 100)
  choice = random. randint(1, 100)
  print(choice)
  import random.
  choice = random. random(1, 100)
  """
  nrows = 4
  ncols = 3
  size = ncols * nrows
  arr = np.random.randint(low=1, high=21, size=size)
  print(arr)
  arr = arr.reshape((nrows, ncols))
  print(arr)
  return arr


def create_preestablished_nparr():
  arr = [2,  4,  7, 16, 13, 17, 14,  2,  9,  1,  1, 19]
  arr = np.array(arr)
  print(arr)
  nrows = 4
  ncols = 3
  size = ncols * nrows
  assert (size == len(arr))
  arr = arr.reshape((nrows, ncols))
  return arr


def create_df_test():
  # arr = create_n_get_nparray_test()
  arr = create_preestablished_nparr()
  df = pd.DataFrame(arr)
  df[df < 3] = np.NaN
  df[df > 17] = np.NaN
  print('Random df')
  print(df.to_string())
  return df


def extract_rows_with_no_na(df):
  extraction = df[~df.isna().any(axis=1)]
  return extraction


def extract_rows_that_have_at_least_one_na(df):
  """
  print('Copied df')
  print(extraction.to_string())
  print('Original df')
  print(df.to_string())
  # copied = df[df.isnull().any(1)]  # obs: this formulation does not work, though it's been found around...
  """
  extraction = df[df.isna().any(axis=1)]
  return extraction


def adhoctest():
  df = create_df_test()
  df_w_nas = extract_rows_that_have_at_least_one_na(df)
  print('df_w_nas')
  print(df_w_nas.to_string())
  df_wo_nas = extract_rows_with_no_na(df)
  print('df_wo_nas')
  print(df_wo_nas.to_string())


def process():
  pass


if __name__ == '__main__':
  """
  process()
  adhoctest()
  """
  adhoctest()
