"""
lib/fncfs/credeb_pkg/pay_by_quinhoes_etc.py
  Contains functions that pay a debt directly or by "quinhões"
    (i.e., peacemealwise when monthly mora is partitioned, i.e., it happens across more than one month)
"""
from decimal import Decimal, Context, ROUND_HALF_UP
import decimal
import datetime
from dataclasses import dataclass

from urllib3.util import retry

import lib.datesetc.datefs as dtfs
import lib.fncfs.credeb_pkg.credit_debit_fs as cdfs  # cdfs.debit_value_to_accounts
# for fncfs.calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants as fncfs
from lib.datesetc.datefs import inspect_n_get_sepchar_in_strdate

DECIMAL_ZERO = Decimal('0')


@dataclass
class PaymentInterfaceDateNValue:
  """
  This class is just to contain payment's date and value
  Clients will use it with obj.date and obj.value
  (It aims to simplify the two fields for objects coming from a Pydantic class with more attributes.)
  """
  date: datetime.date
  value: Decimal


def pay_monthsbill_by_quinhao_considering_mora(
    debito_em_mora: Decimal,
    p_payments: list[PaymentInterfaceDateNValue],  # we'll only need date and value from a payment object
    retrodate_ifinmora: datetime.date,
    postdate_ifinmora: datetime.date,
    fix_plus_var_ir_dec: Decimal  # the variable parcel, if mora happens, is fetched 'downstream'
  ) -> tuple[decimal.Decimal, decimal.Decimal, list[tuple[int, Decimal]]]:
  if debito_em_mora > DECIMAL_ZERO:
    errmsg = f"Error: debito_em_mora (={debito_em_mora}) cannot be greater than zero"
    raise ValueError(errmsg)
  elif debito_em_mora == DECIMAL_ZERO:
    return DECIMAL_ZERO, DECIMAL_ZERO, []
  # at this point: debito_em_mora < DECIMAL_ZERO
  debito, credito = debito_em_mora, DECIMAL_ZERO
  payments = p_payments[:]  # copy it
  quinhoes_days_vals = []
  while len(payments) > 0:
    payment = payments.pop(0)
    payvalue = payment.value
    paydate = payment.date
    inimontant = -debito
    if inimontant > DECIMAL_ZERO:
      mora_incr = fncfs.calc_incr_insamemonth_w_1inimontant_2fixplusvardec_3inidate_4findate(
        inimontant, fix_plus_var_ir_dec, retrodate_ifinmora, paydate
      )
      debito = debito - mora_incr
      ndays = paydate.day - retrodate_ifinmora.day + 1
      days_n_vals = (ndays, mora_incr)
      quinhoes_days_vals.append(days_n_vals)
      debito = debito + payvalue  # notice pay is positive, debito is negative
      if debito > DECIMAL_ZERO:
        # debito has been paid
        credito += debito
        debito = DECIMAL_ZERO
        break
    else:  # debito has been paid
      credito += payvalue
    # loop on if while condition is still true (more payments in queue)
  # loop is over, payments all considered
  # at this point, if debito may or may not yet exist
  # however, if it does, it must mora-increase from retrodate_ifinmora to postdate_ifinmora
  if debito < DECIMAL_ZERO:
    inimontant = -debito
    mora_incr = fncfs.calc_increase_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
      inimontant, fix_plus_var_ir_dec, retrodate_ifinmora, postdate_ifinmora
    )
    debito = debito - mora_incr
    ndays = postdate_ifinmora.day - retrodate_ifinmora.day + 1
    days_n_vals = (ndays, mora_incr)
    quinhoes_days_vals.append(days_n_vals)
  return credito, debito, quinhoes_days_vals


