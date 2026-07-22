#!/usr/bin/env python3
"""
lib/finfs/dinerofs/credit_debit_fs.py

"""
from dinero import Dinero
from dinero.currencies import BRL
import finfs.dinerofs.credit_debit_fs as cdfs  # cdfs.credit_value_to_cred_account
import unittest
DINERO_ZERO = Dinero(str("0"), BRL)


class TestCase1(unittest.TestCase):

  def setUp(self) -> None:
    pass

  def test_1credit_debt_w_1_cre_or_deb_account(self):
    # hypothesis 1-1 credit_value_to_cred_account()
    account = Dinero(str("200"), BRL)
    value = Dinero(str("100"), BRL)
    exp_account = account + value
    ret_account = cdfs.credit_value_to_cred_account(value, account)
    self.assertEqual(exp_account, ret_account)
    # hypothesis 1-2 debit_value_to_deb_account()
    account = Dinero(str("-200"), BRL)
    value = Dinero(str("-100"), BRL)
    exp_account = account + value
    ret_account = cdfs.debit_value_to_deb_account(value, account)
    self.assertEqual(exp_account, ret_account)
    # hypothesis 1-3 credit_value_to_deb_account()
    account = Dinero(str("-200"), BRL)
    value = Dinero(str("100"), BRL)
    exp_account = account + value
    exp_remaining = cdfs.DINERO_ZERO
    ret_remaining, ret_account = cdfs.credit_value_to_deb_account(value, account)
    self.assertEqual((exp_remaining, exp_account), (ret_remaining, ret_account))
    # hypothesis 1-4 debit_value_to_cred_account()
    account = Dinero(str("200"), BRL)
    value = Dinero(str("-100"), BRL)
    exp_account = account + value
    exp_remaining = cdfs.DINERO_ZERO
    ret_remaining, ret_account = cdfs.debit_value_to_cred_account(value, account)
    self.assertEqual((exp_remaining, exp_account), (ret_remaining, ret_account))

  def test_2credit_debt_w_2_cre_n_deb_accounts(self):
    # hypothesis 2-1 debit_or_credit_value_to_accounts(value, cred_account, deb_account)
    cred_account = Dinero(str("100"), BRL)
    deb_account = Dinero(str("-200"), BRL)
    value = Dinero(str("-150"), BRL)
    exp_cred_account = cdfs.DINERO_ZERO
    exp_deb_account = cred_account + deb_account + value
    ret_cred_account, ret_deb_account = cdfs.debit_or_credit_value_to_accounts(value, cred_account, deb_account)
    self.assertEqual((exp_cred_account, exp_deb_account), (ret_cred_account, ret_deb_account))
    # hypothesis 2-2 debit_value_to_accounts(value, cred_account, deb_account)
    cred_account = Dinero(str("100"), BRL)
    deb_account = Dinero(str("-200"), BRL)
    value = Dinero(str("-150"), BRL)
    exp_cred_account = cdfs.DINERO_ZERO
    exp_deb_account = cred_account + deb_account + value
    ret_cred_account, ret_deb_account = cdfs.debit_value_to_accounts(value, cred_account, deb_account)
    self.assertEqual((exp_cred_account, exp_deb_account), (ret_cred_account, ret_deb_account))
    # hypothesis 2-3 credit_value_to_accounts(value, cred_account, deb_account)
    cred_account = Dinero(str("100"), BRL)
    deb_account = Dinero(str("-200"), BRL)
    value = Dinero(str("150"), BRL)
    # this credit is divided into two actions
    # first: cred 150 is credited against debt -200, cred is zeroed, debtacc becomes -50
    # second: because cred was zeroed, credacc remains the same
    exp_cred_account = cred_account  # in this case, it remains the same
    exp_deb_account = deb_account + value  # in this case
    ret_cred_account, ret_deb_account = cdfs.credit_value_to_accounts(value, cred_account, deb_account)
    self.assertEqual((exp_cred_account, exp_deb_account), (ret_cred_account, ret_deb_account))

  def test_3compensate_cred_w_debt_or_viceversa(self):
    # hypothesis 3-1 compensate_cred_deb_accounts_one_against_the_other()
    # cred_account fully compensates deb_account
    cred_account = Dinero(str("200"), BRL)
    deb_account = Dinero(str("-100"), BRL)
    exp_cred_account = cred_account + deb_account
    exp_deb_account = DINERO_ZERO
    ret_cred_account, ret_deb_account = cdfs.compensate_cred_deb_accounts_one_against_the_other(
      cred_account, deb_account
    )
    self.assertEqual((exp_cred_account, exp_deb_account), (ret_cred_account, ret_deb_account))
    # hypothesis 3-2 compensate_cred_deb_accounts_one_against_the_other()
    # deb_account fully compensates cred_account
    cred_account = Dinero(str("100"), BRL)
    deb_account = Dinero(str("-200"), BRL)
    exp_cred_account = DINERO_ZERO
    exp_deb_account = cred_account + deb_account
    ret_cred_account, ret_deb_account = cdfs.compensate_cred_deb_accounts_one_against_the_other(
      cred_account, deb_account
    )
    self.assertEqual((exp_cred_account, exp_deb_account), (ret_cred_account, ret_deb_account))
    # hypothesis 3-3 compensate_cred_deb_accounts_one_against_the_other()
    # one fully compensates the other (both end up 'zeroed')
    cred_account = Dinero(str("100"), BRL)
    deb_account = Dinero(str("-100"), BRL)
    exp_cred_account = DINERO_ZERO
    exp_deb_account = DINERO_ZERO
    ret_cred_account, ret_deb_account = cdfs.compensate_cred_deb_accounts_one_against_the_other(
      cred_account, deb_account
    )
    self.assertEqual((exp_cred_account, exp_deb_account), (ret_cred_account, ret_deb_account))


def process():
  pass


if __name__ == '__main__':
  """
  adhoctest()
  process()
  """
  pass
