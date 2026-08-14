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
# from lib.datesetc.refmonth_fs import make_refmonth_or_raise
DECIMAL_ZERO = Decimal('0.00')
DECIMAL_ONE = Decimal('1.0')


def calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
    ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  """
  Calculates the multiplier by initial montant that gives 'final montant'.
    => fm = im * (1 + ir) ** exponent
    the multiplier here is: (1 + ir) ** exponent
  @see also next function that calculates the multiplier by initial montant
    that gives rather the 'amount increase'.

  Where:
    ir_idx is the Interest Rate index
    exponent is the exponent (the time duration of the interest rate calcuation.)

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
  """
  Calculates the multiplier by initial montant that gives the 'amount increase'.
      => fm = im * (1 + ir) ** exponent
    the multiplier here is: (1 + ir) ** exponent - 1
  @see also previous function that calculates the multiplier by initial montant
    that gives rather final montant.

  @see also unit-tests related to 'multiplier_for_increase'.
  The tests contemplate:
    a) 'multiplier_for_increase' comparisons with expected values
    b) 'multiplier_for_increase' comparisons related to 'multiplier_for_finalmontant'
    c) comparison with two calculations of finalmontant:
      with c1 addition of 'increase' to initial montant giving final montant;
      with c2 multiplying of 'multiplier_for_increase' by initial montant giving final montant;
  """
  multiplier_for_finalmontant = calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
    ir_idx=ir_idx,
    exponent=exponent,
  )
  multiplier_for_increase = multiplier_for_finalmontant - 1
  return multiplier_for_increase


def calc_increase_amount_intrstrt_w_1inimomtant_2iridx_3expo(
    inimontant: Decimal, ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  """
  Calculates the increase amount with:
   initial montant, interest rate index, and exponent (duration).

  This function reuses calc_multiplier_for_increase_intrstrt_w_1iridx_2expo()
  @see it below.
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
  Calculates the final montant with:
    initial montant, interest rate index, and exponent (duration).

  This function reuses calc_multiplier_for_fm_intrstrt_w_1iridx_2expo()
  @see it below.
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
  The calculation itself is not here, this function does the following:
    1 sanitize 2 parameter indices fixir and varir
    2 sums up the 2 indices: fixir and varir to ir_idx
    3 dispatches execution to a function that receives ir_idx and monthsduration as exponent.

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


def calc_multiplicationfactor_for_fm_w_1iridx_2monthpartition(
    ir_idx: Decimal, monthpartition: list[tuple[int, datetime.date]]
  ) -> tuple[Decimal, list[Decimal]]:
  """
  Calculates the multiplication factor compounded throughout a series of months
    each month having a certain fraction of itself.

  What's in a monthpartition?
    It's a tuple list that informs a number of days and its corresponding refmonth.

  For example:
    if a monthpartition is: [(15, mkrm('2026-4')), (3, mkrm('2026-4'))]
    this means that 15 days were 'used' in April 2026 and 3/31 days in January 2026.

  The return is a tuple composed of the multiplication factors. Notice that this is different from 'quinhões'.
  'quinhões' contains the increase amounts and also the refmonths; factor contains the multiplication factors.
  """
  base = Decimal(1 + ir_idx)
  monthsfractions = rmfs.calc_fractionlist_fr_monthpartition(monthpartition)
  multiplicationfactors = list(map(lambda expo: base ** expo, monthsfractions))
  mult_factor_for_finalmontant = functools.reduce(operator.mul, multiplicationfactors, 1)
  # the IDE does not recognize mult_factor_for_finalmontant with type-conforming to Decimal (though its results is a number)
  # the IDE included the next comment when we asked to suppress the mentioned warning
  # noinspection bad-argument-type
  mult_factor_for_finalmontant = Decimal(mult_factor_for_finalmontant)
  return mult_factor_for_finalmontant, multiplicationfactors


def calc_multiplicationfactor_for_increase_w_1iridx_2monthpartition(
    ir_idx: Decimal, monthpartition: list[tuple[int, datetime.date]]
  ) -> tuple[Decimal, list[Decimal]]:
  """
  Calculates the multiplication factor compounded throughout a series of months, each having a certain month's fraction.
  @see also docstr for the function above.

  Notice: when the function receiving monthpartition does not have inimontant as input,
    multiplicationfactors is in the output instead of quinhoes.
  """
  multiplicationfactor_fo_fm, quinhoes = calc_multiplicationfactor_for_fm_w_1iridx_2monthpartition(
    ir_idx=ir_idx, monthpartition=monthpartition
  )
  multiplicationfactor_fo_incr = multiplicationfactor_fo_fm - 1
  return multiplicationfactor_fo_incr, quinhoes


