import functools
import operator
import random
from decimal import Decimal, ROUND_HALF_EVEN
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fm_mnts  # fm_cmnts.calc_incrfactor_intrstrt_w_1iridx_2expo
import lib.datesetc.refmonth_fs as rmfs
import lib.datesetc.datefs as dtfs
mkdt = dtfs.make_date_or_raise
DECIMAL_ONE = Decimal(1)
dec_is_close = fm_mnts.dec_is_close
quant = fm_mnts.quant
q4 = fm_mnts.q4
q8 = fm_mnts.q8


def make_random_inimontants(n: int, param_hi: int, param_lo: int) -> list[Decimal]:
  """
  Make n random initial montants according to a rule of a parameter-function superior and inferior.
  """
  if param_hi < param_lo:
    # swap them if ri_num < ri_den
    tmp = param_hi
    param_hi = param_lo
    param_lo = tmp
  inimontants: list[Decimal] = []
  for i in range(n):
    ri_num = random.randint(param_lo, param_hi)
    ri_den = random.randint(param_lo, param_hi)
    if ri_num < ri_den:
      # swap them if ri_num < ri_den
      tmp = ri_num
      ri_num = ri_den
      ri_den = tmp
    try:
      inimontant = Decimal(ri_num * 100 / ri_den)
    except ZeroDivisionError:
      inimontant = Decimal(ri_num * 100 / 1)
    inimontants.append(inimontant)
  return inimontants


def make_random_tuplelist_iridx_exponent(
    n: int, ir_range: tuple[float, float], exp_range: tuple[float, float],
  ) -> list[tuple[Decimal, Decimal]]:
  """
  Make n random tuples with iridx and exponent according to their ranges.
  """
  tuplelist_iridx_exponent: list[tuple[Decimal, Decimal]] = []
  for _ in range(n):
    ir_idx = random.uniform(ir_range[0], ir_range[1])
    exponent = random.uniform(exp_range[0], exp_range[1])
    ir_idx, exponent = q8(Decimal(ir_idx)), q8(Decimal(exponent))
    tuplelist_iridx_exponent.append((ir_idx, exponent))
  return tuplelist_iridx_exponent


def func1():
  # tuplelist_iridx_n_expo = [(1,2), (2,1), (1.5, 1.5)]
  tuplelist_iridx_n_expo = [(1,2), (2,1)]
  elems = [(1 + x) ** y for (x, y) in tuplelist_iridx_n_expo]
  produtory = functools.reduce(operator.mul, elems, 1)
  # produtory = Decimal(produtory)
  # by hand
  # noinspection bad-argument-type
  produtory = Decimal(produtory)
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
  # noinspection bad-argument-type
  produtory = Decimal(produtory)
  print(produtory)


def adhoctest4():
  monthpartition = [
    (15, mkdt('2026-04')),
    (3, mkdt('2026-01')),
  ]
  d1 = DECIMAL_ONE
  inimontant, ir_idx = 3 * d1, d1 / 10
  exponents = [Decimal(.5), Decimal(3 / 31)]
  byhand_multfactor_for_fm = (1 + ir_idx) ** exponents[0]
  byhand_multfactor_for_fm *= (1 + ir_idx) ** exponents[1]
  print('byhand_multfactor_for_fm', byhand_multfactor_for_fm)
  final_montant = inimontant * byhand_multfactor_for_fm
  print('final montant', final_montant)
  ret_finalmontant_direct, quinhoes1 = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3monthpartition(
    inimontant=inimontant,
    ir_idx=ir_idx,
    monthpartition=monthpartition,
  )
  print('ret_finalmontant_direct', ret_finalmontant_direct)
  # make_random_inimontants
  inimontants = make_random_inimontants(n=10, param_hi=100, param_lo=10)
  print('make_random_inimontants(n=10, param_hi=100, param_lo=10)')
  for i, inimont in enumerate(inimontants):
    line = f"{i+1} inimontant random {inimont:.2f}"
    print(line)
  tuplelist_iridx_exponent = make_random_tuplelist_iridx_exponent(
    n=10, ir_range=(0.005, 1.345), exp_range=(0.45, 15.468)
  )
  for i, tupl in enumerate(tuplelist_iridx_exponent):
    print(tupl)


def adhoctest5() -> None:
  # d1 = DECIMAL_ONE
  # ========================
  dec_1 = Decimal('376864724583327170969454.0846')
  dec_2 = Decimal('376864724583327170969454.0840')
  print('dec_1 =', dec_1, '| dec_2 =', dec_2)
  print('is equal?', dec_1 == dec_2)
  boolval = dec_is_close(dec_1, dec_2)
  print('is close?', boolval)


