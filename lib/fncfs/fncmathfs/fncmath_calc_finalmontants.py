"""
lib/fncfs/fncmathfs/fncmath_calc_finalmontants.py

To import it:
  import lib.fncfs.fncmathfs.finance_math_fs as fncmath  # fncmath.calc_ir_incrfact_f_mora_w_idx_n_expo()
"""
import functools
import operator
from decimal import Decimal
import calendar
import datetime
import decimal
import lib.datesetc.datefs as dtfs  # for partition_inidate_findate_as_monthndays_tuplelist
import lib.datesetc.refmonth_fs as rmfs  # for partition_inidate_findate_as_monthndays_tuplelist
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcafs  # ipcafs.IpcaAPICacherRetriever
from lib.datesetc.refmonth_fs import make_refmonth_or_raise
DECIMAL_ZERO = Decimal('0.00')


def calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
    ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  """
  Returns the multiplier (or the factor) for Interest Rate (ir)
    calculation based on the IR index (ir_idx) and the exponent (duration).

  The exponent here is independent on the duration time units (days, months, etc.),
    which might be anyone in the caller. Another function below wraps parameter 'monthduration',
    which then calls this with 'monthduration' as 'exponent'.

  Acronyms:
    ir -> interest rate | ir idx -> interest rate index
    incrfactor -> interest rate multiplier for finding the 'incr' (increment factor)
  """
  try:
    ir_idx = Decimal(ir_idx)
    exponent = Decimal(exponent)
  except (ValueError, TypeError, decimal.InvalidOperation) as e:
    errmsg = f"acc index ({ir_idx}) and/or exponent ({exponent}) are invalid: {e}"
    raise ValueError(errmsg)
  multiplier = (1 + ir_idx) ** exponent
  return multiplier


def calc_multiplier_for_increase_intrstrt_w_1iridx_2expo(
    ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  intermediate = (1 + ir_idx) ** exponent
  multiplier_for_finalmontant = calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
    ir_idx=ir_idx,
    exponent=exponent,
  )
  if multiplier_for_finalmontant < 2:
    multiplier_for_increase = multiplier_for_finalmontant - 1
  else:
    multiplier_for_increase = multiplier_for_finalmontant
  return multiplier_for_increase


def calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo(
    inimontant: Decimal, ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  """
  Calculates the increase amount with initial montant,
    the interest rate index, and the exponent (duration).

  This function reuses calc_incrfactor_intrstrt_w_1iridx_2expo()
  """
  try:
    inimontant = Decimal(inimontant)
    ir_idx = Decimal(ir_idx)
    exponent = Decimal(exponent)
  except (ValueError, TypeError, decimal.InvalidOperation) as e:
    errmsg = f"acc index ({ir_idx}) and/or exponent ({exponent}) are invalid: {e}"
    raise ValueError(errmsg)
  increase_factor = calc_multiplier_for_increase_intrstrt_w_1iridx_2expo(
    ir_idx=ir_idx, exponent=exponent
  )
  increase_amount = inimontant * increase_factor
  return increase_amount


def calc_finalmontant_w_1inimontant_2iridx_3expo(
    inimontant: Decimal, ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  """
  Calculates the final montant with initial montant,
    the interest rate index, and the exponent (duration).

  This function reuses calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo()
  """
  try:
    inimontant = Decimal(inimontant)
  except (ValueError, TypeError, decimal.InvalidOperation) as e:
    errmsg = f"acc index ({ir_idx}) and/or exponent ({exponent}) are invalid: {e}"
    raise ValueError(errmsg)
  r_finalmontant = inimontant * calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(ir_idx, exponent)
  return r_finalmontant


def calc_finalmontant_w_1inimontant_2fixir_3varir_4monthsduration(
    inimontant: Decimal, fixir: Decimal, varir: Decimal, monthsduration: Decimal
  ) -> Decimal:
  """
  Calculates final montant as the above function (*) does.
  (*) calc_finalmontant_w_1inimontant_2ir_3expo()
  It adds up the two indices (called fix and variable) and reuses the function above.
  """
  try:
    ir_idx = Decimal(fixir + varir)
  except (ValueError, TypeError, decimal.InvalidOperation) as e:
    errmsg = f"fixir index ({fixir}) and/or varir ({varir}) are invalid: {e}"
    raise ValueError(errmsg)
  return calc_finalmontant_w_1inimontant_2iridx_3expo(
    inimontant=inimontant, ir_idx=ir_idx, exponent=monthsduration
  )


def calc_finalmontant_w_1inimontant_2iridx_3partitionmonths(
    inimontant: Decimal, ir_idx: Decimal, partitionmonths: list[tuple[int, datetime.date]]
  ) -> tuple[Decimal, list[tuple[int, Decimal]]]:
  """
  Idem as the final montant montant calculator above, but it
    runs one or more calculations as they are contained in a 'partition'.
  This partition is an additive 'batch' calculation.
  One main application for this 'batch' calculation' is
    when the partition represents months (each one a tuple with 'days used' and the month itself).

  calc_finalmontant_w_1inimontant_2ir_3partitionmonths
  """
  ongoing_montant = inimontant
  quinhoes = []
  for partitionmonth in partitionmonths:
    ndays, refmonth = partitionmonth
    _, ndaysinmonth = calendar.monthrange(refmonth)
    monthsduration = Decimal(ndays / ndaysinmonth)
    increase_amount = calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo(
        inimontant=ongoing_montant, ir_idx=ir_idx, exponent=monthsduration
    )
    quinhoes.append((increase_amount, refmonth))
    ongoing_montant += increase_amount
  r_finalmontant = ongoing_montant
  return r_finalmontant, quinhoes


def calc_finalmontant_w_1inimontant_2fixir_fetchipca_3partitionmonths(
      inimontant: Decimal, fixir: Decimal,
      partitionmonths: list[tuple[int, datetime.date]],
      m_minus_n: int = 2,
  ) -> tuple[Decimal, list[tuple[Decimal, datetime.date]]]:
  """
  Idem as above but it needs first to add up the two IR indices,
    then it calls (reuses) the above function.
  """
  # 1 prepare the
  ongoing_montant = inimontant
  quinhoes = []
  ipcacacher = ipcafs.IpcaAPICacherRetriever()
  for partitionmonth in partitionmonths:
    ndays, refmonth = partitionmonth
    _, ndaysinmonth = calendar.monthrange(refmonth.year, refmonth.month)
    monthsduration = Decimal(ndays / ndaysinmonth)
    ipcadec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(
      p_refmonth=refmonth, n=m_minus_n)
    ir_idx = fixir + ipcadec
    increase_amount = calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo(
        inimontant=ongoing_montant, ir_idx=ir_idx, exponent=monthsduration
    )
    quinhoes.append((increase_amount, refmonth))
    ongoing_montant += increase_amount
  r_finalmontant = ongoing_montant
  return r_finalmontant, quinhoes


def calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant: Decimal, fixir: Decimal, inidate: datetime.date, findate: datetime.date
  ) -> tuple[Decimal, list[tuple[Decimal, datetime.date]]]:
  # duration may be partitioned
  inidate = dtfs.make_date_or_raise(inidate)
  findate = dtfs.make_date_or_raise(findate)
  if (inidate.year, inidate.month) == (findate.year, findate.month):
    # same month case
    refmonth = rmfs.make_refmonth_or_raise(inidate)
    ndays = findate.day - inidate.day + 1
    _, totaldaysinmonth = calendar.monthrange(inidate.year, inidate.month)
    monthduration = Decimal(ndays / totaldaysinmonth)
    ipcacacher = ipcafs.IpcaAPICacherRetriever()
    refmonth = make_refmonth_or_raise(inidate)
    ipcadec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(refmonth, 2)
    ipcadec = DECIMAL_ZERO if ipcadec is None else ipcadec
    r_finalmontant = calc_finalmontant_w_1inimontant_2fixir_3varir_4monthsduration(
      inimontant=inimontant,
      fixir=fixir,
      varir=ipcadec,
      monthsduration=monthduration
    )
    #
    # it was only one month: create a 'quinhão' with it
    # quinhaotuple contains (first) value and (second) refmonth.
    quinhaotuple = (r_finalmontant, refmonth)
    quinhoes = [quinhaotuple]
    return r_finalmontant, quinhoes
  # from this point on, there are more than one month
  partitionmonths = rmfs.mk_partition_inidate_findate_as_ndays_n_refms_tlist(inidate, findate)
  return calc_finalmontant_w_1inimontant_2fixir_fetchipca_3partitionmonths(
    inimontant=inimontant,
    fixir=fixir,
    partitionmonths=partitionmonths
  )


def calc_incr_amt_w_1inimontant_2iridx_wo_varir_3exposeries(
    inimontant: Decimal, ir_idx: Decimal, exposeries: list[Decimal],
):
  """
  Calculates increase amount with iridx through a series of duration
  """
  increase_amount = 1
  for exponent in exposeries:
    i_increase_amount = calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent,
    )
    increase_amount *= i_increase_amount
  return increase_amount


def calc_finalmontant_w_1inimontant_2iridx_wo_varir_3exposeries(
    inimontant: Decimal, ir_idx: Decimal, exposeries: list[Decimal],
  ):
  """
  Calculates final montant with iridx through a series of duration
  """
  increase_amount = calc_incr_amt_w_1inimontant_2iridx_wo_varir_3exposeries(
    inimontant=inimontant,
    ir_idx=ir_idx,
    exposeries=exposeries,
  )
  r_finalmontant = inimontant * increase_amount
  return r_finalmontant


def calc1_increase_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant: Decimal, fixir: Decimal, inidate: datetime.date, findate: datetime.date
  ) -> Decimal:
  """
  Calculates the IR increment on inimont between two dates (inclusive),
  Reusing the above functions, there are two of doing it:
    a) calculate total_increase taking the subtract of final montant from initial montant;
    b) calculate total_increase from 'quinhoes';
  Letter 'a' was chosen (@see below).
  """
  finalmontant, _ = calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant=inimontant, fixir=fixir, inidate=inidate, findate=findate
  )
  total_increase = finalmontant - inimontant
  return total_increase