def calc_increase_amount_w_1inimontant_2iridx_3monthpartition(
    inimontant: Decimal, ir_idx: Decimal, monthpartition: list[tuple[int, datetime.date]]
  ) -> tuple[Decimal, list[tuple[Decimal, datetime.date]]]:
  """

  """
  multiplicationfactor_fo_incr, quinhoes = calc_multiplicationfactor_for_increase_w_1iridx_2monthpartition(
    ir_idx=ir_idx, monthpartition=monthpartition
  )
  increase_amount = inimontant * multiplicationfactor_fo_incr
  return increase_amount, quinhoes


def calc_finalmontant_w_1inimontant_2iridx_3monthpartition(
    inimontant: Decimal, ir_idx: Decimal, monthpartition: list[tuple[int, datetime.date]]
  ) -> tuple[Decimal, list[tuple[Decimal, datetime.date]]]:
  """
  Idem as the final montant calculator above, but it
    runs one or more calculations as they are contained in a 'partition'.

  One main application for this 'batch' calculation' is
    when the partition represents months (each one a tuple with 'days used' and the month itself).

  A month partition is a list of tuples where the latter
       contains the numbers of 'used days' and the month itself (represented by a 'refmonth' (*))

    (*) A refmonth is a date with day=1 and is useful for representing months.

    This information gives the exponent in the IR expression.
    Examples:
      a) if tuple is (15, '2026-04'), then exponent will be 15 (days) by 30 (total days in April) = 0.5
      b) if tuple is (3, '2026-01'), then exponent will be 3 (days) by 31 (total days in April) = 3/31

  calc_finalmontant_w_1inimontant_2ir_3partitionmonths
  """
  ongoing_montant = inimontant
  quinhoes = []
  for partitionmonth in monthpartition:
    ndays, refmonth = partitionmonth
    _, ndaysinmonth = calendar.monthrange(refmonth.year, refmonth.month)
    monthsduration = Decimal(ndays / ndaysinmonth)
    increase_amount = calc_increase_amount_intrstrt_w_1inimomtant_2iridx_3expo(
        inimontant=ongoing_montant, ir_idx=ir_idx, exponent=monthsduration
    )
    quinhoes.append((increase_amount, refmonth))
    ongoing_montant += increase_amount
  r_finalmontant = ongoing_montant
  return r_finalmontant, quinhoes


def calc_finalmontant_w_1inimontant_2fixir_fetchipca_3monthpartition(
      inimontant: Decimal, fixir: Decimal,
      monthpartition: list[tuple[int, datetime.date]],
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
  for partitionmonth in monthpartition:
    ndays, refmonth = partitionmonth
    _, ndaysinmonth = calendar.monthrange(refmonth.year, refmonth.month)
    monthsduration = Decimal(ndays / ndaysinmonth)
    ipcadec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(
      p_refmonth=refmonth, n=m_minus_n)
    ir_idx = fixir + ipcadec
    increase_amount = calc_increase_amount_intrstrt_w_1inimomtant_2iridx_3expo(
        inimontant=ongoing_montant, ir_idx=ir_idx, exponent=monthsduration
    )
    quinhoes.append((increase_amount, refmonth))
    ongoing_montant += increase_amount
  r_finalmontant = ongoing_montant
  return r_finalmontant, quinhoes


def calc_finalmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant: Decimal, ir_idx: Decimal, inidate: datetime.date, findate: datetime.date,
  ) -> tuple[Decimal, list[tuple[Decimal, datetime.date]]]:
    inidate = rmfs.make_refmonth_or_raise(inidate)
    findate = rmfs.make_refmonth_or_raise(findate)
    if (inidate.year, inidate.month) != (findate.year, findate.month):
      errmsg = f"Error: dates should be in the same month: inidate={inidate}, findate={findate}"
      raise ValueError(errmsg)
    ndays = findate.day - inidate.day + 1
    _, totaldaysinmonth = calendar.monthrange(inidate.year, inidate.month)
    monthduration = Decimal(ndays / totaldaysinmonth)
    r_finalmontant = calc_finalmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=monthduration,
    )
    # it was only one month: create a 'quinhão' with it
    # quinhaotuple contains (first) value and (second) refmonth.
    refmonth = rmfs.make_refmonth_or_raise(inidate)
    quinhaotuple = (r_finalmontant, refmonth)
    quinhoes = [quinhaotuple]
    return r_finalmontant, quinhoes


