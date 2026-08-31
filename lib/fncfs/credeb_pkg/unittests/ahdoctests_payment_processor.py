"""
lib/fncfs/credeb_pkg/unittests/ahdoctests_payment_processor.py
  Contains adhoctests for:
    paypro.PaymentProcessor
    lib.fncfs.credeb_pkg.payment_processor as paypro  # paypro.PaymentProcessor

"""
import datetime
from decimal import Decimal, Context, ROUND_HALF_UP
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.credeb_pkg.payment_processor as pay  # pay.process_payments_in_month
import lib.fncfs.credeb_pkg.payment_processor as paypro  # paypro.PaymentProcessor
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcam  # ipcam.IpcaAPICacherRetriever
# fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fnmts
from lib.fncfs.indices.ipca.ipca_fetcher_cacher import IpcaAPICacherRetriever
mkdt = dtfs.make_date_or_raise
fetch_iridx_n_ipca_m_plus_1_w_refmonth_n_fix = ipcam.fetch_iridx_n_ipca_m_plus_i_w_refmonth_n_fix



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
  credito, debito, quinhoes = payprocessor.cre_deb_moras_after_process
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
  credito, debito, quinhoes = payprocessor.cre_deb_moras_after_process
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
  credito, debito, monthmoras = payprocessor.cre_deb_moras_after_process
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


def adhoctest4():
  inidate = mkdt('2026-04-01')
  findate = mkdt('2026-04-30')
  ipcacacher = ipcam.IpcaAPICacherRetriever()
  ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(inidate, 2)
  refminus2 = rmfs.calc_refmonth_minus_n(inidate, 2)
  scrmsg = f"refmonth={inidate} M-2 {refminus2} | ipca_dec: {ipca_dec:.4f}"
  print(scrmsg)
  ir_idx = Decimal(0.02) + ipca_dec
  moravalue = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant=Decimal(-1000),
    ir_idx=ir_idx,
    inidate=inidate,
    findate=findate,
  )
  scrmsg = f"moravalue' {moravalue:.4f}"
  print(scrmsg)
  monthdebtvalue = Decimal(-2000)
  duedate = datetime.date(2026, 4, 10)
  pprocessor = pay.PaymentProcessor(
    ongoing_debt=monthdebtvalue,
    duedate=duedate,
    fix_ir_dec=Decimal(0.02),
  )
  payment_1 = intrfc.PaymentInterfaceDateNValue(
    date=duedate, value=Decimal(1000),
  )
  pprocessor.payments = [payment_1]
  pprocessor.process()
  cre_deb_moras_after_process = pprocessor.cre_deb_moras_after_process
  print('cre_deb_moras_after_process', cre_deb_moras_after_process)
  print(pprocessor)
  print(pprocessor.monthmoras[0])


def adhoctest5():
  inidate = mkdt('2026-04-01')
  findate = mkdt('2026-04-30')
  ipcacacher = ipcam.IpcaAPICacherRetriever()
  ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(inidate, 2)
  refminus2 = rmfs.calc_refmonth_minus_n(inidate, 2)
  scrmsg = f"refmonth={inidate} M-2 {refminus2} | ipca_dec: {ipca_dec:.4f}"
  print(scrmsg)
  ir_idx = Decimal(0.02) + ipca_dec
  moravalue = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant=Decimal(-1000),
    ir_idx=ir_idx,
    inidate=inidate,
    findate=findate,
  )
  scrmsg = f"moravalue' {moravalue:.4f}"
  print(scrmsg)
  monthdebtvalue = Decimal(-2000)
  duedate = datetime.date(2026, 4, 10)
  pprocessor = pay.PaymentProcessor(
    ongoing_debt=monthdebtvalue,
    duedate=duedate,
    fix_ir_dec=Decimal(0.02),
  )
  paydate = mkdt('2026-04-20')
  payment_1 = intrfc.PaymentInterfaceDateNValue(
    date=paydate, value=Decimal(1000),
  )
  pprocessor.payments = [payment_1]
  pprocessor.process()
  cre_deb_moras_after_process = pprocessor.cre_deb_moras_after_process
  print('cre_deb_moras_after_process', cre_deb_moras_after_process)
  print(pprocessor)
  for mmora in pprocessor.monthmoras:
    print(mmora)


def adhoctest6():
  paymonthstr = '2025-4'
  inidate, findate = mkdt(f'{paymonthstr}-1'), mkdt(f'{paymonthstr}-30')
  duedate, paydate1, paydate2 = mkdt(f'{paymonthstr}-10'), mkdt(f'{paymonthstr}-5'), mkdt(f'{paymonthstr}-23')
  payvalue1, payvalue2 = Decimal(950), Decimal(1250)
  payment1 = intrfc.PaymentInterfaceDateNValue(
    date=paydate1, value=payvalue1,
  )
  payment2 = intrfc.PaymentInterfaceDateNValue(
    date=paydate2, value=payvalue2,
  )
  monthdebtvalue = Decimal(-2000)
  pprocessor = pay.PaymentProcessor(
    ongoing_debt=monthdebtvalue,
    duedate=duedate,
    fix_ir_dec=Decimal(0.02),
  )
  pprocessor.payments = [payment1, payment2]
  pprocessor.process()
  fix_ir_dec = Decimal(0.02)
  # refmonth is the previous (penultimate, one but last) month from paymonth
  refmonth = rmfs.make_refmonth_it_minus_n_or_raise(paymonthstr, 1)
  ir_idx, ipca_dec = fetch_iridx_n_ipca_m_plus_1_w_refmonth_n_fix(
    refmonth=refmonth, p_fix_ir_dec=fix_ir_dec
  )
  exp_inimontant_1 = monthdebtvalue + payvalue1
  print('payment1', payment1, ' | payment2', payment2)
  scrmg = f"fix_ir_dec={fix_ir_dec:.4f} | ipca={ipca_dec:.4f} | ir_idx={ir_idx:.4f}"
  print(scrmg)
  print('exp_inimontant_1', exp_inimontant_1)
  exp_moravalue1 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant=exp_inimontant_1,
    ir_idx=ir_idx,
    inidate=inidate,
    findate=paydate2,
  )
  exp_credit = monthdebtvalue + payvalue1 + payvalue2 + exp_moravalue1
  ret_credit, ret_debt, monthmoras = pprocessor.cre_deb_moras_after_process
  exp_credit = monthdebtvalue + payvalue1 + payvalue2 + exp_moravalue1
  print('exp_credit', exp_credit, 'exp_moravalue1', exp_moravalue1)
  print('ret_credit, ret_debt, monthmoras', ret_credit, ret_debt, monthmoras)
  for mmora in pprocessor.monthmoras:
    print(mmora)


def adhoctest15():
  inidate = mkdt('2026-04-01')
  findate = mkdt('2026-04-30')
  ipcacacher = ipcam.IpcaAPICacherRetriever()
  ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(inidate, 2)
  print(inidate, ipca_dec)


def process():
  pass


if __name__ == "__main__":
  """
  process()
  # adhoctest1()
  # adhoctest2()
  """
  adhoctest6()
