#!/usr/bin/env python3
"""
lib/fncfs/dinerofs/adhoctests/ahdoctest_credit_debit_fs.py
  Contains adhoctests for 'credit_debt_fs.py'.

from dinero import Dinero
from dinero.currencies import BRL
DINERO_ZERO = Dinero(Decimal("0"), BRL)
"""
from decimal import Decimal
import lib.fncfs.credeb_pkg.credit_debt_fs as cdfs  # cdfs.credit_value_to_cred_account


def print_adhoc1(
    seq: int, credit: Decimal, account: Decimal, detail: str = ''
  ) -> None:
  fmt_account = f"{account:.02f}" if account is not None else "n/a"
  fmt_credit = f"{credit:.02f}" if credit is not None else "n/a"
  scrmsg = f"{seq} | [{detail}] -> credit = [{fmt_credit}], account = [{fmt_account}]"
  print(scrmsg)


# noinspection PyTypeChecker
def adhoctest1():
  srule = '='*40
  # 1 credacc=200, value=100
  seq = 1
  cre_account = Decimal("200")
  value = Decimal("100")
  # credit = Dinero(str("100"), BRL)
  detail = 'input credit'
  print_adhoc1(seq, value, cre_account, detail)
  credit, account = cdfs.credit_or_debt_value_to_accounts(value=value, cre_account=cre_account, deb_account=None)
  detail = 'output'
  print_adhoc1(seq, credit, account, detail)
  print(srule)
  # 2 debacc=-200, value=100
  seq += 1
  deb_account = Decimal("-200")
  value = Decimal("100")
  detail = 'input'
  print_adhoc1(seq, value, deb_account, detail)
  credit, account = cdfs.credit_or_debt_value_to_accounts(value=value, cre_account=None, deb_account=deb_account)
  detail = 'output'
  print_adhoc1(seq, value, account, detail)
  print(srule)
  # 3
  seq += 1
  account = Decimal("-200")
  credit = Decimal("100")
  detail = 'input'
  print_adhoc1(seq, credit, account, detail)
  detail = 'output'
  print_adhoc1(seq, credit, account, detail)
  print(srule)


def adhoctest2():
  account = Decimal("200")
  value = Decimal("100")
  ret_account = cdfs.credit_value_to_cred_account(value, account)
  print('credit_value_to_cred_account', value, account, ret_account)
  #
  account = Decimal("-200")
  value = Decimal("-100")
  ret_account = cdfs.debt_value_to_debt_account(value, account)
  print('debit_value_to_deb_account', value, account, ret_account)
  #
  account = Decimal("-200")
  value = Decimal("100")
  remaining, ret_account = cdfs.credit_value_to_debt_account(value, account)
  print('credit_value_to_deb_account', value, account, remaining, ret_account)
  #
  account = Decimal("200")
  value = Decimal("-100")
  remaining, ret_account = cdfs.debt_value_to_cred_account(value, account)
  print('debit_value_to_cred_account', value, account, remaining, ret_account)
  #
  account = Decimal("-100")
  value = Decimal("200")
  remaining, ret_account = cdfs.credit_value_to_debt_account(value, account)
  print('credit_value_to_deb_account', value, account, remaining, ret_account)
  #
  account = Decimal("100")
  value = Decimal("-200")
  remaining, ret_account = cdfs.debt_value_to_cred_account(value, account)
  print('debit_value_to_cred_account', value, account, remaining, ret_account)
  #
  cre_account = Decimal("100")
  deb_account = Decimal("-200")
  cred_value = Decimal("250")
  ret_cred_account, ret_deb_account = cdfs.credit_value_to_accounts(cred_value, cre_account, deb_account)
  print('credit_value_to_accounts', cred_value, cre_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cre_account = Decimal("100")
  deb_account = Decimal("-200")
  deb_value = Decimal("-150")
  ret_cred_account, ret_deb_account = cdfs.debt_value_to_accounts(deb_value, cre_account, deb_account)
  print('debit_value_to_accounts', deb_value, cre_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cre_account = Decimal("100")
  deb_account = Decimal("-200")
  value = Decimal("-150")
  ret_cred_account, ret_deb_account = cdfs.credit_or_debt_value_to_accounts(value, cre_account, deb_account)
  print('debit_or_credit_value_to_accounts', value, cre_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cre_account = Decimal(str("7"))
  deb_account = Decimal(str("-113"))
  value = Decimal(str("-10"))
  ret_cred_account, ret_deb_account = cdfs.credit_or_debt_value_to_accounts(value, cre_account, deb_account)
  print('debit_or_credit_value_to_accounts', value, cre_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cre_account = Decimal(str("100"))
  deb_account = Decimal(str("-200"))
  value = Decimal(str("150"))
  ret_cred_account, ret_deb_account = cdfs.credit_value_to_accounts(value, cre_account, deb_account)
  print('credit_value_to_accounts', value, cre_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cre_account = Decimal(str("100"))
  deb_account = Decimal(str("-200"))
  ret_cre_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(cre_account, deb_account)
  print(
    'compensate_cred_deb_accounts_one_against_the_other',
    'credacc =', cre_account, 'debacc =', deb_account, 'newcredacc =', ret_cre_account, 'newdebacc =', ret_deb_account
  )
  #
  cre_account = Decimal(str("200"))
  deb_account = Decimal(str("-100"))
  ret_cred_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(cre_account, deb_account)
  print(
    'compensate_cred_deb_accounts_one_against_the_other',
    'credacc =', cre_account, 'debacc =', deb_account, 'newcredacc =', ret_cred_account, 'newdebacc =', ret_deb_account
  )
  #
  cre_account = Decimal(str("100"))
  deb_account = Decimal(str("-100"))
  ret_cre_account, ret_deb_account = cdfs.compensate_cred_debt_accounts_one_against_the_other(cre_account, deb_account)
  print(
    'compensate_cred_deb_accounts_one_against_the_other',
    'credacc =', cre_account, 'debacc =', deb_account, 'newcredacc =', ret_cre_account, 'newdebacc =', ret_deb_account
  )


def various_adhoctests():
  adhoctest1()
  adhoctest2()


def process():
  pass


if __name__ == '__main__':
  """
  various_adhoctests()
  process()
  """
  various_adhoctests()
