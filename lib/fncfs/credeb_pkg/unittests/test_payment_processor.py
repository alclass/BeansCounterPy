"""

"""
from decimal import Decimal
import unittest
import datetime
import lib.fncfs.credeb_pkg.payment_processor as pay  # pay.process_payments_in_month
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

  def test_1_process_month_pays(self):
    """
    hypotheses 1 and 2

    """
    # hypothesis 1: paying correctly in/on time
    valor_a_pagar_como_debito = Decimal(-2000)
    duedate = datetime.date(2026, 4, 10)
    payment_1 = pay.PaymentInterfaceDateNValue(
      date=duedate, value=Decimal(2000),
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

  def test_2_process_month_pays(self):
    """
    hypotheses 3 and 4
    """
    # hypothesis 3: paying once less but in tardy
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

  def test_3_process_month_pays(self):
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