def calc_finalmontant_w_1inimontant_2iridxlist_3partitionmonths(
    inimontant: Decimal, iridxlist: list[Decimal], monthpartition: list[tuple[int, datetime.date]]
  ) -> tuple[Decimal, list[tuple[Decimal, datetime.date]]]:
  ongoing_montant = inimontant
  quinhoes = []
  if len(iridxlist) != len(monthpartition):
    errmsg = (f"Error: iridxlist (len={len(iridxlist)}) and partitionmonths (len={len(monthpartition)})"
              f" should have the same length, they don't.")
    raise ValueError(errmsg)
  monthfractions = rmfs.calc_fractionlist_fr_monthpartition(monthpartition)
  for i, iridx in enumerate(iridxlist):
    monthfraction = monthfractions[i]
    cur_finalmontant = ongoing_montant * (1 + iridx) ** monthfraction
    quinhao = cur_finalmontant - ongoing_montant
    _, refmonth = monthpartition[i]
    quinhaotuple = (quinhao, refmonth)
    quinhoes.append(quinhaotuple)
    ongoing_montant = cur_finalmontant
  finalmontant = ongoing_montant
  return finalmontant, quinhoes


def calc_multiplier_fo_fm_w_1iridx_2exposeries(
    ir_idx: Decimal, exposeries: list[Decimal],
  ):
  """
  Calculates multiplifier factor with iridx through a series of duration
  """
  acc_multiplier = DECIMAL_ONE
  for exponent in exposeries:
    multiplier = calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent,
    )
    acc_multiplier *= multiplier
  return acc_multiplier


def calc_multiplier_fo_incr_w_1iridx_2exposeries(
    ir_idx: Decimal, exposeries: list[Decimal],
  ):
  multiplier_for_fm = calc_multiplier_fo_fm_w_1iridx_2exposeries(
    ir_idx=ir_idx,
    exposeries=exposeries,
  )
  multiplier_for_increase = multiplier_for_fm - 1
  return multiplier_for_increase


def calc_increase_amount_w_1inimontant_2iridx_3exposeries(
    inimontant: Decimal, ir_idx: Decimal, exposeries: list[Decimal],
):
  """
  Calculates increase amount with iridx through a series of duration
  """
  multiplier_for_increase = calc_multiplier_fo_incr_w_1iridx_2exposeries(
    ir_idx=ir_idx,
    exposeries=exposeries,
  )
  increase_amount = inimontant * multiplier_for_increase
  return increase_amount


def calc_finalmontant_w_1inimontant_2iridx_3exposeries(
    inimontant: Decimal, ir_idx: Decimal, exposeries: list[Decimal],
  ):
  """
  Calculates final montant with iridx through a series of duration
  """
  increase_amount = calc_increase_amount_w_1inimontant_2iridx_3exposeries(
    inimontant=inimontant,
    ir_idx=ir_idx,
    exposeries=exposeries,
  )
  r_finalmontant = inimontant + increase_amount
  return r_finalmontant


def calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant: Decimal, ir_idx: Decimal, inidate: datetime.date, findate: datetime.date
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
  increase_amount = calc_increase_amount_intrstrt_w_1inimomtant_2iridx_3expo(
    inimontant=inimontant, ir_idx=ir_idx, exponent=monthsduration
  )
  return increase_amount


def calc_multiplicationfactor_for_fm_w_1param_iridx_n_exponent_tuplelist(
    tuplelist_iridx_n_expo: list[tuple[Decimal, Decimal]],
  ):
  """
  Calculates the Interest Rate (IR) increase foctor from the tuple list with indices and exponents.

  This function does not output quinhoes:
    @see another function above that calculates with iridx's and exponents (one-to-one like this function)
    and returns quinhoes.

  One application is a calculation of IR along months that have each different indices and
   each not taking a full duration (partial months).
    For example:
      => month 1 (say January): index = 0.1, month's fraction = 1/2
      => month 2 (say February): index = 0.075, month's fraction = 3/4
      => month 3 (say March): index = 0.11, month's fraction = 1/3
    For the example above, the tuple list tuplelist_iridx_n_expo
      will be: [(0.1, 0.5), (0.075, 0.75), (0.11, 0.6667)]
  """
  elems = [(1 + x) ** y for (x, y) in tuplelist_iridx_n_expo]
  produtory = functools.reduce(operator.mul, elems, 1)
  # noinspection bad-argument-type
  produtory = Decimal(produtory)  # though it works, IDE complains here about type coming from reduce()
  return produtory


def calc_multiplicationfactor_for_increase_w_1param_iridx_n_exponent_tuplelist(
    tuplelist_iridx_n_expo: list[tuple[Decimal, Decimal]],
  ) -> Decimal:
  """
  Calculates the multiplication factor for finding the increase amount
    when each component may have a different index and a different duration.

  @see also previous function that calculates the multiplication factor
    for finding the final montant.
  """
  produtory = calc_multiplicationfactor_for_fm_w_1param_iridx_n_exponent_tuplelist(
    tuplelist_iridx_n_expo=tuplelist_iridx_n_expo,
  )
  multiplication_factor_for_increase = produtory - 1
  return multiplication_factor_for_increase


