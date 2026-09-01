#!/usr/bin/env python3
"""
lib/fncfs/credeb_pkg/credit_debt_fs.py
  Contains functions for crediting or debting credit and/or debt accounts.

"""
from dinero import Dinero
from dinero.currencies import BRL
from decimal import Decimal, Context, ROUND_HALF_UP
DECIMAL_CTX = Context(prec=34, rounding=ROUND_HALF_UP)
ONE_THOUSANDTH_AS_STR = '0.0001'
DECIMAL_ZERO = Decimal(str("0"), DECIMAL_CTX).quantize(Decimal(ONE_THOUSANDTH_AS_STR))
DINERO_ZERO = Dinero(str("0"), BRL)


def make_decimal_w_appcontext(val: str | int | float | Decimal, n_decimal_places: int = 4) -> Decimal:
  if n_decimal_places == 4:
    str_decimal_places = ONE_THOUSANDTH_AS_STR
  else:
    str_decimal_places = '0.' + '0'*(n_decimal_places-1) + '1'
  return Decimal(val, DECIMAL_CTX).quantize(Decimal(str_decimal_places))


def compensate_cred_debt_accounts_one_against_the_other(
    cre_account: Decimal, deb_account: Decimal,
  ):
  """
  Compensates credit account with debt account (or viceversa)

  input: credit_account, debt_account
  output: new_credit_account, new_debt_account

  Example:
    ex1:
      input:
        cre_account = 100
        deb_account = -200
      output:
        new_cre_account = 0
        new_deb_account = -100
    ex2:
      input:
        cre_account = 200
        deb_account = -100
      output:
        new_cre_account = 100
        new_deb_account = 0
    ex3:
      input:
        cre_account = 100
        deb_account = -100
      output:
        new_cre_account = 0
        new_deb_account = 0
  """
  # noinspection unreachable-code
  if cre_account is None or deb_account is None:
    errmsg = f"Error: credit account [{cre_account}] or deb_account [{deb_account}] is None. Neither can be None."
    raise ValueError(errmsg)
  if cre_account < DECIMAL_ZERO:
    errmsg = f"Error: credit account ({cre_account}) cannot be negative."
    raise ValueError(errmsg)
  if deb_account > DECIMAL_ZERO:
    errmsg = f"Error: debt account ({deb_account}) cannot be positive."
    raise ValueError(errmsg)
  # ========================
  # remembering that cred >= 0 and deb <= 0 (otherwise, ValueError would be raised above)
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
  Crediting a cred account is just a sum, and it doesn't produce a remaining.
  """
  # noinspection unreachable-code
  if cre_value is None or cre_account is None:
    errmsg = f"Error: either (credit) value [{cre_value}] (credit) or account [{cre_account}] is None. Neither can be None."
    raise ValueError(errmsg)
  if cre_value < DECIMAL_ZERO:
    errmsg = f"Error: credit_value ({cre_value}) cannot be negative"
    raise ValueError(errmsg)
  if cre_account < DECIMAL_ZERO:
    errmsg = f"Error: cred account ({cre_account}) cannot be negative"
    raise ValueError(errmsg)
  cre_account = cre_account + cre_value
  return cre_account


def credit_value_to_debt_account(cre_value: Decimal, deb_account: Decimal) -> tuple[Decimal, Decimal]:
  """
  Credits a debt account. It may produce a remaining.
  Returns (remaining, deb_acc)
  """
  # noinspection unreachable-code
  if cre_value is None or deb_account is None:
    errmsg = f"Error: either (credit) value [{cre_value}] or (debt) account [{deb_account}] is None. Neither can be None."
    raise ValueError(errmsg)
  if cre_value < DECIMAL_ZERO:
    errmsg = f"Error: credit value ({cre_value}) cannot be negative"
    raise ValueError(errmsg)
  # =========================
  if deb_account > DECIMAL_ZERO:
    errmsg = f"Error: debt account ({deb_account}) cannot be positive"
    raise ValueError(errmsg)
  if abs(deb_account) > cre_value:
    deb_account = deb_account + cre_value
    return DECIMAL_ZERO, deb_account
  remaining = deb_account + cre_value
  return remaining, DECIMAL_ZERO


def debt_value_to_debt_account(deb_value: Decimal, deb_account: Decimal) -> Decimal:
  """
  Debts a debt account.
  Debting a debt account is just a sum, and it doesn't produce a remaining.
  """
  # noinspection unreachable-code
  if deb_value is None or deb_account is None:
    errmsg = f"Error: either (debt) value [{deb_value}] or (debt) account [{deb_account}] is None. Neither can be None."
    raise ValueError(errmsg)
  if deb_value > DECIMAL_ZERO:
    errmsg = f"Error: debt value ({deb_value}) cannot be positive"
    raise ValueError(errmsg)
  if deb_account > DECIMAL_ZERO:
    errmsg = f"Error: debt account ({deb_account}) cannot be positive"
    raise ValueError(errmsg)
  deb_account = deb_account + deb_value  # both are negative
  return deb_account


def debt_value_to_cred_account(deb_value: Decimal, cre_account: Decimal) -> tuple[Decimal, Decimal]:
  """
  Debts a credit account. It may produce a remaining.
  """
  # noinspection unreachable-code
  if deb_value is None or cre_account is None:
    errmsg = f"Error: either value [{deb_value}] or account [{cre_account}] is None. Neither can be None."
    raise ValueError(errmsg)
  if deb_value > DECIMAL_ZERO:
    errmsg = f"debt value ({deb_value}) cannot be positive."
    raise ValueError(errmsg)
  if cre_account < DECIMAL_ZERO:
    errmsg = f"credit account ({cre_account}) cannot be negative."
    raise ValueError(errmsg)
  # ========================
  if abs(deb_value) < cre_account:
    cre_account = cre_account + deb_value  # cre_account is positive, deb_value is negative
    return cre_account, DECIMAL_ZERO
  remaining = cre_account + deb_value
  return DECIMAL_ZERO, remaining


def raise_va_or_zero_or_return_credit_debt_accounts(
    cre_account: Decimal, deb_account: Decimal
  ) -> tuple[Decimal, Decimal]:
  # Here, if any one of the accounts comes in as None, it becomes zero.
  cre_account = DECIMAL_ZERO if cre_account is None else cre_account
  deb_account = DECIMAL_ZERO if deb_account is None else deb_account
  if cre_account < DECIMAL_ZERO:
    errmsg = f"Error: credit account [{cre_account}] cannot be negative."
    raise ValueError(errmsg)
  if deb_account > DECIMAL_ZERO:
    errmsg = f"Error: debt account ({deb_account}) cannot be positive."
    raise ValueError(errmsg)
  return cre_account, deb_account


def credit_value_to_accounts(
    cre_value: Decimal, cre_account: Decimal, deb_account: Decimal
  ) -> tuple[Decimal, Decimal]:
  """
  Credits value to debt account and then, if remaining, to credit account.
  Here, if any of the accounts comes in as None, it becomes zero.

  Receives triple (value, credit_account, debt_account)
  Calculates resultant cred_account, deb_account
  """
  # noinspection unreachable-code
  if cre_value is None:
    errmsg = f"Error: credit value ({cre_value}) is None."
    raise ValueError(errmsg)
  cre_account, deb_account = raise_va_or_zero_or_return_credit_debt_accounts(cre_account, deb_account)
  # ========================
  intermediate_cre_value = credit_value_to_cred_account(cre_value, cre_account)
  new_cre_account, new_deb_account = credit_value_to_debt_account(intermediate_cre_value, deb_account)
  return new_cre_account, new_deb_account


def debt_value_to_accounts(
    deb_value: Decimal, cre_account: Decimal, deb_account: Decimal
  ) -> tuple[Decimal, Decimal]:
  """
  Debts value to credit account and then, if remaining, to debt account.
  Here, if any of the accounts comes in as None, it becomes zero.

  Receives triple (value, credit_account, debt_account)
  Calculates resultant cred_account, deb_account
  """
  # noinspection unreachable-code
  if deb_value is None:
    errmsg = f"Error: debt value ({deb_value}) is None"
    raise ValueError(errmsg)
  cre_account, deb_account = raise_va_or_zero_or_return_credit_debt_accounts(cre_account, deb_account)
  # ========================
  intermediate_deb_value = debt_value_to_debt_account(deb_value, deb_account)
  new_cre_account, new_deb_account = debt_value_to_cred_account(intermediate_deb_value, cre_account)
  return new_cre_account, new_deb_account


def credit_or_debt_value_to_accounts(
    value: Decimal, cre_account: Decimal, deb_account: Decimal
  ) -> tuple:
  """
  Credits or debts value to credit and/or debt accounts.

  To credit, here, is conventioned as a 'plus' operation
    and also credit_value must be a positive value
    (otherwise it's a debt operation).

  Observations:
  =============

  if account is positive, the whole credit goes into account
  else, if account is negative, the crediting must check:
    a) if it's less than the abs(account_value), credit it all
    b) otherwise, if it's greater than the abs(account_value),
       zero account_value and return the 'remainings'
  """
  # noinspection unreachable-code
  if value is None:
    errmsg = f"Error: value [{value}] (credit or debt) is None."
    raise ValueError(errmsg)
  cre_account, deb_account = raise_va_or_zero_or_return_credit_debt_accounts(cre_account, deb_account)
  if value == DECIMAL_ZERO:
    return cre_account, deb_account
  if value > DECIMAL_ZERO:
    return credit_value_to_accounts(value, cre_account, deb_account)
  return debt_value_to_accounts(value, cre_account, deb_account)


def get_brl_dinero(value):
  """
  DEPRECATED (in the sense of no longer used)
  In this app, Dinero has become Decimal
  """
  if isinstance(value, Decimal):
    return value
  try:
    flo = float(value)
    din = Dinero(flo, BRL)
    return din
  except ValueError:
    pass
  try:
    strvalue = str(value)
    # if strvalue is a representation of Dinero, it may contain ',' for thousands
    # which should be removed or else a dinero.exceptions.InvalidOperationError exception will be raised
    strvalue = strvalue.replace(',', '')
    din = Dinero(strvalue, BRL)
    return din
  except dinero.exceptions.InvalidOperationError as e:
    errmsg = f"Error: The value {value} (type {type(value)}) is not a valid dinero."
    raise ValueError(errmsg + str(e))


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
