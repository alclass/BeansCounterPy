"""
lib/fncfs/credeb_pkg/unittests/test_payment_fs.py
   Unit-tests to class payment_processor.PaymentProcessor()

import calendar
from dateutil.relativedelta import relativedelta
"""
from decimal import Decimal
import unittest
import datetime
from beanie.odm.utils import pydantic
import art.immeub.rent.billmodels.payment_pydant as bipydtc  # bipydtc.PydtcPayment
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.payments.payments_fs as payfs
mkdt = dtfs.make_date_or_raise
mkrm = rmfs.make_refmonth_or_raise
DECIMAL_ZERO = Decimal(0)
DEFAULT_FIX_IR_DEC = Decimal('0.02')
M_MINUS_N = 2  # this means paymonth minus 2 and refmonth minus 1


class InterfPaymWithDatetime(pydantic.BaseModel):
  datahora: datetime.datetime
  value: Decimal


class InterfPaymWithDate(pydantic.BaseModel):
  date: datetime.date
  value: Decimal


class TestCase1(unittest.TestCase):
  """
  hypothesis 1:
  """

  def test_1_verify_datahora_n_value_donotrepeat_in_payments(self):
    """
    hypothesis 1:
    """
    pdate = mkdt('2026-4-7')
    payments = []
    # noinspection argument-list
    payment1 = bipydtc.PydtcPayment(
      date=pdate,
      value=Decimal(100),
    )
    pdate = mkdt('2026-4-8')
    payments.append(payment1)
    # noinspection argument-list
    payment2 = bipydtc.PydtcPayment(
      date=pdate,
      value=Decimal(100),
    )
    payments.append(payment2)
    payments.append(payment1)
    # subtest 1: combination has a repeat and should raise VA
    with self.assertRaises(ValueError):
      payfs.verify_paydatahora_n_value_donotrepeat_in_payments_or_raise_va(payments)
    payments.pop()
    # subtest 2: combination does not have a repeat and should return None (it executed normally)
    self.assertIsNone(payfs.verify_paydatahora_n_value_donotrepeat_in_payments_or_raise_va(payments))

  def test_2_verify_paymentlist_contains_datahora_n_value(self):
    """
    hypothesis 2:
    """
    pdate = mkdt('2026-4-8')
    dt = dtfs.make_datetime_w_horazero_or_raise(pdate)
    payments = []
    payment1 = InterfPaymWithDatetime(
      datahora=dt,
      value=Decimal(100),
    )
    payments.append(payment1)
    # subtest 1: combination contains fields datahora and value and should return None (it executed normally)
    self.assertIsNone(payfs.verify_paymentlist_contains_datahora_n_value_or_raise_va(payments))
    # noinspection argument-list
    payment2 = InterfPaymWithDate(
      date=pdate,  # in the verify function, Attribute Error is caught as Value Error
      value=Decimal(100),
    )
    payments.append(payment2)
    payments.append(payment1)
    # subtest 2: combination does not contain fields datahora and value and should raise VA
    with self.assertRaises(ValueError):
      payfs.verify_paymentlist_contains_datahora_n_value_or_raise_va(payments)
    payments.pop(1)
    # subtest 3: combination contains fields datahora and value and should return None (it executed normally)
    self.assertIsNone(payfs.verify_paymentlist_contains_datahora_n_value_or_raise_va(payments))

  def test_3_verify_paymentlist_consistency(self):
    """
    A repeat of the two tests above
      via wrapper function verify_paymentlist_consistency_or_raise_va()
    """
    pdate = mkdt('2026-4-8')
    dt = dtfs.make_datetime_w_horazero_or_raise(pdate)
    payments = []
    payment1 = InterfPaymWithDatetime(
      datahora=dt,
      value=Decimal(100),
    )
    payments.append(payment1)
    # noinspection argument-list
    payment2 = InterfPaymWithDate(
      date=pdate,  # in the verify function, Attribute Error is caught as Value Error
      value=Decimal(100),
    )
    payments.append(payment2)
    payments.append(payment1)
    with self.assertRaises(ValueError):
      # subtest 1: this test is repeated from above
      # using wrapper function verify_paymentlist_consistency_or_raise_va
      payfs.verify_paymentlist_consistency_or_raise_va(payments)
    payments.pop(2)
    payments.pop(1)
    # subtest 2: this test is repeated from above using wrapper function verify_paymentlist_consistency_or_raise_va
    self.assertIsNone(payfs.verify_paymentlist_consistency_or_raise_va(payments))

  def test_4_split_nonrepeats_n_repeats_datetime_n_value_in_payments_etal(self):
    pdate = mkdt('2026-4-8')
    dt = dtfs.make_datetime_w_horazero_or_raise(pdate)
    payments = []
    payment1 = InterfPaymWithDatetime(
      datahora=dt,
      value=Decimal(100),
    )
    payments.append(payment1)
    pdate = mkdt('2026-4-9')
    dt = dtfs.make_datetime_w_horazero_or_raise(pdate)
    payment2 = InterfPaymWithDatetime(
      datahora=dt,
      value=Decimal(100),
    )
    payments.append(payment2)
    pys_wo_repeats, repeats = payfs.split_nonrepeats_n_repeats_those_w_equal_datetime_n_value_in_payments(payments)
    # subtest 1: no repeats happened
    self.assertEqual([], repeats)
    # subtest 2: as no repeats happened, pys_wo_repeats = payments
    self.assertEqual(payments, pys_wo_repeats)
    payments.append(payment1)
    pys_wo_repeats, repeats = payfs.split_nonrepeats_n_repeats_those_w_equal_datetime_n_value_in_payments(payments)
    # subtest 3: first payment is a repeat
    self.assertEqual([payment1], repeats)
    # the first element that has a further repeated is the repeat itself,
    # so, because of this, the first repeat is split and goes to the second list in the return value
    payments_reordered = [payment2, payment1]
    # subtest 4: first payment was split out, then pys_wo_repeats == payments_reordered
    self.assertEqual(payments_reordered, pys_wo_repeats)
    payments_w_repeats_removed = payfs.remove_if_repeat_datetime_n_value_in_payments(payments)
    # subtest 5: crossing functions: payments_reordered == payments_repeats_removed
    self.assertEqual(payments_reordered, payments_w_repeats_removed)
    # subtest 6: returning True for repeats 'detected'
    self.assertTrue(payfs.do_datetime_n_value_repeat_in_payments(payments))
    with self.assertRaises(ValueError):
      # subtest 7: raising VA for repeats 'detected'
      payfs.raise_va_if_paydate_n_payvalue_repeat_in_payments(payments)
