#!/usr/bin/env python3
"""
lib/finfs/dinerofs/credit_debit_fs.py

"""
from dinero import Dinero
from dinero.currencies import BRL
DINERO_ZERO = Dinero(str("0"), BRL)


def compensate_cred_deb_accounts_one_against_the_other(
    cred_account: Dinero, deb_account: Dinero,
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
  if cred_account < DINERO_ZERO:
    errmsg = f"credit_account ({cred_account}) cannot be negative"
    raise ValueError(errmsg)
  if deb_account > DINERO_ZERO:
    errmsg = f"deb_account ({cred_account}) cannot be positive"
    raise ValueError(errmsg)
  # ========================
  # if hypothesis is not met, return their same values
  new_cred_account, new_deb_account = cred_account, deb_account
  if cred_account > DINERO_ZERO:
    if deb_account < DINERO_ZERO:
      remaining = cred_account + deb_account
      if remaining > DINERO_ZERO:
        new_cred_account = remaining
        new_deb_account = DINERO_ZERO
      else:
        new_deb_account = remaining
        new_cred_account = DINERO_ZERO
  return new_cred_account, new_deb_account


def credit_value_to_cred_account(value: Dinero, account: Dinero) -> Dinero:
  """
  Crediting a cred account is just a sum, and it doesn't produce a remaining.
  """
  if value is None or account is None:
    errmsg = f"Error: either value [{value}] or account [{account}] is None"
    raise ValueError(errmsg)
  if value < DINERO_ZERO:
    errmsg = f"credit_value ({value}) cannot be negative"
    raise ValueError(errmsg)
  if account < DINERO_ZERO:
    errmsg = f"cred account ({value}) cannot be negative"
    raise ValueError(errmsg)
  account = account + value
  return account


def credit_value_to_deb_account(value: Dinero, account: Dinero) -> tuple[Dinero, Dinero]:
  """
  Crediting a debt account may produce a remaining
  """
  if value is None or account is None:
    errmsg = f"Error: either value [{value}] or account [{account}] is None"
    raise ValueError(errmsg)
  if value < DINERO_ZERO:
    errmsg = f"credit_value ({value}) cannot be negative"
    raise ValueError(errmsg)
  # =========================
  if account > DINERO_ZERO:
    errmsg = f"deb account ({value}) cannot be positive"
    raise ValueError(errmsg)
  if abs(account.raw_amount) > value.raw_amount:
    account = account + value
    return DINERO_ZERO, account
  remaining = account + value
  return remaining, DINERO_ZERO


def debit_value_to_deb_account(value: Dinero, account: Dinero) -> Dinero:
  """
  Debting a debt account is just a sum, and it doesn't produce a remaining.
  """
  if value is None or account is None:
    errmsg = f"Error: either value [{value}] or account [{account}] is None"
    raise ValueError(errmsg)
  if value > DINERO_ZERO:
    errmsg = f"debit value ({value}) cannot be positive"
    raise ValueError(errmsg)
  if account > DINERO_ZERO:
    errmsg = f"deb account ({value}) cannot be positive"
    raise ValueError(errmsg)
  account = account + value  # both are negative
  return account


def debit_value_to_cred_account(value: Dinero, account: Dinero) -> tuple[Dinero, Dinero]:
  """
  Debting a cred account may produce a remaining
  """
  if value is None or account is None:
    errmsg = f"Error: either value [{value}] or account [{account}] is None"
    raise ValueError(errmsg)
  if value > DINERO_ZERO:
    errmsg = f"debit value ({value}) cannot be positive"
    raise ValueError(errmsg)
  if account < DINERO_ZERO:
    errmsg = f"cred account ({value}) cannot be negative"
    raise ValueError(errmsg)
  # ========================
  if abs(value.raw_amount) < account.raw_amount:
    account = account + value  # account is positive, value is negative
    return DINERO_ZERO, account
  remaining = account + value
  return remaining, DINERO_ZERO


# noinspection PyTypeChecker
def credit_value_to_accounts(
    value: Dinero, cred_account: Dinero, deb_account: Dinero
  ) -> tuple:
  if value is None:
    errmsg = f"Error: debit ({value}) is None"
    raise ValueError(errmsg)
  if value < DINERO_ZERO:
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
    value: Dinero, cred_account: Dinero, deb_account: Dinero
  ) -> tuple:
  if value is None:
    errmsg = f"Error: debit ({value}) is None"
    raise ValueError(errmsg)
  if cred_account is None and deb_account is None:
    errmsg = "Error: both cred account and deb account cannot be None."
    raise ValueError(errmsg)
  if value > DINERO_ZERO:
    errmsg = f"Error: debit ({value}) cannot be positive"
    raise ValueError(errmsg)
  if cred_account and cred_account < DINERO_ZERO:
    errmsg = f"Error: cred account [{cred_account}] cannot be negative."
    raise ValueError(errmsg)
  if deb_account and deb_account > DINERO_ZERO:
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
    value: Dinero, cred_account: Dinero, deb_account: Dinero
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
  if value == DINERO_ZERO:
    return cred_account, deb_account
  if value > DINERO_ZERO:
    return credit_value_to_accounts(value, cred_account, deb_account)
  return debit_value_to_accounts(value, cred_account, deb_account)


def adhoctests():
  scrmsg = f"""{__name__} | {__file__}:
  The adhoctests were moved to a module of their own.
  At the time of writing, this module:
    lib/finfs/dinerofs/adhoctests/ahdoctest_credit_debit_fs.py
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