def process_payments_in_month(
    valor_a_pagar_como_debito: Decimal,
    payments: list[PaymentInterfaceDateNValue],  # we'll only need date and value from a payment object
    duedate: datetime.date,
    retrodate_ifinmora: datetime.date,
    postdate_ifinmora: datetime.date,
    fix_plus_var_ir_dec: Decimal  # the variable parcel, if mora happens, is fetched 'downstream'
  ) -> tuple[decimal.Decimal, decimal.Decimal, list[tuple[int, Decimal]]]:
  """
  This function receives a debt value and a list of payments.
  It outputs two values: credito_no_fecho, debito_no_fecho
    credito_no_fecho is an excedent out of the payments
    debito_no_fecho signals that the payment was not completed

  This function uses a 'subsystem' that does the credit/debit calculation.
  The 'process' respects duedate and outdated payments,
    on the latter 'mora' is incident.
  """
  debtvalue = valor_a_pagar_como_debito
  if debtvalue > DECIMAL_ZERO:
    errmsg = f"Error: debt (={debtvalue}) cannot be greater than DECIMAL_ZERO"
    raise ValueError(errmsg)
  if len(payments) == 0:
    # there is no payments
    return DECIMAL_ZERO, debtvalue, []
  payments_ondate = list(filter(lambda po: po.date <= duedate, payments))
  payvalues = [p.value for p in payments_ondate]
  cred_account = sum(payvalues)
  if not isinstance(cred_account, Decimal):
    cred_account = Decimal(cred_account)
  credito_no_fecho, debito_no_fecho = cdfs.debit_value_to_accounts(debtvalue, cred_account, DECIMAL_ZERO)
  credito_no_fecho = DECIMAL_ZERO if credito_no_fecho is None else credito_no_fecho
  debito_no_fecho = DECIMAL_ZERO if debito_no_fecho is None else debito_no_fecho
  payments_outdate = list(filter(lambda po: po.date > duedate, payments))
  if len(payments_outdate) == 0:
    # all payments were in duedate, but we still have to check debito_no_fecho
    quinhoes_days_vals = []
    if debito_no_fecho < DECIMAL_ZERO:
      # there should be a 'mora-projection' from retro to post date
      inimontant = -debito_no_fecho
      # mora_incr 'projects' this remaining debt to postdate
      mora_incr = fncfs.calc_incr_insamemonth_w_1inimontant_2fixplusvardec_3inidate_4findate(
        inimontant=inimontant,
        fixplusvardec=fix_plus_var_ir_dec,
        inidate=retrodate_ifinmora,
        findate=postdate_ifinmora,
      )
      # fill in 'quinhoes'
      ndays = postdate_ifinmora.day - retrodate_ifinmora.day + 1
      days_n_vals = (ndays, mora_incr)
      quinhoes_days_vals.append(days_n_vals)
      # udpates debito_no_fecho according to the 'projection' above
      debito_no_fecho = debito_no_fecho - mora_incr
    return credito_no_fecho, debito_no_fecho, quinhoes_days_vals
  if credito_no_fecho > DECIMAL_ZERO:
    # notice that credito is always positive, debito is always negative
    # if one of them has value, the other must be zeroed
    return credito_no_fecho, debito_no_fecho, []
  # now the following condition holds: there are payments done out of duedate
  laterpayvalues = [p.value for p in payments_outdate]
  later_cred_account = sum(laterpayvalues)
  # then let's check if debito == 0, if so, payments go to credit
  if debito_no_fecho == DECIMAL_ZERO:
    credito_no_fecho += later_cred_account
    return credito_no_fecho, debito_no_fecho, []
  # now it's the most 'difficult' part because it involves 'mora'
  if not debito_no_fecho < DECIMAL_ZERO:
    errmsg = f"debito_no_fecho ({debito_no_fecho}) is not < DECIMAL_ZERO"
    raise ValueError(errmsg)
  debito_ainda = debito_no_fecho
  return pay_monthsbill_by_quinhao_considering_mora(
    debito_em_mora=debito_ainda,
    p_payments=payments_outdate,
    retrodate_ifinmora=retrodate_ifinmora,
    postdate_ifinmora=postdate_ifinmora,
    fix_plus_var_ir_dec=fix_plus_var_ir_dec,
  )  # returns credito_no_fecho, debito_no_fecho, quinhoes_days_vals


def adhoctest1():
  """
  In the adhoctests below, ipca is not used, only the fix_ir_dec (=0.02).
  """
  mkdt = dtfs.make_date_or_raise
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  totaldebt = valor_a_pagar_como_debito
  payments = []
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(1200))
  payments.append(payment)
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-20'), value=Decimal(900))
  payments.append(payment)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  retrodate = mkdt('2026-4-1')
  postdate = mkdt('2026-4-30')
  monthly_fix_ir_dec = Decimal(0.02)
  credito, debito, quinhoes = process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    retrodate_ifinmora=retrodate,
    postdate_ifinmora=postdate,
    fix_plus_var_ir_dec=monthly_fix_ir_dec,
  )
  scrmsg = f"""Example:
    Input: debt = {totaldebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {quinhoes} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)
  # 2
  mkdt = dtfs.make_date_or_raise
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  totaldebt = valor_a_pagar_como_debito
  payments = []
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-08'), value=Decimal(1000))
  payments.append(payment)
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(1000))
  payments.append(payment)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  monthly_fix_ir_dec = Decimal(0.02)
  credito, debito, quinhoes = process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    retrodate_ifinmora=retrodate,
    postdate_ifinmora=postdate,
    fix_plus_var_ir_dec=monthly_fix_ir_dec
  )
  scrmsg = f"""Example:
    Input: debt = {totaldebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {quinhoes} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)
  # 3
  mkdt = dtfs.make_date_or_raise
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  totaldebt = valor_a_pagar_como_debito
  payments = []
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-08'), value=Decimal(1000))
  payments.append(payment)
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(900))
  payments.append(payment)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  monthly_fix_ir_dec = Decimal(0.02)
  credito, debito, quinhoes = process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    retrodate_ifinmora=retrodate,
    postdate_ifinmora=postdate,
    fix_plus_var_ir_dec=monthly_fix_ir_dec
  )
  scrmsg = f"""Example:
  Input: debt = {totaldebt} | payments = {payments} 
    duedate = {duedate} | pays issued: {billstotal} | quinhoes = {quinhoes} 
    monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f} ipca = 0.00
  Output: credito, debito = {credito:.2f}, {debito:.2f} 
"""
  print(scrmsg)


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
