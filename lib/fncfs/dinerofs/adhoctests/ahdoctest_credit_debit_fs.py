#!/usr/bin/env python3
"""
lib/fncfs/dinerofs/adhoctests/ahdoctest_credit_debit_fs.py

"""
from dinero import Decimal
from dinero.currencies import BRL
import lib.fncfs.credeb_pkg.credit_debit_fs as cdfs  # cdfs.credit_value_to_cred_account

DINERO_ZERO = Decimal(str("0"), BRL)


def print_adhoc1(
    seq: int, credit: Decimal, account: Decimal, detail: str = ''
  ) -> None:
  fmt_account = f"{account.raw_amount:.02f}" if account is not None else "n/a"
  fmt_credit = f"{credit.raw_amount:.02f}" if credit is not None else "n/a"
  scrmsg = f"{seq} | [{detail}] -> credit = [{fmt_credit}], account = [{fmt_account}]"
  print(scrmsg)


# noinspection PyTypeChecker
def adhoctest1():
  srule = '='*40
  # 1 credacc=200, value=100
  seq = 1
  cred_account = Decimal(str("200"), BRL)
  value = Decimal(str("100"), BRL)
  # credit = Dinero(str("100"), BRL)
  detail = 'input credit'
  print_adhoc1(seq, value, cred_account, detail)
  credit, account = cdfs.debit_or_credit_value_to_accounts(value=value, cred_account=cred_account, deb_account=None)
  detail = 'output'
  print_adhoc1(seq, credit, account, detail)
  print(srule)
  # 2 debacc=-200, value=100
  seq += 1
  deb_account = Decimal(str("-200"), BRL)
  value = Decimal(str("100"), BRL)
  detail = 'input'
  print_adhoc1(seq, value, deb_account, detail)
  credit, account = cdfs.debit_or_credit_value_to_accounts(value=value, cred_account=None, deb_account=deb_account)
  detail = 'output'
  print_adhoc1(seq, value, account, detail)
  print(srule)
  # 3
  seq += 1
  account = Decimal(str("-200"), BRL)
  credit = Decimal(str("100"), BRL)
  detail = 'input'
  print_adhoc1(seq, credit, account, detail)
  detail = 'output'
  print_adhoc1(seq, credit, account, detail)
  print(srule)


def adhoctest2():
  account = Decimal(str("200"), BRL)
  value = Decimal(str("100"), BRL)
  ret_account = cdfs.credit_value_to_cred_account(value, account)
  print('credit_value_to_cred_account', value, account, ret_account)
  #
  account = Decimal(str("-200"), BRL)
  value = Decimal(str("-100"), BRL)
  ret_account = cdfs.debit_value_to_deb_account(value, account)
  print('debit_value_to_deb_account', value, account, ret_account)
  #
  account = Decimal(str("-200"), BRL)
  value = Decimal(str("100"), BRL)
  remaining, ret_account = cdfs.credit_value_to_deb_account(value, account)
  print('credit_value_to_deb_account', value, account, remaining, ret_account)
  #
  account = Decimal(str("200"), BRL)
  value = Decimal(str("-100"), BRL)
  remaining, ret_account = cdfs.debit_value_to_cred_account(value, account)
  print('debit_value_to_cred_account', value, account, remaining, ret_account)
  #
  account = Decimal(str("-100"), BRL)
  value = Decimal(str("200"), BRL)
  remaining, ret_account = cdfs.credit_value_to_deb_account(value, account)
  print('credit_value_to_deb_account', value, account, remaining, ret_account)
  #
  account = Decimal(str("100"), BRL)
  value = Decimal(str("-200"), BRL)
  remaining, ret_account = cdfs.debit_value_to_cred_account(value, account)
  print('debit_value_to_cred_account', value, account, remaining, ret_account)
  #
  cred_account = Decimal(str("100"), BRL)
  deb_account = Decimal(str("-200"), BRL)
  cred_value = Decimal(str("250"), BRL)
  ret_cred_account, ret_deb_account = cdfs.credit_value_to_accounts(cred_value, cred_account, deb_account)
  print('credit_value_to_accounts', cred_value, cred_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cred_account = Decimal(str("100"), BRL)
  deb_account = Decimal(str("-200"), BRL)
  deb_value = Decimal(str("-150"), BRL)
  ret_cred_account, ret_deb_account = cdfs.debit_value_to_accounts(deb_value, cred_account, deb_account)
  print('debit_value_to_accounts', deb_value, cred_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cred_account = Decimal(str("100"), BRL)
  deb_account = Decimal(str("-200"), BRL)
  value = Decimal(str("-150"), BRL)
  ret_cred_account, ret_deb_account = cdfs.debit_or_credit_value_to_accounts(value, cred_account, deb_account)
  print('debit_or_credit_value_to_accounts', value, cred_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cred_account = Decimal(str("7"), BRL)
  deb_account = Decimal(str("-113"), BRL)
  value = Decimal(str("-10"), BRL)
  ret_cred_account, ret_deb_account = cdfs.debit_or_credit_value_to_accounts(value, cred_account, deb_account)
  print('debit_or_credit_value_to_accounts', value, cred_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cred_account = Decimal(str("100"), BRL)
  deb_account = Decimal(str("-200"), BRL)
  value = Decimal(str("150"), BRL)
  ret_cred_account, ret_deb_account = cdfs.credit_value_to_accounts(value, cred_account, deb_account)
  print('credit_value_to_accounts', value, cred_account, deb_account, ret_cred_account, ret_deb_account)
  #
  cred_account = Decimal(str("100"), BRL)
  deb_account = Decimal(str("-200"), BRL)
  ret_cred_account, ret_deb_account = cdfs.compensate_cred_deb_accounts_one_against_the_other(cred_account, deb_account)
  print(
    'compensate_cred_deb_accounts_one_against_the_other',
    'credacc =', cred_account, 'debacc =', deb_account, 'newcredacc =', ret_cred_account, 'newdebacc =', ret_deb_account
  )
  #
  cred_account = Decimal(str("200"), BRL)
  deb_account = Decimal(str("-100"), BRL)
  ret_cred_account, ret_deb_account = cdfs.compensate_cred_deb_accounts_one_against_the_other(cred_account, deb_account)
  print(
    'compensate_cred_deb_accounts_one_against_the_other',
    'credacc =', cred_account, 'debacc =', deb_account, 'newcredacc =', ret_cred_account, 'newdebacc =', ret_deb_account
  )
  #
  cred_account = Decimal(str("100"), BRL)
  deb_account = Decimal(str("-100"), BRL)
  ret_cred_account, ret_deb_account = cdfs.compensate_cred_deb_accounts_one_against_the_other(cred_account, deb_account)
  print(
    'compensate_cred_deb_accounts_one_against_the_other',
    'credacc =', cred_account, 'debacc =', deb_account, 'newcredacc =', ret_cred_account, 'newdebacc =', ret_deb_account
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
