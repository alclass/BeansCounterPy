import functools
import operator
from decimal import Decimal


def func1():
  # tuplelist_iridx_n_expo = [(1,2), (2,1), (1.5, 1.5)]
  tuplelist_iridx_n_expo = [(1,2), (2,1)]
  elems = [(1 + x) ** y for (x, y) in tuplelist_iridx_n_expo]
  produtory = functools.reduce(operator.mul, elems, 1)
  # produtory = Decimal(produtory)
  # by hand
  return produtory

def finm(im, i, e):
  return im * (1 + i) ** e

def multip(i, e):
  return (1 + i) ** e


def incrfact(i, e):
  mtp = multip(i, e)
  if mtp < 2:
    return mtp - 1
  return mtp


def adhoctest2():
  im, i, e = 1, 0.1, 2
  fm = finm(im, i, e)
  ifact = incrfact(i, e)
  form = f"fm = {im} * (1 + {i}) ** {e} = {fm}  | ifact = {ifact}"
  print(form)
  # another
  im, i, e = 1, 2, 2
  fm = finm(im, i, e)
  ifact = incrfact(i, e)
  form = f"fm = {im} * (1 + {i}) ** {e} = {fm}  | ifact = {ifact}"
  print(form)
  # another
  im, i, e = 1, 1, 1
  fm = finm(im, i, e)
  ifact = incrfact(i, e)
  form = f"fm = {im} * (1 + {i}) ** {e} = {fm}  | ifact = {ifact}"
  print(form)
  # another
  im, i, e = 1, 0.9, 1
  fm = finm(im, i, e)
  ifact = incrfact(i, e)
  form = f"fm = {im} * (1 + {i}) ** {e} = {fm}  | ifact = {ifact}"
  print(form)


def adhoctest1():
  res = func1()
  print(res)
  byhand = ((1 + 1) ** 2) * ((1 + 2) ** 1)  # 12?
  print(byhand)
  produtory = functools.reduce(operator.mul, [1,2,3], 1)
  print(produtory)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  adhoctest2()
  """
  adhoctest2()
