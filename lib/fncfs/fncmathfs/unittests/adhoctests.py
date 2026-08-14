import functools
import operator
from decimal import Decimal
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants as fm_mnts  # fm_cmnts.calc_incrfactor_intrstrt_w_1iridx_2expo
import lib.datesetc.refmonth_fs as rmfs
decimal_one = Decimal(1)


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


def adhoctest3():
  res = func1()
  print(res)
  byhand = ((1 + 1) ** 2) * ((1 + 2) ** 1)  # 12?
  print(byhand)
  produtory = functools.reduce(operator.mul, [1,2,3], 1)
  print(produtory)


def adhoctest4():
  mkdt = rmfs.make_refmonth_or_raise
  monthpartition = [
    (15, mkdt('2026-04')),
    (3, mkdt('2026-01')),
  ]
  d1 = decimal_one
  inimontant, ir_idx = 3 * d1, d1 / 10
  exponents = [Decimal(.5), Decimal(3 / 31)]
  byhand_multfactor_for_fm = (1 + ir_idx) ** exponents[0]
  byhand_multfactor_for_fm *= (1 + ir_idx) ** exponents[1]
  print('byhand_multfactor_for_fm', byhand_multfactor_for_fm)
  final_montant = inimontant * byhand_multfactor_for_fm
  print('final montant', final_montant)
  ret_finalmontant_direct, quinhoes1 = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_3monthpartition(
    inimontant=inimontant,
    ir_idx=ir_idx,
    monthpartition=monthpartition,
  )
  print('ret_finalmontant_direct', ret_finalmontant_direct)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  adhoctest2()
  """
  adhoctest4()
