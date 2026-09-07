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
import art.immeub.rent.billmodels.payment_pydant as bipydtc  # bipydtc.PydtcPayment
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcam  # ipcam.IpcaAPICacherRetriever
# fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fnmts
mkdt = dtfs.make_date_or_raise
fetch_iridx_n_ipca_m_plus_1_w_refmonth_n_fix = ipcam.fetch_iridx_n_ipca_m_minus_i_w_1refmonth_2fix_3mminusn
DECIMAL_ZERO = Decimal(0)



def adhoctest1():
  """
  # 1
  hypothesis: fully paying, one parcel up to duedate, one after duedate, remaining credit
  """
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  ongoingdebt = valor_a_pagar_como_debito
  payments = []
  # noinspection argument-list
  payment = bipydtc.PydtcPayment(
    date=mkdt('2026-4-10'), value=Decimal(1200)
  )
  payments.append(payment)
  # noinspection argument-list
  payment = bipydtc.PydtcPayment(
    date=mkdt('2026-4-20'), value=Decimal(900)
  )
  payments.append(payment)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  # retrodate = mkdt('2026-4-1')
  # postdate = mkdt('2026-4-30')
  monthly_fix_ir_dec = Decimal(0.02)
  payprocessor = paypro.PaymentProcessor(
    ongoing_debt=ongoingdebt,
    duedate=duedate,
    fix_ir_dec=monthly_fix_ir_dec,
    has_ipca=True,
  )
  payprocessor.payments = payments
  payprocessor.process_payments_in_month()
  ret_credito, ret_debito, monthmoras = payprocessor.cre_deb_moras_after_process
  ret_credito = ret_credito if ret_credito is not None else DECIMAL_ZERO
  ret_debito = ret_debito if ret_debito is not None else DECIMAL_ZERO
  debito = payprocessor.ongoing_debt
  credito = payprocessor.ongoing_credit or DECIMAL_ZERO
  monthmoras = payprocessor.monthmoras
  scrmsg = f"""Example:
    Input: debt = {ongoingdebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {payprocessor.monthmoras} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {ret_credito:.2f}, {ret_debito:.2f} | {credito:.2f}, {debito:.2f}
  """
  print(scrmsg)
  for monthmora in monthmoras:
    print(monthmora)