def calc_increase_amount_w_1param_iridx_n_exponent_tuplelist(
    inimontant: Decimal, tuplelist_iridx_n_expo: list[tuple[Decimal, Decimal]],
  ) -> Decimal:
  """
  Calculates increase amount on initial montant
    when each component may have a different index and a different duration.

  @see also docstr for calc_finalmontant_w_1param_iridx_n_exponent_tuplelist()
  """
  multiplication_factor_for_increase = calc_multiplicationfactor_for_increase_w_1param_iridx_n_exponent_tuplelist(
    tuplelist_iridx_n_expo=tuplelist_iridx_n_expo,
  )
  increase_amount = inimontant * multiplication_factor_for_increase
  return increase_amount


def calc_finalmontant_w_1param_iridx_n_exponent_tuplelist(
    inimontant: Decimal, tuplelist_iridx_n_expo: list[tuple[Decimal, Decimal]],
  ) -> Decimal:
  """
  Calculates final montant when each component may have a different index and a different duration.
  This function does not output quinhoes:
    @see another function above that calculates with iridx's and exponents (one-to-one like this function)
    and returns quinhoes (generally, they are inidate, findate parameter functions).

  This function does:
    r_finalmontant = inimontant * produtory
  It could also be:
    r_finalmontant = inimontant + increase_amount
  """
  produtory = calc_multiplicationfactor_for_fm_w_1param_iridx_n_exponent_tuplelist(
    tuplelist_iridx_n_expo=tuplelist_iridx_n_expo,
  )
  r_finalmontant = inimontant * produtory
  return r_finalmontant


def calc_increase_amount_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant: Decimal, fixir: Decimal, inidate: datetime.date, findate: datetime.date
  ) -> tuple[Decimal, list[tuple[Decimal, datetime.date]]]:
  """
  Calculates the IR increment on inimont between two dates (inclusive),
  Reusing the above functions, there are two of doing it:
    a) calculate total_increase taking the subtract of final montant from initial montant;
    b) calculate total_increase from 'quinhoes';
  Letter 'a' was chosen (@see below).
  """
  finalmontant, quinhoes = calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant=inimontant, fixir=fixir, inidate=inidate, findate=findate
  )
  total_increase = finalmontant - inimontant
  return total_increase, quinhoes


def calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant: Decimal, fixir: Decimal, inidate: datetime.date, findate: datetime.date
  ) -> tuple[Decimal, list[tuple[Decimal, datetime.date]]]:
  """
  Calculates final montant with parameters:
    1 initial montant,
    2 fix IR index,
    3 variable IR index (which must be fetched),
    4 initial date,
    5 final date

  Before commenting the hypothesis where dates cross over more than one month,
    this function just does:
      1 fetches the variable IR index and
      2 sums up the two indices: the fixed one and the variable one forming 'ir_idx'
      3 then dispatches to the function above the does the calculation with 'ir_idx'.

  When more than one month is involved
  ====================================

  If only one month is involved, dispatch will happen to the function mentioned above.
  If more than one month is involved, dispatch will happen to a monthpartition function.

  """
  # duration may be partitioned
  inidate = dtfs.make_date_or_raise(inidate)
  findate = dtfs.make_date_or_raise(findate)
  if (inidate.year, inidate.month) == (findate.year, findate.month):
    # same month case
    # 1 find ipca
    # 2 sums up fix_ir and ipca to ir_idx
    # 3 then dispatches execution to the function that uses 'ir_idx'
    ipcacacher = ipcafs.IpcaAPICacherRetriever()
    refmonth = rmfs.make_refmonth_or_raise(inidate)
    ipcadec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(refmonth, 2)
    ipcadec = DECIMAL_ZERO if ipcadec is None else ipcadec
    ir_idx = fixir + ipcadec
    return calc_finalmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=inimontant,
      ir_idx=ir_idx,
      inidate=inidate,
      findate=findate,
    )
  # from this point on, there are more than one month | many months case
  # 1 find ipca's
  # 2 list-sums up fix_ir and ipca to ir_idx
  # 3 then dispatches execution to the function that uses 'ir_idx_list' and monthpartition
  ipcacacher = ipcafs.IpcaAPICacherRetriever()
  iridxlist = []
  for refmonth in rmfs.generate_monthrange(inidate, findate):
    ipcadec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(refmonth, 2)
    ipcadec = DECIMAL_ZERO if ipcadec is None else ipcadec
    ir_idx = fixir + ipcadec
    iridxlist.append(ir_idx)
  partitionmonths = rmfs.mk_partition_inidate_findate_as_ndays_n_refms_tlist(inidate, findate)
  return calc_finalmontant_w_1inimontant_2iridxlist_3partitionmonths(
    inimontant=inimontant,
    iridxlist=iridxlist,
    monthpartition=partitionmonths
  )


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
