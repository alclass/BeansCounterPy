#!/usr/bin/env python3
"""
art/financdivers/compoundedinterestWithInputsNWithdrawals.py

# import datetime
# import lib.db.dbasfolder.lookup_monthrange_convention_from_basedatafolder_on as find
# import models.banks.banksgeneral
# import models.banks.extractdistributor as extrdistr
"""
import sys
import lib.datesetc.datefs as dtfs
DEFAULT_BANK3LETTER = 'bdb'
DEFAULT_YEAR = 2023


def compound_interest_with_temporal_changes(
    principal,
    rate,
    compounding_periods,
    years,
    periodic_changes=None
):
  """
  Calculates compound interest with additional periodic deposits or withdrawals.

  Args:
      principal (float): The initial amount of money.
      rate (float): The annual interest rate as a decimal (e.g., 0.05 for 5%).
      compounding_periods (int): The number of times the interest is compounded per year.
      years (int): The number of years to calculate for.
      periodic_changes (dict, optional): A dictionary of changes to the principal,
          where the key is the period number (starting from 1) and the value
          is the amount to add or subtract. Positive for deposits, negative for withdrawals.
          Defaults to None.

  Returns:
      list: A list of tuples, where each tuple contains the period number and the
            balance at the end of that period.
  """
  balance = principal
  results = []
  total_periods = compounding_periods * years
  periodic_rate = rate / compounding_periods

  if periodic_changes is None:
    periodic_changes = {}

  for period in range(1, total_periods + 1):
    # Add any periodic changes for the current period
    if period in periodic_changes:
      balance += periodic_changes[period]

    # Calculate and add interest for the current period
    interest = balance * periodic_rate
    balance += interest

    results.append((period, round(balance, 2)))

  return results


class CompoundedInterest:

  def __init__(
    self,
    initial_principal,
    annual_rate,
    compounds_per_year,
    total_years,
    periodic_ins_n_outs_dict  # = temporal_changes
  ):
    self.initial_principal = initial_principal
    self.annual_rate = annual_rate
    self.compounds_per_year = compounds_per_year
    self.periodic_ins_n_outs_dict = periodic_ins_n_outs_dict or {}
    self.total_years = total_years
    self.results_with_changes = None

  @property
  def total_periods(self):
    return self.compounds_per_year * self.total_years

  def add_monthly_in_or_out(self, seq_period, montant):
    """
    add_monthly_in_or_out (deposit or withdrawal)
    if montant > 0, it's a deposit
    if montant < 0, it's a withdrawal
    seq_period, montant
    """
    previous_montant = 0
    if seq_period in self.periodic_ins_n_outs_dict:
      previous_montant = self.periodic_ins_n_outs_dict[seq_period]
    self.periodic_ins_n_outs_dict[seq_period] = previous_montant + montant

  def remove_monthly_in_or_out_by_seq(self, seq_period):
    try:
      del self.periodic_ins_n_outs_dict[seq_period]
    except IndexError:
      pass

  def compound_interest_with_temporal_changes(self):
    self.results_with_changes = compound_interest_with_temporal_changes(
      principal=self.initial_principal,
      rate=self.annual_rate,
      compounding_periods=self.compounds_per_year,
      years=self.total_years,
      periodic_changes=self.periodic_ins_n_outs_dict,
    )

  def process(self):
    self.compound_interest_with_temporal_changes()

  def __str__(self):
    outstr = f"""[{self.__class__.__name__}]
    initial_principal = {self.initial_principal}
    annual_rate = {self.annual_rate}
    compounds_per_year = {self.compounds_per_year}
    total_years = {self.total_years}
    periodic_changes = {self.periodic_ins_n_outs_dict}
    # ====================================
    [calculated]
    results_with_changes={self.results_with_changes}
    """
    return outstr


def example_usage():
  # Example usage
  # Scenario: An initial principal of $1000, 5% annual interest compounded quarterly for 5 years.
  # Additional deposit of $500 in period 5.
  initial_principal = 1000.0
  annual_rate = 0.05
  compounds_per_year = 4
  total_years = 5

  temporal_changes = {
    5: 500  # A deposit of $500 at the end of the 5th period (1.25 years)
  }

  results_with_changes = compound_interest_with_temporal_changes(
    initial_principal,
    annual_rate,
    compounds_per_year,
    total_years,
    periodic_changes=temporal_changes
  )

  print("Compound interest calculation with temporal changes:")
  scrmsg = f"""
  initial_principal = {initial_principal}
  annual_rate = {annual_rate}
  compounds_per_year = {compounds_per_year}
  total_years = {total_years}
  temporal_changes = {temporal_changes}
  """
  print(scrmsg)
  for period, balance in results_with_changes:
    print(f"Period {period}: ${balance}")

  # Example usage 2: Basic compound interest without temporal changes
  initial_principal = 1000.0
  annual_rate = 0.05
  compounds_per_year = 1  # Annually
  total_years = 8

  results_simple = compound_interest_with_temporal_changes(
    initial_principal,
    annual_rate,
    compounds_per_year,
    total_years
  )

  print("\nBasic compound interest calculation:")
  for year, balance in results_simple:
    print(f"Year {year}: ${balance}")


def get_args_or_defaults():
  bank3letter = DEFAULT_BANK3LETTER
  refmonthdate_ini, refmonthdate_fim = None, None
  for arg in sys.argv:
    if arg in ['-h', '--help']:
      print(__doc__)
      sys.exit(0)
    elif arg.startswith('-b3l='):
      bank3letter = arg[len('-b3l='):]
    elif arg.startswith('-dmdini='):
      refmonthdate_ini = arg[len('-dmdini='):]
    elif arg.startswith('-dmdfim='):
      refmonthdate_fim = arg[len('-dmdfim='):]
  yyyydashmms = (refmonthdate_ini, refmonthdate_fim)
  rmdrange = dtfs.transform_yyyydashmm_to_daterange_from_strlist_or_recentyear(yyyydashmms)
  argdict = {'bank3letter': bank3letter, 'rmdrange': rmdrange}
  return argdict


def adhoctest3():
  initial_principal = 1000.0
  annual_rate = 0.05
  compounds_per_year = 4
  total_years = 5
  temporal_changes = {
    5: 500  # A deposit of $500 at the end of the 5th period (1.25 years)
  }
  ci = CompoundedInterest(
    initial_principal=initial_principal,
    annual_rate=annual_rate,
    compounds_per_year=compounds_per_year,
    total_years=total_years,
    periodic_ins_n_outs_dict=temporal_changes,
  )
  print('compounded interest =>', ci)


def adhoctest2():
  example_usage()


def adhoctest():
  args = get_args_or_defaults()
  print(args)


def process():
  """
  argdict = get_args_or_defaults()
  """
  pass


if __name__ == '__main__':
  """
  adhoctest()
  process()
  """
  adhoctest3()