def adhoctest6() -> None:
  d1 = DECIMAL_ONE
  # ========================
  inidate, findate = mkdt('2026-1-15'), mkdt('2026-1-31')
  inimontant, ir_idx = 3 * d1, 10 * d1 / 100
  finmontant_by_samemonth_fn, quinhoes = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant=inimontant, ir_idx=ir_idx, inidate=inidate, findate=findate,
  )
  monthsfraction = (31 - 15 + 1) * d1 / 31  # (31-15+1) (used) days in the 31-day month
  scrmsg = (f"inidate = {inidate}, findate = {findate} | inimontant={inimontant}"
            f" | monthsfraction={monthsfraction:.4f} | ir_idx={ir_idx}")
  print(scrmsg)
  finmontant_by_direct_fn = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3expo(
    inimontant=inimontant, ir_idx=ir_idx, exponent=monthsfraction,
  )
  increase_amount = finmontant_by_direct_fn - inimontant
  is_close = fm_mnts.dec_is_close(increase_amount, quinhoes[0])
  print('increase_amount =', increase_amount, 'increase in quinhoes =', quinhoes[0], 'is_close =', is_close)
  is_close = fm_mnts.dec_is_close(finmontant_by_direct_fn, finmontant_by_samemonth_fn)
  print(
    'finmontant_by_direct_fn =', finmontant_by_direct_fn,
    'finmontant_by_samemonth_fn =', finmontant_by_samemonth_fn, 'is_close =', is_close)


def adhoctest7() -> None:
  dec_1 = Decimal('376864724583327170969454.0846')
  newdec = fm_mnts.round_sigfigs(d=dec_1, sigfigs=8)
  print(dec_1, 'fm_mnts.round_sigfigs(d=dec_1, sigfigs=8) => newdec =', newdec)
  dec_2 = dec_1 / Decimal('1e22')
  print(dec_1, 'dec_2 = dec_1 / Decimal(1e22)', dec_2)
  dec_3 = newdec / Decimal('1e22')
  print(newdec, 'newdec / Decimal(1e22) =', dec_3)
  f = 1.76864724 * 1e8
  dectest = Decimal(f)  # '1.' + '0'*11
  quantizer = Decimal('1').scaleb(3)
  decquantd = dectest.quantize(quantizer, rounding=ROUND_HALF_EVEN)
  print('dectest =', dectest, ' | quantizer =', quantizer, ' | decquantd =', decquantd)


def adhoctest8() -> None:
  inidate, findate = mkdt('2026-1-15'), mkdt('2026-1-31')
  d1 = DECIMAL_ONE
  inimontant, ir_idx = 3 * d1, 10 * d1 / 100
  iridxlist = [ir_idx]
  ir_idx2 = 2 * ir_idx
  iridxlist.append(ir_idx2)
  finmontant_samemonth_1, quinhoes = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant=inimontant, ir_idx=ir_idx, inidate=inidate, findate=findate,
  )
  monthsfraction = (31 - 15 + 1) * d1 / 31  # (31-15+1) (used) days in the 31-day month
  finmontant_by_direct_fn = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3expo(
    inimontant=inimontant, ir_idx=ir_idx, exponent=monthsfraction,
  )
  increase_amount = finmontant_by_direct_fn - inimontant
  increase_samemonth_1 =finmontant_samemonth_1 - inimontant
  monthpartition_tuple = rmfs.make_monthpartition_tuple_fr_date(inidate, fr_beginning=False)
  monthpartition = [monthpartition_tuple]
  anothermonth_inidate = mkdt('2026-3-1')
  anothermonth_findate = mkdt('2026-3-13')
  finmontant_samemonth_2, anothermonth_quinhoes = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant=finmontant_samemonth_1,
    ir_idx=ir_idx2,
    inidate=anothermonth_inidate,
    findate=anothermonth_findate,
  )
  increase_samemonth_2 = finmontant_samemonth_2 - finmontant_samemonth_1
  monthpartition_tuple = rmfs.make_monthpartition_tuple_fr_date(anothermonth_findate, fr_beginning=True)
  monthpartition.append(monthpartition_tuple)
  twostep_quinhoes = quinhoes + anothermonth_quinhoes
  finmontant_by_monthpartition, twomonth_quinhoes = fm_mnts.calc_finmontant_w_1inimontant_2iridxlist_3monthpartition(
    inimontant=inimontant,
    iridxlist=iridxlist,
    monthpartition=monthpartition,
  )
  acc_piecemeal_fm = inimontant + increase_samemonth_1 + increase_samemonth_2
  print('iridxlist', iridxlist)
  print('monthpartition', monthpartition)
  print('two_step_quinhoes', twostep_quinhoes)
  print('twomonth_quinhoes', twomonth_quinhoes)
  acc_piecemeal_fm = fm_mnts.sigfig(acc_piecemeal_fm, 10)
  print('acc_piecemeal_fm', acc_piecemeal_fm)
  print('finmontant_by_monthpartition', finmontant_by_monthpartition)
  bool_dec_is_close = fm_mnts.dec_is_close(acc_piecemeal_fm, finmontant_by_monthpartition)
  print('dec_is_close()', bool_dec_is_close)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  adhoctest1()
  adhoctest2()
  adhoctest4()
  """
  adhoctest8()
