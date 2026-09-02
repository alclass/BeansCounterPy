#!/usr/bin/env python3
"""
lib/fncfs/credeb_pkg/credit_debt_fs.py
  Contains functions for crediting or debting credit and/or debt accounts.

"""
from decimal import Decimal, Context, ROUND_HALF_UP
DECIMAL_CTX = Context(prec=34, rounding=ROUND_HALF_UP)
ONE_THOUSANDTH_AS_STR = '0.0001'
DECIMAL_ZERO = Decimal(str("0"), DECIMAL_CTX).quantize(Decimal(ONE_THOUSANDTH_AS_STR))


def raise_va_if_not_decimal_or_return_it(dec: Decimal, acc_errmsg: str) -> Decimal:
  try:
    if isinstance(dec, Decimal):
      return dec
    else:
      newdec = Decimal(dec)
      return newdec
  except (TypeError, ValueError) as e:
    raise ValueError(str(e) + acc_errmsg)


def raise_va_simmetry_or_zero_or_ret_cre_deb_accounts(
    cre_account: Decimal, deb_account: Decimal
  ) -> tuple[Decimal, Decimal]:
  # Here, if any one of the accounts comes in as None or is not 'decimalizable', it becomes zero.
  if not isinstance(cre_account, Decimal):
    try:
      cre_account = Decimal(cre_account)
    except (TypeError, ValueError):
      cre_account = DECIMAL_ZERO
  if not isinstance(deb_account, Decimal):
    try:
      deb_account = Decimal(deb_account)
    except (TypeError, ValueError):
      deb_account = DECIMAL_ZERO
  if cre_account < DECIMAL_ZERO:
    errmsg = f"Error: credit account [{cre_account}] cannot be negative."
    raise ValueError(errmsg)
  if deb_account > DECIMAL_ZERO:
    errmsg = f"Error: debt account ({deb_account}) cannot be positive."
    raise ValueError(errmsg)
  return cre_account, deb_account


def compensate_cred_debt_accounts_one_against_the_other(
    cre_account: Decimal, deb_account: Decimal,
  ):
  """
  Compensates credit account with debt account (or viceversa).

  About the input parameters:
    a) if any one of the accounts is not decimalizable, it becomes zero (no exception is raised);

  Return new_cre_account, new_deb_account
  """
  cre_account, deb_account = raise_va_simmetry_or_zero_or_ret_cre_deb_accounts(cre_account, deb_account)
  # ========================
  # remembering that cred >= 0 and deb <= 0 (otherwise, ValueError would have been raised in the function above)
  # ========================
  remaining = cre_account + deb_account
  if remaining > DECIMAL_ZERO:
    new_cre_account = remaining
    new_deb_account = DECIMAL_ZERO
  else:
    new_deb_account = remaining
    new_cre_account = DECIMAL_ZERO
  return new_cre_account, new_deb_account


def credit_value_to_cred_account(cre_value: Decimal, cre_account: Decimal) -> Decimal:
  """
  Credits a credit value to a credit account.
  Crediting a cred account is just a summing:
    cre_account += cre_value

  About the input parameters:
    a) value: it must be decimalizable and have credit/debt simmetry (positive/negative) otherwise VA is raised;
    b) account: it becomes zero if not decimalizable;
    
  Returns new_cre_account 
  """
  acc_errmsg = f"Error: credit value ({cre_value}) is not a valid Decimal."
  cre_value = raise_va_if_not_decimal_or_return_it(dec=cre_value, acc_errmsg=acc_errmsg)
  if cre_value < DECIMAL_ZERO:
    errmsg = f"Error: credit value ({cre_value}) cannot be negative."
    raise ValueError(errmsg)
  new_cre_account, _ = raise_va_simmetry_or_zero_or_ret_cre_deb_accounts(cre_account, DECIMAL_ZERO)
  new_cre_account += cre_value
  return new_cre_account


def credit_value_to_debt_account(cre_value: Decimal, deb_account: Decimal) -> tuple[Decimal, Decimal]:
  """
  Credits a debt account. It may produce a remaining.

  About the input parameters:
    a) value: it must be decimalizable and have credit/debt simmetry (positive/negative) otherwise VA is raised;
    b) account: it becomes zero if not decimalizable;

  Returns tuple: credit_remaining, new_deb_account
  """
  acc_errmsg = f"Error: credit value ({cre_value}) is not a valid Decimal."
  cre_value = raise_va_if_not_decimal_or_return_it(dec=cre_value, acc_errmsg=acc_errmsg)
  if cre_value < DECIMAL_ZERO:
    errmsg = f"Error: credit value ({cre_value}) cannot be negative."
    raise ValueError(errmsg)
  # =========================
  _, deb_account = raise_va_simmetry_or_zero_or_ret_cre_deb_accounts(DECIMAL_ZERO, deb_account)
  if abs(deb_account) > cre_value:
    new_deb_account = deb_account + cre_value
    credit_remaining = DECIMAL_ZERO
  else:
    credit_remaining = deb_account + cre_value
    new_deb_account = DECIMAL_ZERO
  return credit_remaining, new_deb_account


