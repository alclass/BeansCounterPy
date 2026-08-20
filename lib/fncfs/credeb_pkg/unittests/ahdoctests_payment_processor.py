"""
lib/fncfs/credeb_pkg/unittests/ahdoctests_payment_processor.py
  Contains adhoctests for:
    paypro.PaymentProcessor
    lib.fncfs.credeb_pkg.payment_processor as paypro  # paypro.PaymentProcessor

"""
from decimal import Decimal, Context, ROUND_HALF_UP
import lib.datesetc.datefs as dtfs
import lib.fncfs.credeb_pkg.payment_processor as paypro  # paypro.PaymentProcessor
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue


def adhoctest1():
  """
  In the adhoctests below, ipca is not used, only the fix_ir_dec (=0.02).
  """
  mkdt = dtfs.make_date_or_raise
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  ongoingdebt = valor_a_pagar_como_debito
  payments = []
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(1200))
  payments.append(payment)
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-20'), value=Decimal(900))
  payments.append(payment)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  retrodate = mkdt('2026-4-1')
  postdate = mkdt('2026-4-30')
  monthly_fix_ir_dec = Decimal(0.02)
  payprocessor = paypro.PaymentProcessor(
    ongoing_debt=ongoingdebt,
    duedate=duedate,
    fix_ir_dec=monthly_fix_ir_dec,
    has_ipca=True,
  )
  payprocessor.payments = payments
  payprocessor.process_payments_in_month()
  credito, debito, quinhoes = payprocessor.cre_deb_moras_tuple
  debito = payprocessor.ongoing_debt
  credito = payprocessor.ongoing_credit
  monthmoras = payprocessor.monthmoras
  scrmsg = f"""Example:
    Input: debt = {ongoingdebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {payprocessor.monthmoras} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)
  for monthmora in monthmoras:
    print(monthmora)


def adhoctest2():
  """

  """
  # 2
  mkdt = dtfs.make_date_or_raise
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  ongoingdebt = valor_a_pagar_como_debito
  payments = []
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-08'), value=Decimal(1000))
  payments.append(payment)
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(1000))
  payments.append(payment)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  monthly_fix_ir_dec = Decimal(0.02)
  payprocessor = paypro.PaymentProcessor(
    ongoing_debt=ongoingdebt,
    duedate=duedate,
    fix_ir_dec=monthly_fix_ir_dec,
    has_ipca=True,
  )
  payprocessor.payments = payments
  payprocessor.process_payments_in_month()
  credito, debito, quinhoes = payprocessor.cre_deb_moras_tuple
  scrmsg = f"""Example:
    Input: debt = {ongoingdebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {quinhoes} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)


def adhoctest3():
  # 3
  mkdt = dtfs.make_date_or_raise
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  ongoingdebt = valor_a_pagar_como_debito
  payments = []
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-18'), value=Decimal(1000))
  payments.append(payment)
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-25'), value=Decimal(900))
  payments.append(payment)
  payvalues = [p.value for p in payments]
  # total_payvalue = sum(payvalues)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  duedate = mkdt('2026-4-10')
  monthly_fix_ir_dec = Decimal(0.02)
  payprocessor = paypro.PaymentProcessor(
    ongoing_debt=ongoingdebt,
    duedate=duedate,
    fix_ir_dec=monthly_fix_ir_dec,
    has_ipca=True,
  )
  payprocessor.payments = payments
  payprocessor.process_payments_in_month()
  credito, debito, monthmoras = payprocessor.cre_deb_moras_tuple
  scrmsg = f"""Example:
    Input: debt = {ongoingdebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {payprocessor.monthmoras} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)
  for monthmora in monthmoras:
    print(monthmora)
  text = payprocessor.history_backtrack()
  print(text)

def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  # adhoctest1()
  # adhoctest2()
  adhoctest3()
