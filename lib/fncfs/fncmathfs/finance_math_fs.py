"""
lib/fncfs/fncmathfs/finance_math_fs.py

To import it:
  import lib.fncfs.fncmathfs.finance_math_fs as fncmath  # fncmath.calc_ir_incrfact_f_mora_w_idx_n_expo()
"""
from decimal import Decimal
import calendar
import datetime
import decimal
import lib.datesetc.datefs as dtfs  # for partition_inidate_findate_as_monthndays_tuplelist
import lib.datesetc.refmonth_fs as rmfs  # for partition_inidate_findate_as_monthndays_tuplelist
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcafs  # ipcafs.IpcaAPICacherRetriever
from lib.datesetc.refmonth_fs import make_refmonth_or_raise
DECIMAL_ZERO = Decimal('0.00')


def calc_ir_incrfact_f_mora_w_idx_n_expo(
    ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  """
  Returns the multiplier for the (mora) Interest Rate (ir) calculation
    based on an index (ir_idx) and an exponent

  The exponent here is independent on the duration time units (days, months, etc.),
    which might be anyone in the caller. Another function below wraps parameter 'monthduration',
    which then calls this with 'monthduration' as 'exponent'.

  Acronyms:
    ir -> interest rate
    ir idx -> interest rate index
    incrfactor -> interest rate multiplier for finding the 'incr' (increment factor)
  """
  try:
    ir_idx = Decimal(ir_idx)
    exponent = Decimal(exponent)
  except (ValueError, TypeError, decimal.InvalidOperation) as e:
    errmsg = f"acc index ({ir_idx}) and/or exponent ({exponent}) are invalid: {e}"
    raise ValueError(errmsg)
  intermediate = (1 + ir_idx) ** exponent
  multiplier = intermediate - 1
  return multiplier


def calc_finalmontant_w_1inimontant_2ir_3expo(
    inimontant: Decimal, ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  try:
    inimontant = Decimal(inimontant)
    ir_idx = Decimal(ir_idx)
    exponent = Decimal(exponent)
  except (ValueError, TypeError, decimal.InvalidOperation) as e:
    errmsg = f"acc index ({ir_idx}) and/or exponent ({exponent}) are invalid: {e}"
    raise ValueError(errmsg)
  increase = inimontant * calc_ir_incrfact_f_mora_w_idx_n_expo(ir_idx, exponent)
  finalmontant = inimontant + increase
  return finalmontant


def calc_finalmontant_w_1inimontant_2fixir_3varir_4monthduration(
    inimontant: Decimal, fixir: Decimal, varir: Decimal, monthduration: Decimal
  ) -> Decimal:
  ir_idx = Decimal(fixir + varir)
  return calc_finalmontant_w_1inimontant_2ir_3expo(
    inimontant=inimontant, ir_idx=ir_idx, exponent=monthduration
  )


def calc_finalmontant_w_1inimontant_2fixir_fetchipca_3partitionmonths(
    inimontant: Decimal, fixir: Decimal, partitionmonths: list[tuple[datetime.date, int]]
  ) -> Decimal:
  quinhoes = []
  current_montant = inimontant
  for refmonth_n_days in partitionmonths:
    refmonth, ndays = refmonth_n_days
    _, totaldaysinmonth = calendar.monthrange(refmonth.year, refmonth.month)
    monthduration = Decimal( ndays / totaldaysinmonth)
    ipcacacher = ipcafs.IpcaAPICacherRetriever()
    ipcadec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(refmonth, 2)
    ipcadec = DECIMAL_ZERO if ipcadec is None else ipcadec
    ongoing_montant = calc_finalmontant_w_1inimontant_2fixir_3varir_4monthduration(
      inimontant=current_montant,
      fixir=fixir,
      varir=ipcadec,
      monthduration=monthduration,
    )
    quinhao = ongoing_montant - current_montant
    quinhoes.append(quinhao)
    current_montant = ongoing_montant
    print('quinhão', quinhao, 'current_montant', current_montant)
  finalmontant = inimontant + sum(quinhoes)
  return finalmontant


def calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant: Decimal, fixir: Decimal, inidate: datetime.date, findate: datetime.date
  ) -> Decimal:
  # duration may be partitioned
  inidate = dtfs.make_date_or_raise(inidate)
  findate = dtfs.make_date_or_raise(findate)
  if (inidate.year, inidate.month) == (findate.year, findate.month):
    ndays = findate.day - inidate.day
    _, totaldaysinmonth = calendar.monthrange(inidate.year, inidate.month)
    monthduration = Decimal(ndays / totaldaysinmonth)
    ipcacacher = ipcafs.IpcaAPICacherRetriever()
    refmonth = make_refmonth_or_raise(inidate)
    ipcadec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(refmonth, 2)
    ipcadec = DECIMAL_ZERO if ipcadec is None else ipcadec
    return calc_finalmontant_w_1inimontant_2fixir_3varir_4monthduration(
      inimontant=inimontant,
      fixir=fixir,
      varir=ipcadec,
      monthduration=monthduration
    )
  partitionmonths = rmfs.partition_inidate_findate_as_monthndays_tuplelist(inidate, findate)
  return calc_finalmontant_w_1inimontant_2fixir_fetchipca_3partitionmonths(
    inimontant=inimontant,
    fixir=fixir,
    partitionmonths=partitionmonths
  )


def calc_increase_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant: Decimal, fixir: Decimal, inidate: datetime.date, findate: datetime.date
  ) -> Decimal:
  finalmontant = calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
    inimontant=inimontant, fixir=fixir, inidate=inidate, findate=findate
  )
  increase = finalmontant - inimontant
  return increase