def debt_value_to_debt_account(deb_value: Decimal, deb_account: Decimal) -> Decimal:
  """
  Debts a debt account.
  Debting a debt account is just a summing.
    deb_account += deb_value

  About the input parameters:
    a) value: it must be decimalizable and have credit/debt simmetry (positive/negative) otherwise VA is raised;
    b) account: it becomes zero if not decimalizable;

  Returns new_deb_account
  """
  acc_errmsg = f"Error: debt value ({deb_value}) is not a valid Decimal."
  deb_value = raise_va_if_not_decimal_or_return_it(dec=deb_value, acc_errmsg=acc_errmsg)
  if deb_value > DECIMAL_ZERO:
    errmsg = f"Error: debt value ({deb_value}) cannot be positive."
    raise ValueError(errmsg)
  # =========================
  _, deb_account = raise_va_simmetry_or_zero_or_ret_cre_deb_accounts(DECIMAL_ZERO, deb_account)
  new_deb_account = deb_account + deb_value  # both are negative
  return new_deb_account


def debt_value_to_cred_account(deb_value: Decimal, cre_account: Decimal) -> tuple[Decimal, Decimal]:
  """
  Debts a credit account. It may produce a remaining.

  About the input parameters:
    a) value: it must be decimalizable and have credit/debt simmetry (positive/negative) otherwise VA is raised;
    b) account: it becomes zero if not decimalizable;

  Returns tuple: debt_remaining, new_cre_account
  """
  acc_errmsg = f"Error: debt value ({deb_value}) is not a valid Decimal."
  deb_value = raise_va_if_not_decimal_or_return_it(dec=deb_value, acc_errmsg=acc_errmsg)
  if deb_value > DECIMAL_ZERO:
    errmsg = f"Error: debt value ({deb_value}) cannot be positive."
    raise ValueError(errmsg)
  cre_account, _ = raise_va_simmetry_or_zero_or_ret_cre_deb_accounts(cre_account, DECIMAL_ZERO)
  # ========================
  if abs(deb_value) < cre_account:
    new_cre_account = cre_account + deb_value  # cre_account is positive, deb_value is negative
    debt_remaining = DECIMAL_ZERO
  else:
    debt_remaining = cre_account + deb_value
    new_cre_account = DECIMAL_ZERO
  return new_cre_account, debt_remaining


def credit_value_to_accounts(
    cre_value: Decimal, cre_account: Decimal, deb_account: Decimal
  ) -> tuple[Decimal, Decimal]:
  """
  Credits value to debt account and then, if remaining, to credit account.

  About the input parameters:
    a) value: it must be decimalizable and have credit/debt simmetry (positive/negative) otherwise VA is raised;
    b) accounts: become zero if not decimalizable;

  Returns tuple: new_cre_account, new_deb_account
  """
  acc_errmsg = f"Error: credit value ({cre_value}) is not a valid Decimal."
  cre_value = raise_va_if_not_decimal_or_return_it(dec=cre_value, acc_errmsg=acc_errmsg)
  cre_account, deb_account = raise_va_simmetry_or_zero_or_ret_cre_deb_accounts(cre_account, deb_account)
  # ========================
  intermediate_cre_value = credit_value_to_cred_account(cre_value, cre_account)
  new_cre_account, new_deb_account = credit_value_to_debt_account(intermediate_cre_value, deb_account)
  return new_cre_account, new_deb_account


def debt_value_to_accounts(
    deb_value: Decimal, cre_account: Decimal, deb_account: Decimal
  ) -> tuple[Decimal, Decimal]:
  """
  Debts value to credit account and then, if remaining, to debt account.

  About the input parameters:
    a) value: it must be decimalizable and have credit/debt simmetry (positive/negative) otherwise VA is raised;
    b) accounts: become zero if not decimalizable;

  Returns tuple: new_cre_account, new_deb_account
  """
  acc_errmsg = f"Error: debt value ({deb_value}) is not a valid Decimal."
  deb_value = raise_va_if_not_decimal_or_return_it(dec=deb_value, acc_errmsg=acc_errmsg)
  if deb_value > DECIMAL_ZERO:
    errmsg = f"Error: debt value ({deb_value}) cannot be positive."
    raise ValueError(errmsg)
  cre_account, deb_account = raise_va_simmetry_or_zero_or_ret_cre_deb_accounts(cre_account, deb_account)
  # ========================
  intermediate_deb_value = debt_value_to_debt_account(deb_value, deb_account)
  new_cre_account, new_deb_account = debt_value_to_cred_account(intermediate_deb_value, cre_account)
  return new_cre_account, new_deb_account


def credit_or_debt_value_to_accounts(
    value: Decimal, cre_account: Decimal, deb_account: Decimal
  ) -> tuple:
  """
  Credits or debts value to credit and/or debt accounts.

  About the input parameters:
    a) value: it must be decimalizable and have credit/debt simmetry (positive/negative) otherwise VA is raised;
    b) accounts: become zero if not decimalizable;

  Returns tuple: new_cre_account, new_deb_account
    via dispatching to either the 'associated credit function' or its 'counterpart debt function'  
  """
  acc_errmsg = f"Error: credit or debt value ({value}) is not a valid Decimal."
  value = raise_va_if_not_decimal_or_return_it(dec=value, acc_errmsg=acc_errmsg)
  cre_account, deb_account = raise_va_simmetry_or_zero_or_ret_cre_deb_accounts(cre_account, deb_account)
  if value == DECIMAL_ZERO:
    return cre_account, deb_account
  if value > DECIMAL_ZERO:
    return credit_value_to_accounts(value, cre_account, deb_account)
  else:
    return debt_value_to_accounts(value, cre_account, deb_account)


def adhoctests():
  scrmsg = f"""  The adhoctests were moved to a module of their own.

  At the time of writing, they are in module:
    lib/fncfs/dinerofs/adhoctests/ahdoctest_credit_debt_fs.py
  
  This module's full path is: [{__file__}]
  """
  print(scrmsg)


def process():
  pass


if __name__ == '__main__':
  """
  adhoctests()
  process()
  """
  adhoctests()
