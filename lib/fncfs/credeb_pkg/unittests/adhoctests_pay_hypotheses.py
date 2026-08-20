"""

"""
import datetime
from decimal import Decimal
import lib.fncfs.credeb_pkg.pay_dt_val_interface as pinterf  # pay.process_payments_in_month
import lib.fncfs.credeb_pkg.payment_processor as pay  # pay.process_payments_in_month
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.credeb_pkg.credit_debt_fs as cdfs  # cdfs.debit_value_to_accounts
from lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal import \
  calc_finmontant_w_1inimontant_2iridxlist_3monthpartition, \
  calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth

DECIMAL_ZERO = Decimal(0)


def paywindow_postexplain2(
    postpay_tupl: tuple, payments: list,
    duedate: datetime.date, inimonthsdebt: Decimal,
    ir_idx: Decimal,
):
  since = datetime.date(duedate.year, duedate.month, 1)
  lastdaydate = rmfs.make_lastmonthsday_date(duedate)
  cre, deb, ndays_n_value_lst = postpay_tupl
  msgtext = f'Valor a pagar: {inimonthsdebt} -> na janela entre {since} e {duedate}'
  lines = [msgtext]
  if len(payments) == 0:
    return 'no payments'
  intime_payments = [p for p in payments if p.date <= duedate]
  tardy_payments = [p for p in payments if p.date > duedate]
  for payment in intime_payments:
    pdate, payvalue = payment.date, payment.value
    line = f'\tem {pdate} |'
    cre, inimonthsdebt = cdfs.credit_value_to_accounts(
      value=payvalue,
      cre_account=DECIMAL_ZERO,
      deb_account=inimonthsdebt
    )
    line += f' pagos {payvalue:.2f} sem mora remanescendo {inimonthsdebt:.2f}'
    lines.append(line)
  for payment in tardy_payments:
    pdate, payvalue = payment.date, payment.value
    inimonthsdebt_before = inimonthsdebt
    inimonthsdebt, _ = calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=inimonthsdebt,
      ir_idx=ir_idx,
      inidate=since,
      findate=pdate,

    )
    inimonthsdebt_before = inimonthsdebt
    cre, inimonthsdebt = cdfs.credit_value_to_accounts(
      value=payvalue,
      cre_account=DECIMAL_ZERO,
      deb_account=inimonthsdebt
    )
    ndays_n_value_lst_cp = ndays_n_value_lst[:]
    if len(ndays_n_value_lst_cp) > 0:
      ndays, value = ndays_n_value_lst_cp.pop(0)
      line = f'\tem {pdate} | dos atualizados {inimonthsdebt_before:.2f} ({ndays} dias) pagos {payvalue:.2f} '
      line += f'remanescendo {value:.2f}'
    lines.append(line)
    line = ''
    while len(ndays_n_value_lst_cp) > 0:
      ndays, value = ndays_n_value_lst_cp.pop(0)
      inimonthsdebt -= value
      line += f'\tem {lastdaydate} | dos atualizados {inimonthsdebt:.2f} (por {ndays} dias) mora: {value:.2f}'
    line += '\n'
    lines.append(line)
  msgtext = '\n'.join(lines)
  return msgtext


def paywindow_postexplain(
    postpay_tupl, payments, duedate
  ):
  cre, deb, amounts = postpay_tupl
  scrmsg = f"Apuração:\n"
  payvalue_lst = [p.value for p in payments]
  total_paid = sum(payvalue_lst)
  scrmsg += f"total_paid={total_paid} | cre={cre} | deb={deb}, amounts={amounts}"
  tardypayments = [p for p in payments if p.date > duedate]
  for ndays_n_value in amounts:
    ndays, value = ndays_n_value
    scrmsg += f'\n\t amt={value:.2f} with {ndays} days'
  for tardypayment in tardypayments:
    t = tardypayment
    scrmsg += f'\n\t payvalue={t.value:.2f} on {t.date}'
  return scrmsg


def hypothesis8():
  pass


def hypothesis7():
  pass


def hypothesis6():
  pass


def hypothesis5():
  # hypothesis 5: paying twice, one in due time, one tardy
  hypstr = "# hypothesis 5: paying twice, one in due time, one tardy"
  valor_a_pagar_como_debito = Decimal(-2000)
  a_pg_deb = valor_a_pagar_como_debito
  duedate = datetime.date(2026, 4, 10)
  paydate1 = duedate
  payment_1 = pinterf.PaymentInterfaceDateNValue(
    date=paydate1, value=Decimal(1000),
  )
  paydate2 = datetime.date(2026, 4, 21)
  payment_2 = pinterf.PaymentInterfaceDateNValue(
    date=paydate2, value=Decimal(1000),
  )
  payments = [payment_1, payment_2]
  retrodate_ifinmora = datetime.date(2026, 4, 1)
  postdate_ifinmora = datetime.date(2026, 4, 30)
  fix_plus_var_ir_dec = Decimal(0.025)
  postpay_tupl = pinterf.process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    retrodate_ifinmora=retrodate_ifinmora,
    postdate_ifinmora=postdate_ifinmora,
    fix_plus_var_ir_dec=fix_plus_var_ir_dec,
  )
  print(hypstr)
  scrmsg = paywindow_postexplain2(
    postpay_tupl=postpay_tupl, payments=payments, duedate=duedate,
    inimonthsdebt=a_pg_deb, ir_idx=fix_plus_var_ir_dec,
  )
  print(scrmsg)