def calc2_increase_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant: Decimal, fixir: Decimal, inidate: datetime.date, findate: datetime.date
  ) -> Decimal:
  """
  Calculates the IR increment on inimont between two dates (inclusive),
  Reusing the above functions, there are two of doing it:
    a) calculate total_increase from 'quinhoes';
    b) calculate total_increase taking the subtract of final montant from initial montant;
  Letter 'b' was chosen (@see below) - @see also letter 'a' above.
  """
  _, quinhoes = calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant=inimontant, fixir=fixir, inidate=inidate, findate=findate
  )
  increases = [t[0] for t in quinhoes]
  # total_increase = functools.reduce(operator.add, increases, 0)
  total_increase = sum(increases)
  total_increase = Decimal(total_increase)
  return total_increase


def calc_incr_insamemonth_w_1inimontant_2fixplusvardec_3inidate_4findate(
    inimontant: Decimal, fixplusvardec: Decimal, inidate: datetime.date, findate: datetime.date
  ) -> Decimal:
  """
  Calculates the IR increment on inimontant between two dates (inclusive)
    within the same month.

  Obs:
    1- this function pressuposes inidate and findate belong to the same month;
    2 - if dates are in different months, ValueError is raised;
    3 - also, if monthly inflationi rates are different, it would be inconsistent to have the same
        ir_idx across months.

  There are other functions in this module that can do the same calculation
    over various months with or without a variable monthly IR component.

  In words, this function considers a monthly variable inflation rate,
    which 'comes inside' parameter fixplusvardec.
  """
  inidate = dtfs.make_date_or_raise(inidate)
  findate = dtfs.make_date_or_raise(findate)
  if (inidate.year, inidate.month) != (findate.year, findate.month):
    errmsg = f"Error: inidate ({inidate}) and findate ({findate}) must be in the same month."
    raise ValueError(errmsg)
  _, ndaysinmonth = calendar.monthrange(inidate.year, inidate.month)
  ndays_elapsed = findate.day - inidate.day + 1
  monthsduration = Decimal(ndays_elapsed / ndaysinmonth)
  increase_amount = calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo(
    inimontant=inimontant, ir_idx=fixplusvardec, exponent=monthsduration
  )
  return increase_amount


def calc_incrfactor_w_iridx_n_expo_zippedtuplelist(
    tuplelist_iridx_n_expo: list[tuple[Decimal, Decimal]],
  ):
  elems = [(1 + x) ** y for (x, y) in tuplelist_iridx_n_expo]
  produtory = functools.reduce(operator.mul, elems, 1)
  produtory = Decimal(produtory)  # IDE complains here about type
  return produtory


def calc_finalmontant_w_1inimontant_2iridx_n_expo_zippedtuplelist(
    inimontant: Decimal,
    tuplelist_iridx_n_expo: list[tuple[Decimal, Decimal]],
  ):
  """

  """
  produtory = calc_incrfactor_w_iridx_n_expo_zippedtuplelist(
    tuplelist_iridx_n_expo=tuplelist_iridx_n_expo,
  )
  r_finalmontant = inimontant * produtory
  return r_finalmontant


def adhoctest1():
  """
  adhoctest1 are 'quick' print test here.
  @see also unit-tests in their module.
  """
  ir_idx, exponent = Decimal(.023), Decimal(2)
  multiplier = calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(ir_idx, exponent)
  scrmsg = f"(float res) input: ir_idx={ir_idx:.04f}, exponent={exponent} | output multiplier={multiplier:.04f}"
  print(scrmsg)
  # ===============
  inimontant = Decimal(1000)
  finalmontant = calc_finalmontant_w_1inimontant_2iridx_3expo(inimontant, ir_idx, exponent)
  scrmsg = f"(dec res) input: inimontant={inimontant}, ir_idx={ir_idx:.04f}, exponent={exponent} | output finalmontant={finalmontant:.04f}"
  print(scrmsg)
  # ===============
  fixir, varir, monthduration = Decimal(.02), Decimal(.0034), Decimal(2.5)
  finalmontant = calc_finalmontant_w_1inimontant_2fixir_3varir_4monthsduration(inimontant, fixir, varir, monthduration)
  scrmsg = f""" Example:
  input:  initial montant={inimontant}, fix ir={fixir:.04f}, var ir={varir:.04f}, month duration={monthduration}
  output: final montant={finalmontant:.04f}"""
  print(scrmsg)
  # ===============


def adhoctest2():
  mkdt = dtfs.make_date_or_raise
  inidate, findate = mkdt('2026-1-5'), mkdt('2026-3-18')
  inimontant, fixir = Decimal(1000), Decimal(.02)
  finalmontant, quinhoes = calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant=inimontant,
    fixir=fixir,
    inidate=inidate,
    findate=findate
  )
  scrmsg = f"""input:
     inidate, findate = {inidate}, {findate}
     inimontant, fixir = {inimontant:.02f}, {fixir:.04f}
   output:
      finalmontant = {finalmontant:.02f}
      quinhoes = {quinhoes}
  """
  print(scrmsg)


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
