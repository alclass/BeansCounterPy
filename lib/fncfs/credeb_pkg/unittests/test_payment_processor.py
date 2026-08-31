"""
lib/fncfs/credeb_pkg/unittests/test_payment_processor.py
   Unit-tests to class payment_processor.PaymentProcessor()
"""
from decimal import Decimal
import unittest
import datetime
from dateutil.relativedelta import relativedelta
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.credeb_pkg.payment_processor as pay  # pay.process_payments_in_month
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcam  # ipcam.
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fm_mnts
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fnmts
mkdt = dtfs.make_date_or_raise
mkrm = rmfs.make_refmonth_or_raise
DECIMAL_ZERO = Decimal(0)
DEFAULT_FIX_IR_DEC = Decimal('0.02')


class TestCase1(unittest.TestCase):
  """
  # hypothesis 1: paying correctly in/on time
  # hypothesis 2: paying once less than due but in time
  # hypothesis 3: paying once less and tardy
  # hypothesis 4: paying twice less than due: once in time, once tardy
  # hypothesis 5: paying twice, one in due time, one tardy, more than duepayment (has credit)
  # hypothesis 6: paying twice, twice tardy, more than duepayment (has credit)
  # hypothesis 7: paying nothing (to check/verify back mora)
  # hypothesis 8: paying once in/on time leaving credit
  """

  def test_1_paying_the_charged_amount(self):
    """
    hypothesis 1: paying total monthsdebt correctly up to duedate

    A numerical example:
      a) paydate <= duedate: e.g. 2026-04-10
      b) payvalue == duevalue e.g. 2000 (when monthsdebt = -2000)
    """
    monthdebtvalue = Decimal(-2000)
    duedate = datetime.date(2026, 4, 10)
    payment_1 = intrfc.PaymentInterfaceDateNValue(
      date=duedate, value=Decimal(2000),
    )
    pprocessor = pay.PaymentProcessor(
      ongoing_debt=monthdebtvalue,
      duedate=duedate,
    )
    pprocessor.payments = [payment_1]
    self.assertIsNone(pprocessor.is_monthsbill_fully_paid())
    pprocessor.process()
    # tuple[decimal.Decimal, decimal.Decimal, list[tuple[int, Decimal]]]
    cre, deb, monthmoras = pprocessor.cre_deb_moras_after_process
    self.assertEqual(cre, DECIMAL_ZERO)
    self.assertEqual(deb, DECIMAL_ZERO)
    self.assertEqual(monthmoras, [])
    self.assertTrue(pprocessor.is_monthsbill_fully_paid)

  def test_2_paying_1once_2lessthandue_3uptoduedate(self):
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
    fix_ir_dec = Decimal(0.02)
    pprocessor = pay.PaymentProcessor(
      ongoing_debt=monthdebtvalue,
      duedate=duedate,
      fix_ir_dec=fix_ir_dec,
    )
    payment_1 = intrfc.PaymentInterfaceDateNValue(
      date=duedate, value=Decimal(1000),
    )
    pprocessor.payments = [payment_1]
    self.assertIsNone(pprocessor.is_monthsbill_fully_paid())
    pprocessor.process()
    inidate = mkdt('2026-04-01')
    findate = mkdt('2026-04-30')
    refmonth = mkrm('2026-03')
    m_minus_n = 2
    ir_idx, ipca_dec = ipcam.fetch_iridx_n_ipca_m_plus_i_w_refmonth_n_fix(
      refmonth=refmonth, p_fix_ir_dec=fix_ir_dec, i=m_minus_n,
    )
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
    objs_ipca_dec = monthmora.var_ir_dec
    self.assertEqual(ipca_dec, objs_ipca_dec)
    self.assertEqual(deb, missing_avec_mora)
    self.assertEqual(cre, DECIMAL_ZERO)
    # noinspection bad-argument-type
    self.assertEqual(len(monthmoras), 1)
    self.assertEqual(moravalue, monthmora.increase)
    # the 1000 missing is counted for the whole month (30 days)
    # though the 'balance approach' is better when there are payments after duedate
    self.assertEqual(monthmora.moradays, 30)
    self.assertEqual(monthmora.prevalue, missing_sans_mora)
    self.assertEqual(monthmora.postvalue, missing_avec_mora)
    self.assertEqual(monthmora.ir_idx, ir_idx)
    self.assertEqual(pprocessor.tot_mor_val, moravalue)
    self.assertFalse(pprocessor.is_monthsbill_fully_paid())


  def test_3_paying_1once_2lessthandue_3afterduedate(self):
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
      date=paydate, value=Decimal(1000),
    )
    pprocessor.payments = [payment_1]
    pprocessor.process()
    inidate = mkdt('2026-04-01')
    findate = mkdt('2026-04-30')
    fix_ir_dec = Decimal(0.02)
    refmonth = rmfs.make_refmonth_or_raise('2026-03')
    m_minus_n = 2
    ir_idx, ipca_dec = ipcam.fetch_iridx_n_ipca_m_plus_i_w_refmonth_n_fix(
      refmonth=refmonth, p_fix_ir_dec=fix_ir_dec, i=m_minus_n,
    )
    # exp_inimontant_1 = monthdebtvalue
    exp_moravalue1 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=Decimal(-2000),
      ir_idx=ir_idx,
      inidate=inidate,
      findate=paydate,
    )
    paydate_plus_1 = paydate + relativedelta(days=1)
    exp_inimontant_2 = Decimal(-1000) + exp_moravalue1
    exp_moravalue2 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=exp_inimontant_2,
      ir_idx=ir_idx,
      inidate=paydate_plus_1,
      findate=findate,
    )
    the_2_mora = exp_moravalue1 + exp_moravalue2
    exp_debito_no_fecho = monthdebtvalue + payment_1.value + the_2_mora
    credito_debito_no_fecho, ret_debito_no_fecho, monthmoras = pprocessor.cre_deb_moras_after_process
    self.assertEqual(credito_debito_no_fecho, DECIMAL_ZERO)
    ret_monthmora_1 = monthmoras[0]
    ret_monthmora_2 = monthmoras[1]
    objs_ipca_dec = ret_monthmora_1.var_ir_dec
    self.assertEqual(ipca_dec, objs_ipca_dec)
    self.assertEqual(ret_monthmora_1.ir_idx, ir_idx)
    # noinspection bad-argument-type
    self.assertEqual(len(monthmoras), 2)
    self.assertEqual(the_2_mora, ret_monthmora_1.increase+ret_monthmora_2.increase)
    self.assertEqual(ret_debito_no_fecho, exp_debito_no_fecho)
    self.assertEqual(ret_monthmora_1.moradays, 20)
    self.assertEqual(ret_monthmora_2.moradays, 10)
    self.assertEqual(exp_debito_no_fecho, ret_debito_no_fecho)
    self.assertFalse(pprocessor.is_monthsbill_fully_paid())

  def test_4_paying_1twice_2lessthandue_3afterduedate(self):
    """
      # hypothesis 4: paying twice less than due, twice in time, once tardy

    hypotheses 5 and 6
    # hypothesis 5: paying twice, one in due time, one tardy
    # hypothesis 6: paying twice, twice tardy

    """
    # hypothesis 5: paying twice, one in due time, one tardy
    inidate, findate = mkdt('2026-4-1'), mkdt('2026-04-30')
    duedate, paydate1, paydate2 = mkdt('2026-04-10'), mkdt('2026-04-15'), mkdt('2026-04-25')
    payvalue1, payvalue2 = Decimal(950), Decimal(850)
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
    refmonth = rmfs.make_refmonth_or_raise('2026-03')
    m_minus_n = 2
    ir_idx, ipca_dec = ipcam.fetch_iridx_n_ipca_m_plus_i_w_refmonth_n_fix(
      refmonth=refmonth, p_fix_ir_dec=fix_ir_dec, i=m_minus_n,
    )
    exp_inimontant_1 = monthdebtvalue
    exp_moravalue1 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=exp_inimontant_1,
      ir_idx=ir_idx,
      inidate=inidate,
      findate=paydate1,
    )
    paydate1_plus_1 = paydate1 + relativedelta(days=1)
    exp_inimontant_2 = exp_inimontant_1 + payvalue1 + exp_moravalue1
    exp_moravalue2 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=exp_inimontant_2,
      ir_idx=ir_idx,
      inidate=paydate1_plus_1,
      findate=paydate2,
    )
    paydate2_plus_1 = paydate2 + relativedelta(days=1)
    exp_inimontant_3 = exp_inimontant_2 + payvalue2 + exp_moravalue2
    exp_moravalue3 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=exp_inimontant_3,
      ir_idx=ir_idx,
      inidate=paydate2_plus_1,
      findate=findate,
    )
    exp_total_moravalue = exp_moravalue1 + exp_moravalue2 + exp_moravalue3
    calcd_total_moravalue = pprocessor.tot_mor_val
    cre, deb, monthmoras = pprocessor.cre_deb_moras_after_process
    self.assertEqual(calcd_total_moravalue, exp_total_moravalue)
    self.assertEqual(cre, DECIMAL_ZERO)
    exp_deb = monthdebtvalue + payvalue1 + payvalue2 + exp_moravalue1 + exp_moravalue2 + exp_moravalue3
    # noinspection bad-argument-type
    deb, exp_deb = fm_mnts.sigfig(deb, 16), fm_mnts.sigfig(exp_deb, 16)
    exp_debito_no_fecho, ret_debito_no_fecho = exp_deb, deb
    self.assertEqual(exp_debito_no_fecho, ret_debito_no_fecho)
    self.assertFalse(pprocessor.is_monthsbill_fully_paid())

  def test_5_paying_1twice_oneuptoduedate_oneafter_2morethanduepay(self):
    """
    hypothesis 5:
      a) paying twice: once up to duetime, once tardy,
      b) the second and tardy payment paying more than month's duevalue, i.e., resulting credit.

    hypothesis 6: paying twice, twice tardy
    """
    # hypothesis 5: paying twice, one in due time, one tardy
    paymonthstr = '2025-4'
    inidate, findate = mkdt(f'{paymonthstr}-1'), mkdt(f'{paymonthstr}-30')
    paymonth = inidate
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
    refmonth = rmfs.make_refmonth_it_minus_n_or_raise(paymonth, 1)
    m_minus_n = 2
    ir_idx, ipca_dec = ipcam.fetch_iridx_n_ipca_m_plus_i_w_refmonth_n_fix(
      refmonth=refmonth, p_fix_ir_dec=fix_ir_dec, i=m_minus_n,
    )
    exp_inimontant_1 = monthdebtvalue + payvalue1
    exp_moravalue1 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=exp_inimontant_1,
      ir_idx=ir_idx,
      inidate=inidate,
      findate=paydate2,
    )
    exp_credit = monthdebtvalue + payvalue1 + payvalue2  + exp_moravalue1
    ret_credit, ret_debt, monthmoras = pprocessor.cre_deb_moras_after_process
    self.assertEqual(ret_debt, DECIMAL_ZERO)
    self.assertEqual(len(pprocessor.monthmoras), 1)
    self.assertEqual(pprocessor.monthmoras[0].increase, exp_moravalue1)
    # to the IDE because ret_credit is None when processing is unfinished which is not the case at this point
    ret_credit = ret_credit if ret_credit is not None else Decimal(0)
    # below sigfix was set to 15 which is 'big enough', the two ways (exp and ret) diverge 'very far' in digits
    exp_credit, ret_credit = fm_mnts.sigfig(exp_credit, 15), fm_mnts.sigfig(ret_credit, 15)
    self.assertEqual(exp_credit, ret_credit)


  def test_6_paying_1twice_tardy_2morethanduedate(self):
    """
    hypothesis 6:
      a) paying twice
      b) twice tardy (after than duedate)
      c) the payments are more than 'corrected' duepayment
    """
    paymonthstr = '2025-4'
    inidate, findate = mkdt(f'{paymonthstr}-1'), mkdt(f'{paymonthstr}-30')
    paymonth = inidate
    duedate, paydate1, paydate2 = mkdt(f'{paymonthstr}-10'), mkdt(f'{paymonthstr}-15'), mkdt(f'{paymonthstr}-23')
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
    refmonth = rmfs.make_refmonth_it_minus_n_or_raise(paymonth, 1)
    m_minus_n = 2
    ir_idx, ipca_dec = ipcam.fetch_iridx_n_ipca_m_plus_i_w_refmonth_n_fix(
      refmonth=refmonth, p_fix_ir_dec=fix_ir_dec, i=m_minus_n,
    )
    exp_inimontant_1 = monthdebtvalue
    exp_moravalue1 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=exp_inimontant_1,
      ir_idx=ir_idx,
      inidate=inidate,
      findate=paydate1,
    )
    exp_inimontant_2 = exp_inimontant_1 + payvalue1 + exp_moravalue1
    paydate1_plus_1 = paydate1 + relativedelta(days=1)
    exp_moravalue2 = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=exp_inimontant_2,
      ir_idx=ir_idx,
      inidate=paydate1_plus_1,
      findate=paydate2,
    )
    exp_credit = monthdebtvalue + payvalue1 + payvalue2  + exp_moravalue1 + exp_moravalue2
    ret_credit, ret_debt, monthmoras = pprocessor.cre_deb_moras_after_process
    self.assertEqual(ret_debt, DECIMAL_ZERO)
    self.assertEqual(len(pprocessor.monthmoras), 2)
    self.assertEqual(pprocessor.monthmoras[0].increase, exp_moravalue1)
    self.assertEqual(pprocessor.monthmoras[1].increase, exp_moravalue2)
    # to the IDE because ret_credit is None when processing is unfinished which is not the case at this point
    ret_credit = ret_credit if ret_credit is not None else Decimal(0)
    # below sigfix was set to 15 which is 'big enough', the two ways (exp and ret) diverge 'very far' in digits
    exp_credit, ret_credit = fm_mnts.sigfig(exp_credit, 15), fm_mnts.sigfig(ret_credit, 15)
    self.assertEqual(exp_credit, ret_credit)

  def test_7_no_payments_during_paymonth(self):
    """
    hypothesis 7:
      a) paying nothing during paymonth (to check/verify back month's mora)
    """
    paymonthstr = '2025-4'
    inidate, findate = mkdt(f'{paymonthstr}-1'), mkdt(f'{paymonthstr}-30')
    paymonth = inidate
    duedate, paydate1, paydate2 = mkdt(f'{paymonthstr}-10'), mkdt(f'{paymonthstr}-15'), mkdt(f'{paymonthstr}-23')
    monthdebtvalue = Decimal(-2000)
    pprocessor = pay.PaymentProcessor(
      ongoing_debt=monthdebtvalue,
      duedate=duedate,
      fix_ir_dec=Decimal(0.02),
    )
    pprocessor.payments = []
    pprocessor.process()
    fix_ir_dec = Decimal(0.02)
    # refmonth is the previous (penultimate, one but last) month from paymonth
    refmonth = rmfs.make_refmonth_it_minus_n_or_raise(paymonth, 1)
    m_minus_n = 2
    ir_idx, ipca_dec = ipcam.fetch_iridx_n_ipca_m_plus_i_w_refmonth_n_fix(
      refmonth=refmonth, p_fix_ir_dec=fix_ir_dec, i=m_minus_n,
    )
    exp_inimontant = monthdebtvalue
    exp_moravalue = fnmts.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=exp_inimontant,
      ir_idx=ir_idx,
      inidate=inidate,
      findate=findate,
    )
    exp_credit = DECIMAL_ZERO
    ret_credit, ret_debt, monthmoras = pprocessor.cre_deb_moras_after_process
    self.assertEqual(exp_credit, ret_credit)
    exp_debt = exp_inimontant + exp_moravalue
    self.assertEqual(exp_debt, ret_debt)
    self.assertEqual(len(pprocessor.monthmoras), 1)
    self.assertEqual(pprocessor.monthmoras[0].increase, exp_moravalue)

  def test_8_paying_once_leaving_credit(self):
    """
    hypothesis 8:
      a) paying once in/on time;
      b) paying more than duepayment, then leaving credit;
    """
    paymonthstr = '2025-4'
    # inidate, findate = mkdt(f'{paymonthstr}-1'), mkdt(f'{paymonthstr}-30')
    duedate, paydate1 = mkdt(f'{paymonthstr}-10'), mkdt(f'{paymonthstr}-5')
    monthdebtvalue = Decimal(-2000)
    pprocessor = pay.PaymentProcessor(
      ongoing_debt=monthdebtvalue,
      duedate=duedate,
      fix_ir_dec=Decimal(0.02),
    )
    payvalue1 = Decimal(2200)
    payment = intrfc.PaymentInterfaceDateNValue(
      date=paydate1, value=payvalue1,
    )
    pprocessor.payments = [payment]
    pprocessor.process()
    exp_credit = monthdebtvalue + payvalue1
    ret_credit, ret_debt, monthmoras = pprocessor.cre_deb_moras_after_process
    self.assertEqual(exp_credit, ret_credit)
    exp_debt = DECIMAL_ZERO
    self.assertEqual(exp_debt, ret_debt)
    self.assertEqual(len(pprocessor.monthmoras), 0)
