#!/usr/bin/env python3
"""
lib/fncfs/dinerofs/credit_debit_fs.py

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


def compensate_cred_deb_accounts_one_against_the_other(
    cred_account: Decimal, deb_account: Decimal,
  ):
  """
  Compensates credit account with debit account (or viceversa)

  input: credit_account, debit_account
  output: new_credit_account, new_debit_account

  Example:
    ex1:
      input:
        cred_account = 100
        deb_account = -200
      output:
        new_cred_account = 0
        new_deb_account = -100
    ex2:
      input:
        cred_account = 200
        deb_account = -100
      output:
        new_cred_account = 100
        new_deb_account = 0
    ex3:
      input:
        cred_account = 100
        deb_account = -100
      output:
        new_cred_account = 0
        new_deb_account = 0
  """
  if cred_account is None or deb_account is None:
    errmsg = f"Error: either cred_account [{cred_account}] or deb_account [{deb_account}] is None"
    raise ValueError(errmsg)
  if cred_account < DECIMAL_ZERO:
    errmsg = f"credit_account ({cred_account}) cannot be negative"
    raise ValueError(errmsg)
  if deb_account > DECIMAL_ZERO:
    errmsg = f"deb_account ({cred_account}) cannot be positive"
    raise ValueError(errmsg)
  # ========================
  # if hypothesis is not met, return their same values
  new_cred_account, new_deb_account = cred_account, deb_account
  if cred_account > DECIMAL_ZERO:
    if deb_account < DECIMAL_ZERO:
      remaining = cred_account + deb_account
      if remaining > DECIMAL_ZERO:
        new_cred_account = remaining
        new_deb_account = DECIMAL_ZERO
      else:
        new_deb_account = remaining
        new_cred_account = DECIMAL_ZERO
  return new_cred_account, new_deb_account


def credit_value_to_cred_account(value: Decimal, account: Decimal) -> Decimal:
  """
  Crediting a cred account is just a sum, and it doesn't produce a remaining.
  """
  if value is None or account is None:
    errmsg = f"Error: either value [{value}] or account [{account}] is None"
    raise ValueError(errmsg)
  if value < DECIMAL_ZERO:
    errmsg = f"credit_value ({value}) cannot be negative"
    raise ValueError(errmsg)
  if account < DECIMAL_ZERO:
    errmsg = f"cred account ({value}) cannot be negative"
    raise ValueError(errmsg)
  account = account + value
  return account


def credit_value_to_deb_account(value: Decimal, account: Decimal) -> tuple[Decimal, Decimal]:
  """
  Crediting a debt account may produce a remaining
  """
  if value is None or account is None:
    errmsg = f"Error: either value [{value}] or account [{account}] is None"
    raise ValueError(errmsg)
  if value < DECIMAL_ZERO:
    errmsg = f"credit_value ({value}) cannot be negative"
    raise ValueError(errmsg)
  # =========================
  if account > DECIMAL_ZERO:
    errmsg = f"deb account ({value}) cannot be positive"
    raise ValueError(errmsg)
  if abs(account) > value:
    account = account + value
    return DECIMAL_ZERO, account
  remaining = account + value
  return remaining, DECIMAL_ZERO


def debit_value_to_deb_account(value: Decimal, account: Decimal) -> Decimal:
  """
  Debting a debt account is just a sum, and it doesn't produce a remaining.
  """
  if value is None or account is None:
    errmsg = f"Error: either value [{value}] or account [{account}] is None"
    raise ValueError(errmsg)
  if value > DECIMAL_ZERO:
    errmsg = f"debit value ({value}) cannot be positive"
    raise ValueError(errmsg)
  if account > DECIMAL_ZERO:
    errmsg = f"deb account ({value}) cannot be positive"
    raise ValueError(errmsg)
  account = account + value  # both are negative
  return account


def debit_value_to_cred_account(value: Decimal, account: Decimal) -> tuple[Decimal, Decimal]:
  """
  Debting a cred account may produce a remaining
  """
  if value is None or account is None:
    errmsg = f"Error: either value [{value}] or account [{account}] is None"
    raise ValueError(errmsg)
  if value > DECIMAL_ZERO:
    errmsg = f"debit value ({value}) cannot be positive"
    raise ValueError(errmsg)
  if account < DECIMAL_ZERO:
    errmsg = f"cred account ({value}) cannot be negative"
    raise ValueError(errmsg)
  # ========================
  if abs(value) < account:
    account = account + value  # account is positive, value is negative
    return DECIMAL_ZERO, account
  remaining = account + value
  return remaining, DECIMAL_ZERO


# noinspection PyTypeChecker
def credit_value_to_accounts(
    value: Decimal, cred_account: Decimal, deb_account: Decimal
  ) -> tuple:
  if value is None:
    errmsg = f"Error: debit ({value}) is None"
    raise ValueError(errmsg)
  if value < DECIMAL_ZERO:
    errmsg = f"credit_value ({value}) cannot be negative"
    raise ValueError(errmsg)
  if cred_account is None and deb_account is None:
    errmsg = "both cred account and deb account cannot be None."
    raise ValueError(errmsg)
  # ========================
  if deb_account is None:
    cred_account = credit_value_to_cred_account(value, cred_account)
    return cred_account, None
  remaining, deb_account = credit_value_to_deb_account(value, deb_account)
  cred_account += remaining
  return cred_account, deb_account


def debit_value_to_accounts(
    value: Decimal, cred_account: Decimal, deb_account: Decimal
  ) -> tuple[Decimal | None, Decimal | None]:
  """
  Receives tripe value, credit account, debit account
  Calculates resultant cred_account, deb_account
  """
  if value is None:
    errmsg = f"Error: debit ({value}) is None"
    raise ValueError(errmsg)
  if cred_account is None and deb_account is None:
    errmsg = "Error: both cred account and deb account cannot be None."
    raise ValueError(errmsg)
  if value > DECIMAL_ZERO:
    errmsg = f"Error: debit ({value}) cannot be positive"
    raise ValueError(errmsg)
  if cred_account and cred_account < DECIMAL_ZERO:
    errmsg = f"Error: cred account [{cred_account}] cannot be negative."
    raise ValueError(errmsg)
  if deb_account and deb_account > DECIMAL_ZERO:
    errmsg = f"Error: deb account [{deb_account}] cannot be positive."
    raise ValueError(errmsg)
  # ========================
  if cred_account is None:
    deb_account = debit_value_to_deb_account(value, deb_account)
    return None, deb_account
  remaining, cred_account = debit_value_to_cred_account(value, cred_account)
  deb_account = deb_account + remaining
  return cred_account, deb_account


def debit_or_credit_value_to_accounts(
    value: Decimal, cred_account: Decimal, deb_account: Decimal
  ) -> tuple:
  """
    To credit, here, is conventioned as a 'plus' operation
      and also credit_value must be a positive value
      (otherwise it's a debit operation).

    Observations:
    =============

    if account is positive, the whole credit goes into account
    else, if account is negative, the crediting must check:
      a) if it's less than the abs(account_value), credit it all
      b) otherwise, if it's greater than the abs(account_value),
         zero account_value and return the 'remainings'
  """
  if value is None:
    errmsg = f"Error: value [{value}] (cred or deb) is None"
    raise ValueError(errmsg)
  if value == DECIMAL_ZERO:
    return cred_account, deb_account
  if value > DECIMAL_ZERO:
    return credit_value_to_accounts(value, cred_account, deb_account)
  return debit_value_to_accounts(value, cred_account, deb_account)


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
  scrmsg = f"""{__name__} | {__file__}:
  The adhoctests were moved to a module of their own.
  At the time of writing, this module:
    lib/fncfs/dinerofs/adhoctests/ahdoctest_credit_debit_fs.py
  (it cannot be executed from here due to circular imports)
  (execute it from its module [ahdoctest_credit_debit_fs.py] 'there'.)
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