def calc_incr_insamemonth_w_1inimontant_2fixplusvardec_3inidate_4findate(
    inimontant: Decimal, fixplusvardec: Decimal, inidate: datetime.date, findate: datetime.date
  ) -> Decimal:
  """
  Calculates the mora-increment on inimontant between two dates (inclusive),
    but an interest rate.

  This function pressuposes inidate and findate belong to the same month.
  (There are other functions in this module that can calculate it over various months.)

  In words, this function considers a monthly variable inflation rate,
    which 'comes inside' parameter fixplusvardec.
  So inidate and findate must be in the same month.
    If not, raise ValueError, for it would be inconsistent
      to have a monthly inflation rate applied to a different month.
  """
  inidate = dtfs.make_date_or_raise(inidate)
  findate = dtfs.make_date_or_raise(findate)
  if (inidate.year, inidate.month) != (findate.year, findate.month):
    errmsg = f"Error: inidate ({inidate}) and findate ({findate}) must be in the same month."
    raise ValueError(errmsg)
  # monthndays_tuplelist = monthduration = rmfs.partition_inidate_findate_as_monthndays_tuplelist(inidate, findate)
  _, ndaysinmonth = calendar.monthrange(inidate.year, inidate.month)
  ndays_elapsed = findate.day - inidate.day + 1
  monthsduration = Decimal(ndays_elapsed / ndaysinmonth)
  finalmontant = calc_finalmontant_w_1inimontant_2ir_3expo(
    inimontant=inimontant, ir_idx=fixplusvardec, exponent=monthsduration
  )
  increase = finalmontant - inimontant
  return increase


def adhoctest1():
  ir_idx, exponent = Decimal(.023), Decimal(2)
  multiplier = calc_ir_incrfact_f_mora_w_idx_n_expo(ir_idx, exponent)
  scrmsg = f"(float res) input: ir_idx={ir_idx:.04f}, exponent={exponent} | output multiplier={multiplier:.04f}"
  print(scrmsg)
  # ===============
  inimontant = Decimal(1000)
  finalmontant = calc_finalmontant_w_1inimontant_2ir_3expo(inimontant, ir_idx, exponent)
  scrmsg = f"(dec res) input: inimontant={inimontant}, ir_idx={ir_idx:.04f}, exponent={exponent} | output finalmontant={finalmontant:.04f}"
  print(scrmsg)
  # ===============
  fixir, varir, monthduration = Decimal(.02), Decimal(.0034), Decimal(2.5)
  finalmontant = calc_finalmontant_w_1inimontant_2fixir_3varir_4monthduration(inimontant, fixir, varir, monthduration)
  scrmsg = f""" Example:
  input:  initial montant={inimontant}, fix ir={fixir:.04f}, var ir={varir:.04f}, month duration={monthduration}
  output: final montant={finalmontant:.04f}"""
  print(scrmsg)
  # ===============


def adhoctest2():
  mkdt = dtfs.make_date_or_raise
  inidate, findate = mkdt('2026-1-5'), mkdt('2026-3-18')
  inimontant, fixir = Decimal(1000), Decimal(.02)
  finalmontant = calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
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
