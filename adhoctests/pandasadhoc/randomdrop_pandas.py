"""
# pd.set_option('max_lines', None)

"""
from collections import namedtuple
import pandas as pd
import random
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
columns = ['seq', 'text', 'amount']
NTRow = namedtuple('NTRow', columns)


def gen_amount(seq):
  other = random.randint(1, seq)
  return (seq + other) / 2


class Frame:

  def __init__(self):
    self.df = None
    self.process()

  def create_df(self):
    ntrows = []
    for i in range(10):
      seq = random.randint(1, 20)
      nt = NTRow(seq, 'text'+str(seq), gen_amount(seq))
      ntrows.append(nt)
    self.df = pd.DataFrame(ntrows)
    print(self.df.to_string())

  def drop_rows(self):
    n_rows = self.df.shape[0]
    iloop = 0
    while n_rows > 0:
      r = random.randint(0, n_rows-1)
      idx = self.df.index[r]
      series = self.df.loc[idx]
      print(self.df.index)
      print('len', n_rows, ' rand =', r, ' del_idx =', idx, 'Series =>', series.seq, series.text, series.amount)
      self.df.drop(idx, axis=0, inplace=True)
      iloop += 1
      if iloop > 300:
        break
      n_rows = self.df.shape[0]

  def process(self):
    self.create_df()
    self.drop_rows()


def adhoctest():
  pass


def process():
  """
  for row in df.iterrows():
    print(row)
  """
  Frame()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
