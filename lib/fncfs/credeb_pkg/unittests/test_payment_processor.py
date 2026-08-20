"""

"""
from decimal import Decimal
import unittest
import datetime

from dateutil.relativedelta import relativedelta

import lib.datesetc.datefs as dtfs
import lib.fncfs.credeb_pkg.payment_processor as pay  # pay.process_payments_in_month
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcam  # ipcam.
# fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fnmts
from lib.fncfs.indices.ipca.ipca_fetcher_cacher import IpcaAPICacherRetriever
mkdt = dtfs.make_date_or_raise
DECIMAL_ZERO = Decimal(0)


class TestCase1(unittest.TestCase):
  """
  # hypothesis 1: paying correctly in/on time
  # hypothesis 2: paying once less than due but in time
  # hypothesis 3: paying once less but in tardy
  # hypothesis 4: paying twice less than due, twice in time, once tardy
  # hypothesis 5: paying twice, one in due time, one tardy
  # hypothesis 6: paying twice, twice tardy
  # hypothesis 7: paying nothing (to check/verify back mora)
  # hypothesis 8: paying once in/on time leaving credit
  # test_2 below will repeat this with more data
  """

  def test_1_paying_the_charged_amount(self):
    """
    hypothesis 1: paying total monthsdebt correctly up to duedate

    The numerical example:
      2a paydate <= duedate: e.g. 2026-04-10
      2a payvalue < duevalue e.g. 2000 (when monthsdebt = -2000)
    """
    monthdebtvalue = Decimal(-2000)
    duedate = datetime.date(2026, 4, 10)
    payment_1 = intrfc.PaymentInterfaceDateNValue(
      date=duedate, value=Decimal(2000),
    )
    fix_plus_var_ir_dec = Decimal(0.025)
    pprocessor = pay.PaymentProcessor(
      ongoing_debt=monthdebtvalue,
      duedate=duedate,
    )
    pprocessor.payments = [payment_1]
    pprocessor.process()
    # tuple[decimal.Decimal, decimal.Decimal, list[tuple[int, Decimal]]]
    postpay_tupl = pprocessor.cre_deb_moras_after_process
    cre, deb, monthmoras = postpay_tupl
    self.assertEqual(cre, DECIMAL_ZERO)
    self.assertEqual(deb, DECIMAL_ZERO)
    self.assertEqual(monthmoras, [])

  def test_2_paying_less(self):
    """
    hypothesis 2:
      2a paying once and up to duedate
      2b paying less than due-amount
    The numerical example:
      2a paydate <= duedate: e.g. 2026-04-10
      2a payvalue < duevalue e.g. 1000 (when monthsdebt = -2000)
    """
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
    inidate = mkdt('2026-04-01')
    findate = mkdt('2026-04-30')
    ipcacacher = ipcam.IpcaAPICacherRetriever()
    ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(inidate, 2)
    if ipca_dec is None:
      ir_idx = Decimal(0.02)
    else:
      ir_idx = Decimal(0.02) + ipca_dec
    moravalue = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=Decimal(-1000),
      ir_idx=ir_idx,
      inidate=inidate,
      findate=findate,
    )
    missing_sans_mora = monthdebtvalue + payment_1.value
    missing_avec_mora = missing_sans_mora + moravalue
    cre, deb, monthmoras = pprocessor.cre_deb_moras_after_process
    self.assertEqual(cre, DECIMAL_ZERO)
    monthmora = monthmoras[0]
    self.assertEqual(ipca_dec, monthmora.ipca_dec)
    self.assertEqual(deb, missing_avec_mora)
    self.assertEqual(len(monthmoras), 1)
    self.assertEqual(moravalue, monthmora.increase)
    # the 1000 missing is counted for the whole month (30 days)
    self.assertEqual(monthmora.moradays, 30)
    self.assertEqual(monthmora.prevalue, missing_sans_mora)
    self.assertEqual(monthmora.postvalue, missing_avec_mora)
    self.assertEqual(monthmora.ir_idx, ir_idx)

  def test_3_process_month_pays(self):
    """
    hypothesis 3
      3a paying once and after duedate
      3b paying less than due-amount

    The numerical example:
      3a paydate <= duedate: e.g. 2026-04-20
      3b payvalue < duevalue e.g. 1000 (when monthsdebt = -2000)

    """
    monthdebtvalue = Decimal(-2000)
    duedate = datetime.date(2026, 4, 10)
    pprocessor = pay.PaymentProcessor(
      ongoing_debt=monthdebtvalue,
      duedate=duedate,
      fix_ir_dec=Decimal(0.02),
    )
    paydate = mkdt('2026-04-20')
    payment_1 = intrfc.PaymentInterfaceDateNValue(
      date=duedate, value=Decimal(1000),
    )
    pprocessor.payments = [payment_1]
    pprocessor.process()
    inidate = mkdt('2026-04-01')
    findate = mkdt('2026-04-30')
    ipcacacher = ipcam.IpcaAPICacherRetriever()
    ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(inidate, 2)
    if ipca_dec is None:
      ir_idx = Decimal(0.02)
    else:
      ir_idx = Decimal(0.02) + ipca_dec
    moravalue1 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=Decimal(-2000),
      ir_idx=ir_idx,
      inidate=inidate,
      findate=paydate,
    )
    paydate_plus_1 = paydate + relativedelta(days=1)
    moravalue2 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=Decimal(-1000),
      ir_idx=ir_idx,
      inidate=paydate_plus_1,
      findate=findate,
    )
    the_2_mora = moravalue1 + moravalue2
    missing_avec_mora = monthdebtvalue + payment_1.value + the_2_mora
    cre, deb, monthmoras = pprocessor.cre_deb_moras_after_process
    self.assertEqual(cre, DECIMAL_ZERO)
    monthmora = monthmoras[0]
    self.assertEqual(ipca_dec, monthmora.ipca_dec)
    self.assertEqual(len(monthmoras), 2)
    # self.assertEqual(deb, missing_avec_mora)
    # self.assertEqual(moravalue, monthmora.increase)
    # # the 1000 missing is counted for the whole month (30 days)
    # self.assertEqual(monthmora.moradays, 30)
    # self.assertEqual(monthmora.prevalue, missing_sans_mora)
    # self.assertEqual(monthmora.postvalue, missing_avec_mora)
    # self.assertEqual(monthmora.ir_idx, ir_idx)

  def atest_3_process_month_pays(self):
    """
    hypotheses 5 and 6
    # hypothesis 5: paying twice, one in due time, one tardy
    # hypothesis 6: paying twice, twice tardy

    """
    # hypothesis 5: paying twice, one in due time, one tardy
    valor_a_pagar_como_debito = Decimal(-2000)
    duedate = datetime.date(2026, 4, 10)
    payment_1 = pay.PaymentInterfaceDateNValue(
      date=duedate, value=Decimal(1000),
    )
    retrodate_ifinmora = datetime.date(2026, 4, 1)
    postdate_ifinmora = datetime.date(2026, 4, 30)
    fix_plus_var_ir_dec = Decimal(0.025)
    # tuple[decimal.Decimal, decimal.Decimal, list[tuple[int, Decimal]]]
    postpay_tupl = pay.process_payments_in_month(
      valor_a_pagar_como_debito=valor_a_pagar_como_debito,
      payments=[payment_1],
      duedate=duedate,
      retrodate_ifinmora=retrodate_ifinmora,
      postdate_ifinmora=postdate_ifinmora,
      fix_plus_var_ir_dec=fix_plus_var_ir_dec,
    )
    cre, deb, ndays_n_amt = postpay_tupl
    self.assertEqual(cre, DECIMAL_ZERO)
    self.assertEqual(deb, DECIMAL_ZERO)
    self.assertEqual(ndays_n_amt, [])
    # hypothesis 2: paying once: less than due and in/on time
    valor_a_pagar_como_debito = Decimal(-2000)
    duedate = datetime.date(2026, 4, 10)
    payment_1 = pay.PaymentInterfaceDateNValue(
      date=duedate, value=Decimal(1000),
    )
    retrodate_ifinmora = datetime.date(2026, 4, 1)
    postdate_ifinmora = datetime.date(2026, 4, 30)
    fix_plus_var_ir_dec = Decimal(0.025)
    # tuple[decimal.Decimal, decimal.Decimal, list[tuple[int, Decimal]]]
    cre, deb, ndays_n_amt = postpay_tupl
    self.assertEqual(cre, DECIMAL_ZERO)
    # deb will be finmontant = 1000 * (1 + 0.025) ** 1
    v_a_pg = valor_a_pagar_como_debito + payment_1.value
    mult_for_fm = (1 + fix_plus_var_ir_dec) ** 1
    exp_deb_finmontant = v_a_pg * mult_for_fm
    # ==========
    # at the month's end, deb is the mora-updated debt
    # ==========
    self.assertEqual(deb, exp_deb_finmontant)
    exp_abs_deb_increase = abs(v_a_pg * (mult_for_fm - 1))
    exp_ndays_n_amt = [(30, exp_abs_deb_increase)]
    # ==========
    # at the month's end, tuple contains ndays and increse
    # take care with signs (though debt is negative, amounts are positive)
    # (maybe the system should re-sign it, i.e., the amounts being negative)
    # ==========
    self.assertEqual(ndays_n_amt, exp_ndays_n_amt)
