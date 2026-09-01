#!/usr/bin/env python3
"""
lib/fncfs/credeb_pkg/unittests/test_credit_debt_fs.py
  Unit-tests for 'credeb_pkg.credit_debt_fs.py'
    which is a module for crediting and debting values against crediting and debting accounts.

  Hypotheses:
    # 1 hypothesis 1-1 credit_value_to_cred_account()
    # 2 hypothesis 1-2 debt_value_to_debt_account()
    # 3 hypothesis 1-3 credit_value_to_debt_account()
    # 4 hypothesis 1-4 debt_value_to_cred_account()
    # 5 hypothesis 2-1 credit_value_to_accounts(value, cred_account, deb_account)
    # 6 hypothesis 2-2 debt_value_to_accounts(value, cred_account, deb_account)
    # 7 hypothesis 2-3 debt_or_credit_value_to_accounts(value, cred_account, deb_account)
    # 8 hypothesis 3-1 compensate_cred_deb_accounts_one_against_the_other()
    # 9 hypothesis 3-2 compensate_cred_deb_accounts_one_against_the_other()
    # 10 hypothesis 3-3 (simetric) compensate_cred_deb_accounts_one_against_the_other()
"""
from decimal import Decimal
import lib.fncfs.credeb_pkg.credit_debt_fs as cdfs  # cdfs.credit_value_to_cred_account
import unittest
DECIMAL_ZERO = Decimal("0")


class TestCase1(unittest.TestCase):

  def setUp(self) -> None:
    pass

  def test_1credit_debt_w_1_cre_or_deb_account(self):
    # hypothesis 1-1 credit_value_to_cred_account()
    account = Decimal(str("200"))
    value = Decimal(str("100"))
    exp_account = account + value
    ret_account = cdfs.credit_value_to_cred_account(value, account)
    self.assertEqual(exp_account, ret_account)
    # hypothesis 1-2 debt_value_to_debt_account()
    account = Decimal(str("-200"))
    value = Decimal(str("-100"))
    exp_account = account + value
    ret_account = cdfs.debt_value_to_debt_account(value, account)
    self.assertEqual(exp_account, ret_account)
    # hypothesis 1-3 credit_value_to_debt_account()
    account = Decimal(str("-200"))
    value = Decimal(str("100"))
    exp_account = account + value
    ret_remaining, ret_account = cdfs.credit_value_to_debt_account(value, account)
    self.assertEqual((cdfs.DECIMAL_ZERO, exp_account), (ret_remaining, ret_account))
    # hypothesis 1-4 debt_value_to_cred_account()
    cre_account = Decimal(str("200"))
    deb_value = Decimal(str("-100"))
    exp_cre_account = cre_account + deb_value
    ret_cre_remaining, ret_deb_account = cdfs.debt_value_to_cred_account(deb_value, cre_account)
    self.assertEqual((exp_cre_account, cdfs.DECIMAL_ZERO), (ret_cre_remaining, ret_deb_account))

  def test_2credit_debt_w_2_cre_n_deb_accounts(self):
    # hypothesis 2-1 credit_value_to_accounts(value, cred_account, deb_account)
    cre_account = Decimal(str("100"))
    deb_account = Decimal(str("-200"))
    value = Decimal(str("150"))
    # this credit is divided into two actions
    # first: cred 150 is credited against debt -200, cred is zeroed, debtacc becomes -50
    # second: because cred was zeroed, credacc remains the same
    exp_cre_account = cre_account + value + deb_account  # in this case, it remains the same
    exp_deb_account = DECIMAL_ZERO
    ret_cre_account, ret_deb_account = cdfs.credit_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((exp_cre_account, exp_deb_account), (ret_cre_account, ret_deb_account))
    # hypothesis 2-2 debt_value_to_accounts(value, cred_account, deb_account)
    cre_account = Decimal(str("100"))
    deb_account = Decimal(str("-200"))
    value = Decimal(str("-150"))
    exp_cre_account = cdfs.DECIMAL_ZERO
    exp_deb_account = cre_account + deb_account + value
    ret_cre_account, ret_deb_account = cdfs.debt_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((exp_cre_account, exp_deb_account), (ret_cre_account, ret_deb_account))
    # hypothesis 2-3 debt_or_credit_value_to_accounts(value, cred_account, deb_account)
    cre_account = Decimal(str("100"))
    deb_account = Decimal(str("-200"))
    value = Decimal(str("-150"))
    exp_cre_account = cdfs.DECIMAL_ZERO
    exp_deb_account = cre_account + deb_account + value
    ret_cre_account, ret_deb_account = cdfs.credit_or_debt_value_to_accounts(value, cre_account, deb_account)
    self.assertEqual((exp_cre_account, exp_deb_account), (ret_cre_account, ret_deb_account))

  def test_3compensate_cred_w_debt_or_viceversa(self):
    # hypothesis 3-1 compensate_cred_deb_accounts_one_against_the_other()
    # cred_account fully compensates deb_account
    cred_account = Decimal(str("200"))
    deb_account = Decimal(str("-100"))
    exp_cred_account = cred_account + deb_account
    exp_deb_account = DECIMAL_ZERO
    ret_cred_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(
      cred_account, deb_account
    )
    self.assertEqual((exp_cred_account, exp_deb_account), (ret_cred_account, ret_deb_account))
    # hypothesis 3-2 compensate_cred_deb_accounts_one_against_the_other()
    # deb_account fully compensates cred_account
    cred_account = Decimal(str("100"))
    deb_account = Decimal(str("-200"))
    exp_cred_account = DECIMAL_ZERO
    exp_deb_account = cred_account + deb_account
    ret_cred_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(
      cred_account, deb_account
    )
    self.assertEqual((exp_cred_account, exp_deb_account), (ret_cred_account, ret_deb_account))
    # hypothesis 3-3 compensate_cred_deb_accounts_one_against_the_other()
    # one fully compensates the other (both end up 'zeroed')
    cred_account = Decimal(str("100"))
    deb_account = Decimal(str("-100"))
    ret_cred_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(
      cred_account, deb_account
    )
    self.assertEqual((DECIMAL_ZERO, DECIMAL_ZERO), (ret_cred_account, ret_deb_account))


def process():
  pass


if __name__ == '__main__':
  """
  adhoctest()
  process()
  """
  pass
