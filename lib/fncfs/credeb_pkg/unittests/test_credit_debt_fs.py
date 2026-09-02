#!/usr/bin/env python3
"""
lib/fncfs/credeb_pkg/unittests/test_credit_debt_fs.py
  Unit-tests for 'credeb_pkg.credit_debt_fs.py'
    which is a module for crediting and debting values against crediting and debting accounts.

  Test Hypotheses:
  ================
   1st hypothesis: credit value to credit account
   2nd hypothesis: debt value to debt account
   3rd hypothesis: credit value to debt account
   4th hypothesis: debt value to credit account
   5th hypothesis: credit value to credit and/or debt accounts
   6th hypothesis: debt value to credit and/or debt accounts
   7th hypothesis: credit or debt value to credit and/or debt accounts
   8th hypothesis: compensate credit or debt accounts one against the other
"""
from decimal import Decimal
import lib.fncfs.credeb_pkg.credit_debt_fs as cdfs  # cdfs.credit_value_to_cred_account
import unittest
DECIMAL_ZERO = Decimal("0")


class TestCase1(unittest.TestCase):

  def test_1_credit_value_to_credit_account(self):
    """
    1st hypothesis: credit value to credit account
    """
    # subtest 1 credits 100 to 200
    account = Decimal(200)
    value = Decimal(100)
    exp_account = account + value
    ret_account = cdfs.credit_value_to_cred_account(value, account)
    self.assertEqual(exp_account, ret_account)
    # subtest 2 set value as None, expect a ValueError
    account = Decimal(100)
    value = None
    with self.assertRaises(ValueError):
      cdfs.credit_value_to_cred_account(value, account)
    # subtest 3 set account as None, expect it 'going in' as zero
    account = None
    value = Decimal(100)
    ret_account = cdfs.credit_value_to_cred_account(value, account)
    self.assertEqual(value, ret_account)

  def test_2_debt_value_to_debt_account(self):
    """
    2nd hypothesis 2: debt value to debt account
    """
    # subtest 1 debt -100 to -200
    account = Decimal(-200)
    value = Decimal(-100)
    exp_account = account + value
    ret_account = cdfs.debt_value_to_debt_account(value, account)
    self.assertEqual(exp_account, ret_account)
    # subtest 2 set value as None, expect a ValueError
    value = None
    with self.assertRaises(ValueError):
      cdfs.debt_value_to_debt_account(value, account)
    # subtest 3 set account as None, expect it 'going in' as zero
    account = None
    value = Decimal(-100)
    ret_account = cdfs.debt_value_to_debt_account(value, account)
    self.assertEqual(value, ret_account)

  def test_3_credit_value_to_debt_account(self):
    """
    3rd hypothesis: credit value to debt account
    """
    # subtest 1 credit 100 to -200
    account = Decimal(-200)
    value = Decimal(100)
    exp_account = account + value
    ret_remaining, ret_account = cdfs.credit_value_to_debt_account(value, account)
    self.assertEqual((cdfs.DECIMAL_ZERO, exp_account), (ret_remaining, ret_account))
    # subtest 2 set value as None, expect a ValueError
    value = None
    with self.assertRaises(ValueError):
      cdfs.credit_value_to_debt_account(value, account)
    # subtest 3 set account as None, expect it 'going in' as zero
    account = None
    value = Decimal(100)
    cre_remaining, ret_account = cdfs.credit_value_to_debt_account(value, account)
    self.assertEqual((value, DECIMAL_ZERO), (cre_remaining, ret_account))

  def test_4_debt_value_to_credit_account(self):
    """
    4th hypothesis: debt value to credit account
    """
    # subtest 1 debt -100 to 200
    account = Decimal(200)
    value = Decimal(-100)
    exp_cre_account = account + value
    ret_cre_remaining, ret_deb_account = cdfs.debt_value_to_cred_account(value, account)
    self.assertEqual((exp_cre_account, cdfs.DECIMAL_ZERO), (ret_cre_remaining, ret_deb_account))
    # subtest 2 set value as None, expect a ValueError
    value = None
    with self.assertRaises(ValueError):
      cdfs.debt_value_to_cred_account(value, account)
    # subtest 3 set account as None, expect it 'going in' as zero
    account = None
    value = Decimal(-100)
    ret_cre_account, ret_deb_remaining = cdfs.debt_value_to_cred_account(value, account)
    self.assertEqual((DECIMAL_ZERO, value), (ret_cre_account, ret_deb_remaining))

  def test_5_credit_value_to_accounts(self):
    """
    5th hypothesis: credit value to credit and/or debt accounts
    """
    # subtest 1 credit value to accounts
    cre_account = Decimal(100)
    deb_account = Decimal(-200)
    value = Decimal(150)
    exp_cre_account = cre_account + value + deb_account
    exp_deb_account = DECIMAL_ZERO
    ret_cre_account, ret_deb_account = cdfs.credit_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((exp_cre_account, exp_deb_account), (ret_cre_account, ret_deb_account))
    # subtest 2 set value as None, expect a ValueError
    value = None
    with self.assertRaises(ValueError):
      cdfs.credit_value_to_accounts(value, cre_account, deb_account)
    # subtest 3 with credit, set accounts as None, expect it 'going in' as zero
    cre_account, deb_account = None, None
    value = Decimal(100)
    ret_cre_account, ret_deb_remaining = cdfs.credit_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((value, DECIMAL_ZERO), (ret_cre_account, ret_deb_remaining))

  def test_6_debt_value_to_accounts(self):
    """
    6th hypothesis: debt value to credit and/or debt accounts
    """
    # subtest 1 debt_value_to_accounts(value, cred_account, deb_account)
    cre_account = Decimal(100)
    deb_account = Decimal(-200)
    value = Decimal(-150)
    exp_cre_account = cdfs.DECIMAL_ZERO
    exp_deb_account = cre_account + deb_account + value
    ret_cre_account, ret_deb_account = cdfs.debt_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((exp_cre_account, exp_deb_account), (ret_cre_account, ret_deb_account))
    # subtest 2 set value as None, expect a ValueError
    value = None
    with self.assertRaises(ValueError):
      cdfs.debt_value_to_accounts(value, cre_account, deb_account)
    # subtest 3 set accounts as None, expect them 'going in' as zero
    cre_account, deb_account = None, None
    value = Decimal(-100)
    ret_cre_account, ret_deb_remaining = cdfs.debt_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((DECIMAL_ZERO, value), (ret_cre_account, ret_deb_remaining))

  def test_7_credit_or_debt_value_to_accounts(self):
    """
    7th hypothesis: credit or debt value to credit and/or debt accounts
      This unit-test repeats the two former ones.
    """
    # subtest 1 debt -150 against 100 and -200
    cre_account = Decimal(str("100"))
    deb_account = Decimal(str("-200"))
    value = Decimal(str("-150"))
    exp_cre_account = cdfs.DECIMAL_ZERO
    exp_deb_account = cre_account + deb_account + value
    ret_cre_account, ret_deb_account = cdfs.credit_or_debt_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((exp_cre_account, exp_deb_account), (ret_cre_account, ret_deb_account))
    # subtest 2 credit 150 against 100 and -200
    cre_account = Decimal(str("100"))
    deb_account = Decimal(str("-200"))
    value = Decimal(str("150"))
    exp_cre_account = cre_account + deb_account + value
    exp_deb_account = cdfs.DECIMAL_ZERO
    ret_cre_account, ret_deb_account = cdfs.credit_or_debt_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((exp_cre_account, exp_deb_account), (ret_cre_account, ret_deb_account))
    # subtest 3 set value as None, expect a ValueError
    value = None
    with self.assertRaises(ValueError):
      cdfs.credit_or_debt_value_to_accounts(value, cre_account, deb_account)
    # subtest 4 with debt, set accounts as None, expect them 'going in' as zero
    cre_account, deb_account = None, None
    value = Decimal(-100)
    ret_cre_account, ret_deb_remaining = cdfs.credit_or_debt_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((DECIMAL_ZERO, value), (ret_cre_account, ret_deb_remaining))
    # subtest 5 with credit, set accounts as None, expect them 'going in' as zero
    cre_account, deb_account = None, None
    value = Decimal(100)
    ret_cre_account, ret_deb_remaining = cdfs.credit_or_debt_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((value, DECIMAL_ZERO), (ret_cre_account, ret_deb_remaining))

  def test_8_compensate_credit_w_debt_or_viceversa(self):
    """
    8th hypothesis: compensate credit or debt accounts one against the other
    """
    # subtest 1 cred_account fully compensates deb_account
    cre_account = Decimal(str("200"))
    deb_account = Decimal(str("-100"))
    exp_cre_account = cre_account + deb_account
    exp_deb_account = DECIMAL_ZERO
    ret_cre_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(
      cre_account, deb_account
    )
    self.assertEqual((exp_cre_account, exp_deb_account), (ret_cre_account, ret_deb_account))
    # subtest 2 deb_account fully compensates cred_account
    cre_account = Decimal(str("100"))
    deb_account = Decimal(str("-200"))
    exp_cre_account = DECIMAL_ZERO
    exp_deb_account = cre_account + deb_account
    ret_cre_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(
      cre_account, deb_account
    )
    self.assertEqual((exp_cre_account, exp_deb_account), (ret_cre_account, ret_deb_account))
    # subtest 3 one account fully compensates the other (both end up 'zeroed')
    cre_account = Decimal(str("100"))
    deb_account = Decimal(str("-100"))
    ret_cre_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(
      cre_account, deb_account
    )
    self.assertEqual((DECIMAL_ZERO, DECIMAL_ZERO), (ret_cre_account, ret_deb_account))
    # subtest 4 set accounts as None, expect them 'going in' as zero
    cre_account, deb_account = None, None
    ret_cre_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(
      cre_account, deb_account
    )
    self.assertEqual((DECIMAL_ZERO, DECIMAL_ZERO), (ret_cre_account, ret_deb_account))


def process():
  pass


if __name__ == '__main__':
  """
  adhoctest()
  process()
  """
  pass