def adhoctest2():
  """
  # 2
  hypothesis: fully paying up to duedate
  """
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  ongoingdebt = valor_a_pagar_como_debito
  payments = []
  # noinspection argument-list
  payment = bipydtc.PydtcPayment(
    date=mkdt('2026-4-8'), value=Decimal(1000)
  )
  payments.append(payment)
  # noinspection argument-list
  payment = bipydtc.PydtcPayment(
    date=mkdt('2026-4-10'), value=Decimal(1000)
  )
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
  # noinspection string-format
  scrmsg = f"""Example:
    Input: debt = {ongoingdebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {quinhoes} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)


def adhoctest3():
  """
  # 3
  hypothesis: paying less in two parcels, both after duedate, remaining debt
  """
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  ongoingdebt = valor_a_pagar_como_debito
  payments = []
  # noinspection argument-list
  payment = bipydtc.PydtcPayment(
    date=mkdt('2026-4-18'), value=Decimal(1000)
  )
  payments.append(payment)
  # noinspection argument-list
  payment = bipydtc.PydtcPayment(
    date=mkdt('2026-4-25'), value=Decimal(900)
  )
  payments.append(payment)
  # payvalues = [p.value for p in payments]
  # total_payvalue = sum(payvalues)
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
  ret_credito, ret_debito, monthmoras = payprocessor.cre_deb_moras_after_process
  ret_credito = ret_credito if ret_credito is not None else DECIMAL_ZERO
  ret_debito = ret_debito if ret_debito is not None else DECIMAL_ZERO
  # noinspection string-format
  scrmsg = f"""Example:
    Input: debt = {ongoingdebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {payprocessor.monthmoras} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {ret_credito:.2f}, {ret_debito:.2f} | {credito:.2f}, {debito:.2f}
  """
  print(scrmsg)
  monthmoras = monthmoras if monthmoras is not None else []
  for monthmora in monthmoras:
    print(monthmora)
  text = payprocessor.history_backtrack()
  print(text)


def adhoctest4():
  """
  # 4
  hypothesis: paying less in one parcel, up to duedate, remaining debt
  """

  inidate = mkdt('2026-04-01')
  findate = mkdt('2026-04-30')
  ipcacacher = ipcam.IpcaAPICacherRetriever()
  ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(inidate, 2)
  refminus2 = rmfs.calc_refmonth_minus_n(inidate, 2)
  # noinspection string-format
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
  # noinspection argument-list
  payment = bipydtc.PydtcPayment(
    date=duedate, value=Decimal(1000),
  )
  pprocessor.payments = [payment]
  pprocessor.process()
  cre_deb_moras_after_process = pprocessor.cre_deb_moras_after_process
  print('cre_deb_moras_after_process', cre_deb_moras_after_process)
  print(pprocessor)
  print(pprocessor.monthmoras[0])


def adhoctest5():
  """
  5
  hypothesis: paying less in one parcel, up to duedate, remaining debt
  """
  inidate = mkdt('2026-04-01')
  findate = mkdt('2026-04-30')
  ipcacacher = ipcam.IpcaAPICacherRetriever()
  ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(inidate, 2)
  refminus2 = rmfs.calc_refmonth_minus_n(inidate, 2)
  # noinspection string-format
  scrmsg = f"refmonth={inidate} M-2 {refminus2} | ipca_dec: {ipca_dec:.4f}"
  print(scrmsg)
  ir_idx = Decimal(0.02) + ipca_dec
  moravalue = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant=Decimal(-1000),
    ir_idx=ir_idx,
    inidate=inidate,
    findate=findate,
  )
  # noinspection string-format
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
  # noinspection argument-list
  payment = bipydtc.PydtcPayment(
    date=paydate, value=Decimal(1000)
  )
  pprocessor.payments = [payment]
  paydate = mkdt('2026-04-30')
  # noinspection argument-list
  payment = bipydtc.PydtcPayment(
    date=paydate, value=Decimal(1000)
  )
  pprocessor.payments.append(payment)
  pprocessor.process()
  print(pprocessor)
  credit_value, debt_value, monthmoras = pprocessor.cre_deb_moras_after_process
  monthmoras = monthmoras if monthmoras is not None else []
  for mmora in monthmoras:
    print(mmora)
  # noinspection string-format
  credit_value, debt_value = f"{credit_value:.2f}", f"{debt_value:.2f}"
  print('credit_value', credit_value, 'debt_value', debt_value)


def adhoctest6():
  paymonthstr = '2025-4'
  inidate, findate = mkdt(f'{paymonthstr}-1'), mkdt(f'{paymonthstr}-30')
  duedate, paydate1, paydate2 = mkdt(f'{paymonthstr}-10'), mkdt(f'{paymonthstr}-5'), mkdt(f'{paymonthstr}-23')
  payvalue1, payvalue2 = Decimal(950), Decimal(1250)
  # noinspection argument-list
  payment1 = bipydtc.PydtcPayment(
    date=paydate1, value=payvalue1,
  )
  # noinspection argument-list
  payment2 = bipydtc.PydtcPayment(
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
  # notice that 2 is M_MINUS_N
  refmonth = rmfs.make_refmonth_it_minus_n_or_raise(paymonthstr, m_minus_n=2)
  ir_idx, ipca_dec = fetch_iridx_n_ipca_m_plus_1_w_refmonth_n_fix(
    refmonth=refmonth, p_fix_ir_dec=fix_ir_dec
  )
  exp_inimontant_1 = monthdebtvalue + payvalue1
  print('payment1', payment1, ' | payment2', payment2)
  scrmg = f"fix_ir_dec={fix_ir_dec:.4f} | ipca={ipca_dec:.4f} | ir_idx={ir_idx:.4f}"
  print(scrmg)
  exp_moravalue1 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
    inimontant=exp_inimontant_1,
    ir_idx=ir_idx,
    inidate=inidate,
    findate=paydate2,
  )
  # noinspection string-format
  scrmg = f"exp_inimontant_1={exp_inimontant_1:.2f} | exp_moravalue1={exp_moravalue1:.2f}"
  print(scrmg)
  exp_credit = monthdebtvalue + payvalue1 + payvalue2 + exp_moravalue1
  exp_debt = DECIMAL_ZERO
  ret_credit, ret_debt, monthmoras = pprocessor.cre_deb_moras_after_process
  if monthmoras is None:
    errmsg = "Error: monthmoras is None."
    raise ValueError(errmsg)
  for mmora in monthmoras:
    print(mmora)
  # noinspection string-format
  scrmsg = f"exp_credit={exp_credit:.2f} | exp_debt={exp_debt:.2f}"
  print(scrmsg)
  # noinspection string-format
  scrmsg = f"ret_credit={ret_credit:.2f} | ret_debt={ret_debt:.2f}"
  print(scrmsg)


def adhoctest11():
  inidate = mkdt('2026-04-01')
  # findate = mkdt('2026-04-30')
  ipcacacher = ipcam.IpcaAPICacherRetriever()
  ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(inidate, 2)
  print(inidate, ipca_dec)


def process():
  pass


if __name__ == "__main__":
  """
  process()
  adhoctest1()
  adhoctest2()
  adhoctest3()
  adhoctest4()
  adhoctest5()
  adhoctest6()
  """
  adhoctest6()
