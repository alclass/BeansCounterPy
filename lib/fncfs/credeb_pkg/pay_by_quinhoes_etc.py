"""
lib/fncfs/credeb_pkg/pay_by_quinhoes_etc.py
  Contains functions that pay a debt directly or by "quinhões"
    (i.e., peacemealwise when monthly mora is partitioned, i.e., it happens across more than one month)
"""
from decimal import Decimal, Context, ROUND_HALF_UP
import decimal
import datetime
from dataclasses import dataclass
import lib.datesetc.datefs as dtfs
import lib.fncfs.credeb_pkg.credit_debit_fs as cdfs  # cdfs.debit_value_to_accounts
# for fncfs.calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate
import lib.fncfs.fncmathfs.finance_math_fs as fncfs
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


def pay_by_quinhao_considering_mora(
    debito_em_mora: Decimal,
    p_payments: list[PaymentInterfaceDateNValue],  # we'll only need date and value from a payment object
    duedate: datetime.date,
    monthly_fix_ir_dec: Decimal  # the variable parcel, if mora happens, is fetched 'downstream'
  ) -> tuple[decimal.Decimal, decimal.Decimal]:
  if debito_em_mora > DECIMAL_ZERO:
    errmsg = f"Error: debito_em_mora (={debito_em_mora}) cannot be greater than zero"
    raise ValueError(errmsg)
  debito, credito = debito_em_mora, DECIMAL_ZERO
  payments = p_payments[:]  # copy it
  while len(payments) > 0:
    payment = payments.pop(0)
    payvalue = payment.value
    paydate = payment.date
    inimontant = -debito
    if inimontant > DECIMAL_ZERO:
      mora_incr = fncfs.calc_increase_w_1inimontant_2fixir_fetchipca_3inidate_4findate(
        inimontant, monthly_fix_ir_dec, duedate, paydate
      )
      debito = debito - mora_incr
      debito = debito + payvalue  # notice pay is positive, debito is negative
      if debito > DECIMAL_ZERO:
        # debito has been paid
        credito += debito
        debito = DECIMAL_ZERO
        break
      # from here loop on
    else:  # debito has been paid
      credito += payvalue
      break
  # sums up any missing payments yet
  payvalues = [p.value for p in payments]
  # cred_remaining = functools.reduce(lambda x, y: x + y, payvalues, DECIMAL_ZERO)
  cred_remaining = sum(payvalues)
  credito += cred_remaining
  return credito, debito


def process_payments(
    valor_a_pagar_como_debito: Decimal,
    payments: list[PaymentInterfaceDateNValue],  # we'll only need date and value from a payment object
    duedate: datetime.date,
    monthly_fix_ir_dec: Decimal  # the variable parcel, if mora happens, is fetched 'downstream'
  ) -> tuple[decimal.Decimal, decimal.Decimal]:
  """
  This function receives a debt value and a list of payments.
  It outputs two values: credito_no_fecho, debito_no_fecho
    credito_no_fecho is an excedent out of the payments
    debito_no_fecho signals that the payment was not completed
  This function uses a 'subsystem' that does the credit/debit calculation.
  """
  debtvalue = valor_a_pagar_como_debito
  if debtvalue > DECIMAL_ZERO:
    errmsg = f"Error: debt (={debtvalue}) cannot be greater than DECIMAL_ZERO"
    raise ValueError(errmsg)
  if len(payments) == 0:
    return DECIMAL_ZERO, debtvalue
  payments_ondate = list(filter(lambda po: po.date <= duedate, payments))
  payvalues = [p.value for p in payments_ondate]
  # we used sum() instead of reduce() (below)
  # cred_account = functools.reduce(lambda x, y: x + y, payvalues, DECIMAL_ZERO)
  cred_account = sum(payvalues)
  credito_no_fecho, debito_no_fecho = cdfs.debit_value_to_accounts(debtvalue, cred_account, DECIMAL_ZERO)
  credito_no_fecho = DECIMAL_ZERO if credito_no_fecho is None else credito_no_fecho
  debito_no_fecho = DECIMAL_ZERO if debito_no_fecho is None else debito_no_fecho
  payments_outdate = list(filter(lambda po: po.date > duedate, payments))
  if len(payments_outdate) == 0:
    return credito_no_fecho, debito_no_fecho
  if credito_no_fecho > DECIMAL_ZERO:
    # notice that credito is always positive, debito is always negative
    # if one of them has value, the other must be zeroed
    return credito_no_fecho, debito_no_fecho
  # now the following condition holds: there are payments done out of duedate
  laterpayvalues = [p.value for p in payments_outdate]
  # later_cred_account = functools.reduce(lambda x, y: x + y, laterpayvalues, DECIMAL_ZERO)
  later_cred_account = sum(laterpayvalues)
  # then let's check if debito == 0, if so, payments go to credit
  if debito_no_fecho == DECIMAL_ZERO:
    credito_no_fecho += later_cred_account
    return credito_no_fecho, debito_no_fecho
  # now it's the most 'difficult' part because it involves 'mora'
  if not debito_no_fecho < DECIMAL_ZERO:
    errmsg = f"debito_no_fecho ({debito_no_fecho}) is not < DECIMAL_ZERO"
    raise ValueError(errmsg)
  debito_ainda = debito_no_fecho
  return pay_by_quinhao_considering_mora(
    debito_ainda, payments_outdate, duedate, monthly_fix_ir_dec
  )  # returns credito_no_fecho, debito_no_fecho


  for payment in payments:
    if payment.date <= self.duedate:
      total_debito += payment.value
  return credito_no_fecho, debito_no_fecho


def adhoctest1():
  mkdt = dtfs.make_date_or_raise
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  payments = []
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(1200))
  payments.append(payment)
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-20'), value=Decimal(900))
  payments.append(payment)
  duedate = mkdt('2026-4-10')
  monthly_fix_ir_dec = Decimal(0.02)
  credito, debito = process_payments(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    monthly_fix_ir_dec=monthly_fix_ir_dec
  )
  scrmsg = f"""
  Input:
    payments = {payments}
    duedate = {duedate}
    monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
  Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)
  # 2
  mkdt = dtfs.make_date_or_raise
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  payments = []
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-08'), value=Decimal(1000))
  payments.append(payment)
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(1000))
  payments.append(payment)
  duedate = mkdt('2026-4-10')
  monthly_fix_ir_dec = Decimal(0.02)
  credito, debito = process_payments(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    monthly_fix_ir_dec=monthly_fix_ir_dec
  )
  scrmsg = f"""
  Input:
    payments = {payments}
    duedate = {duedate}
    monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
  Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)
  # 3
  mkdt = dtfs.make_date_or_raise
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  payments = []
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-08'), value=Decimal(1000))
  payments.append(payment)
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(900))
  payments.append(payment)
  duedate = mkdt('2026-4-10')
  monthly_fix_ir_dec = Decimal(0.02)
  credito, debito = process_payments(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    monthly_fix_ir_dec=monthly_fix_ir_dec
  )
  scrmsg = f"""
  Input:
    payments = {payments}
    duedate = {duedate}
    monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
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