def hypothesis4():
  # hypothesis 4: paying twice less than due, twice in time, once tardy
  hypstr = "# hypothesis 4: paying twice less than due, twice in time, once tardy"
  valor_a_pagar_como_debito = Decimal(-2000)
  duedate = datetime.date(2026, 4, 10)
  payment_1 = pinterf.PaymentInterfaceDateNValue(
    date=duedate, value=Decimal(2000),
  )
  retrodate_ifinmora = datetime.date(2026, 4, 1)
  postdate_ifinmora = datetime.date(2026, 4, 30)
  fix_plus_var_ir_dec = Decimal(0.025)
  tupl_dec_dec_list = pinterf.process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=[payment_1],
    duedate=duedate,
    retrodate_ifinmora=retrodate_ifinmora,
    postdate_ifinmora=postdate_ifinmora,
    fix_plus_var_ir_dec=fix_plus_var_ir_dec,
  )
  print(hypstr)
  v_paid = f"{payment_1.value:.2f}"
  v_a_pg = f"{valor_a_pagar_como_debito:.2f}"
  scrmsg = f"deb={v_a_pg} pgt={v_paid} | res={tupl_dec_dec_list}"
  print(scrmsg)


def hypothesis3():
  # hypothesis 3: paying once: less than due and tardy
  hypstr = "# hypothesis 3: paying once: less than due and tardy"
  valor_a_pagar_como_debito = Decimal(-2000)
  duedate = datetime.date(2026, 4, 10)
  paydate = datetime.date(2026, 4, 11)
  payment_1 = pinterf.PaymentInterfaceDateNValue(
    date=paydate, value=Decimal(1000),
  )
  retrodate_ifinmora = datetime.date(2026, 4, 1)
  postdate_ifinmora = datetime.date(2026, 4, 30)
  fix_plus_var_ir_dec = Decimal(0.025)
  tupl_dec_dec_list = pinterf.process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=[payment_1],
    duedate=duedate,
    retrodate_ifinmora=retrodate_ifinmora,
    postdate_ifinmora=postdate_ifinmora,
    fix_plus_var_ir_dec=fix_plus_var_ir_dec,
  )
  print(hypstr)
  v_paid = f"{payment_1.value:.2f}"
  v_a_pg = f"{valor_a_pagar_como_debito:.2f}"
  scrmsg = f"deb={v_a_pg} pgt={v_paid} on {paydate} | res={tupl_dec_dec_list}"
  print(scrmsg)


def hypothesis2():
  # hypothesis 2: paying once: less than due and in/on time
  hypstr = "# hypothesis 2: paying once: less than due and in/on time"
  valor_a_pagar_como_debito = Decimal(-2000)
  duedate = datetime.date(2026, 4, 10)
  payment_1 = pinterf.PaymentInterfaceDateNValue(
    date=duedate, value=Decimal(1000),
  )
  retrodate_ifinmora = datetime.date(2026, 4, 1)
  postdate_ifinmora = datetime.date(2026, 4, 30)
  fix_plus_var_ir_dec = Decimal(0.025)
  tupl_dec_dec_list = pinterf.process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=[payment_1],
    duedate=duedate,
    retrodate_ifinmora=retrodate_ifinmora,
    postdate_ifinmora=postdate_ifinmora,
    fix_plus_var_ir_dec=fix_plus_var_ir_dec,
  )
  print(hypstr)
  v_paid = f"{payment_1.value:.2f}"
  v_a_pg = f"{valor_a_pagar_como_debito:.2f}"
  scrmsg = f"deb={v_a_pg} pgt={v_paid} | res={tupl_dec_dec_list}"
  print(scrmsg)


def hypothesis1():
  # hypothesis 1: paying correctly in/on time
  hypstr = "# hypothesis 1: paying correctly in/on time"
  valor_a_pagar_como_debito = Decimal(-2000)
  duedate = datetime.date(2026, 4, 10)
  paydate = duedate
  payment_1 = pinterf.PaymentInterfaceDateNValue(
    date=paydate, value=Decimal(2000),
  )
  retrodate_ifinmora = datetime.date(2026, 4, 1)
  postdate_ifinmora = datetime.date(2026, 4, 30)
  fix_plus_var_ir_dec = Decimal(0.025)
  payproc = pay.PaymentProcessor(

  )
  tupl_dec_dec_list = pay.process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=[payment_1],
    duedate=duedate,
    retrodate_ifinmora=retrodate_ifinmora,
    postdate_ifinmora=postdate_ifinmora,
    fix_plus_var_ir_dec=fix_plus_var_ir_dec,
  )
  print(hypstr)
  v_paid = f"{payment_1.value:.2f}"
  v_a_pg = f"{valor_a_pagar_como_debito:.2f}"
  scrmsg = f"deb={v_a_pg} pgt={v_paid} on {paydate} | res={tupl_dec_dec_list}"
  print(scrmsg)


def adhoctest1():
  # hypothesis 1: paying correctly in/on time
  # hypothesis 2: paying once: less than due and in/on time
  # hypothesis 3: paying once: less than due and tardy
  # hypothesis 4: paying twice less than due, twice in time, once tardy
  # hypothesis 5: paying twice, one in due time, one tardy
  # hypothesis 6: paying twice, twice tardy
  # hypothesis 7: paying nothing (to check/verify back mora)
  # hypothesis 8: paying once in/on time leaving credit
  hypothesis1()
  hypothesis2()
  hypothesis3()
  hypothesis4()
  hypothesis5()
  hypothesis6()
  hypothesis7()
  hypothesis8()




adhoctest1()