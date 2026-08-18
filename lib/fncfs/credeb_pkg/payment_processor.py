"""
lib/fncfs/credeb_pkg/pay_by_quinhoes_etc.py
  Contains functions that pay a debt directly or by "quinhões"
    (i.e., peacemealwise when monthly mora is partitioned, i.e., it happens across more than one month)

To import PaymentProcessor:
  import lib.fncfs.credeb_pkg.payment_processor as paypro  # paypro.PaymentProcessor

from dataclasses import dataclass
from collections.abc import Iterable
import lib.datesetc.datefs as dtfs
# for fncfs.calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fncfs
"""
import calendar
from decimal import Decimal, Context, ROUND_HALF_UP
import datetime
from typing import Optional
import lib.fncfs.credeb_pkg.credit_debit_fs as cdfs  # cdfs.debit_value_to_accounts
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.fncfs.credeb_pkg.samemonthmora_classes as moram  # moram.SameMonthMora
DECIMAL_ZERO = Decimal('0')


class PaymentProcessor:
  """
  Contains 'logic' to process a monthly payment obligation
    having a due-window-day-range for payment and the rest
    of the month an incident mora.
  """

  def __init__(
      self,
      ongoing_debt: Decimal,
      duedate: datetime.date,
      fix_ir_dec: Decimal,
      has_ipca: bool
    ) -> None:
    self.ongoing_debt: Decimal = ongoing_debt
    self.duedate: datetime.date = duedate
    self.fix_ir_dec: Decimal = fix_ir_dec or Decimal(0.02)
    self.has_ipca: bool = True
    # we'll only need date and value from a payment object
    self.payments: list[intrfc.PaymentInterfaceDateNValue] = []
    self._retrodate_ifinmora: Optional[datetime.date] = None
    self._postdate_ifinmora: Optional[datetime.date] = None
    self.credito_no_fecho: Optional[Decimal] = None
    self.debito_no_fecho: Optional[Decimal] = None
    self.monthmoras: list[moram.SameMonthMora] = []
    self.has_ipca: bool = has_ipca
    self.total_payvalue_ondate: Decimal = DECIMAL_ZERO

  @property
  def retrodate_ifinmora(self) -> datetime.date:
    """
    The date from which mora duration starts.
    When in mora, its time-span (duration) goes before duedate
      down to the first day of the month.

    Example:
      a) suppose the 'window' of payment is from the 1st to the 10th of the month;
      b) if payment happens within this pay-window, it's on duetime and ;
      c) if it happens later/tardy, the 'mora' is counted from day 1
    """
    if self._retrodate_ifinmora is not None:
      return self._retrodate_ifinmora
    year, month = self.duedate.year, self.duedate.month
    monthsfirstdaydate = datetime.date(year=year, month=month, day=1)
    self._retrodate_ifinmora = monthsfirstdaydate
    return self._retrodate_ifinmora

  @property
  def postdate_ifinmora(self) -> datetime.date:
    """
    The date to which mora duration ends.
    When in months mora, this ending duration may be two:
      a) it's either the pay date itself;
      b) or, if value remains unpaid, it's the last day of the month;
    """
    if self._postdate_ifinmora is not None:
      return self._postdate_ifinmora
    year, month = self.duedate.year, self.duedate.month
    _, lastdayinmonth = calendar.monthrange(year, month)
    monthslastdaydate = datetime.date(year=year, month=month, day=lastdayinmonth)
    self._postdate_ifinmora = monthslastdaydate
    return self._postdate_ifinmora

  @property
  def tupl_cre_deb_moras(self) -> tuple[Decimal, Decimal, list[moram.SameMonthMora]]:
    tupl = self.credito_no_fecho, self.debito_no_fecho, self.monthmoras
    return tupl

  def process_payment_under_mora(self):
    """
    All input dates for this function must be in the same month.

    Explanation of retrodate_ifinmora and postdate_ifinmora:
    ==============
      retrodate_ifinmora applies only when in mora.
      The same with postdate_ifinmora.

      When in mora, a payment window (date range) opens.
      However, if duedate is overtaken, the payment window
        becomes a 'mora' moment together with the days after
        dueday (the whole month in fact for refmonth is M-1).
      The general case is the following:
        a) if dueday is the 10th of the month
        b) if a payment 'overtook' duedate
        c) then retroday goes back to the 1st day of month
        d) and postday goes either to paydate or, if remaisn, last day of the month
    """
    if self.ongoing_debt > DECIMAL_ZERO:
      errmsg = f"Error: debito_em_mora (={self.ongoing_debt:.2f}) cannot be greater than zero"
      raise ValueError(errmsg)
    elif self.ongoing_debt == DECIMAL_ZERO:
      self.monthmoras = []
      self.credito_no_fecho = DECIMAL_ZERO
      self.debito_no_fecho = DECIMAL_ZERO
      return self.credito_no_fecho, self.debito_no_fecho, self.monthsmora
    # at this point: debito_em_mora < DECIMAL_ZERO
    self.credito_no_fecho = DECIMAL_ZERO
    return self.treat_debito_em_mora()

  def mk_n_get_monthmora_w_todate(self, todate):
    pdate = todate
    monthmora = moram.SameMonthMora(
      fromdate=self.retrodate_ifinmora,
      todate=todate,
      prevalue=self.ongoing_debt,  # this is negative
      fix_ir_dec=self.fix_ir_dec,
      has_ipca=self.has_ipca,
    )
    return monthmora

  def credit_payments(self):
    payments = self.payments[:]  # copy it
    monthsmoras = []  # quinhoes_days_vals = []
    while len(payments) > 0:
      payment = payments.pop(0)
      payvalue = payment.value
      paydate = payment.date
      if self.ongoing_debt > DECIMAL_ZERO:
        self.mk_n_get_monthmora_w_todate(paydate)
        # montnsmora.increase must be negative as ongoing_debt is
        self.ongoing_debt = self.ongoing_debt + monthmora.increase
        self.monthmoras.append(monthmora)
        self.ongoing_debt = self.ongoing_debt + payvalue  # notice pay is positive, debito is negative
        if self.ongoing_debt > DECIMAL_ZERO:
          # debito has been paid
          self.credito_no_fecho += self.ongoing_debt
          self.debito_no_fecho = DECIMAL_ZERO
          break
      else:  # debito has been paid
        self.credito_no_fecho += payvalue
      # loop on if while condition is still true (more payments in queue)

  def treat_debt_after_payments_credited(self):
    todate = self.retrodate_ifinmora
    monthmora = self.mk_n_get_monthmora_w_todate(todate)
    self.monthmoras.append(monthmora)
    self.ongoing_debt = self.ongoing_debt + monthmora.increase
    self.debito_no_fecho = self.ongoing_debt
    self.credito_no_fecho = DECIMAL_ZERO

  def treat_debito_em_mora(self):
    self.credit_payments()
    # at this point, payments were considered,
    # debito may or may not yet exist,
    # however, if it does, it must mora-increase
    # from retrodate_ifinmora to postdate_ifinmora (generally the full month)
    if self.ongoing_debt < DECIMAL_ZERO:
      self.treat_debt_after_payments_credited()
    else:
      self.debito_no_fecho = self.ongoing_debt

  def treat_no_payments_happened(self):
    """
    Treats the case when no payments were made.
    """
    self.credito_no_fecho, self.monthmoras = DECIMAL_ZERO, []
    todate = self.postdate_ifinmora
    monthmora = self.mk_n_get_monthmora_w_todate(todate)
    self.monthmoras.append(monthmora)
    self.debito_no_fecho = self.ongoing_debt + monthmora.increase
    return

  def treat_payments_ondate_ifany(self):
    payments_ondate = list(filter(lambda po: po.date <= self.duedate, self.payments))
    payvalues = [p.value for p in payments_ondate]
    self.total_payvalue_ondate = Decimal(sum(payvalues))
    self.credito_no_fecho, self.debito_no_fecho = cdfs.debit_value_to_accounts(self.ongoing_debt, self.total_payvalue_ondate, DECIMAL_ZERO)
    self.credito_no_fecho = DECIMAL_ZERO if self.credito_no_fecho is None else self.credito_no_fecho
    self.debito_no_fecho = DECIMAL_ZERO if self.debito_no_fecho is None else self.debito_no_fecho

  def calc_mora_on_residual_debt(self):
    """
    There is still a debt residue after payments processed.
    """
    todate = self.postdate_ifinmora
    monthmora = self.mk_n_get_monthmora_w_todate(todate)
    self.monthmoras.append(monthmora)
    self.ongoing_debt = self.ongoing_debt + monthmora.increase
    self.debito_no_fecho = self.ongoing_debt

  def treat_payments_tardy_ifany(self):
    """
    Treats the case when payments made were tardy.
    """
    pays_tardy = list(filter(lambda po: po.date > self.duedate, self.payments))
    if len(pays_tardy) == 0:
      # all payments, if any, were in duedate, but we still have to check debito_no_fecho
      self.monthmoras = []
      if self.debito_no_fecho < DECIMAL_ZERO:
        # there should be a 'mora-projection' from retro to post date
        self.calc_mora_on_residual_debt()
        return
      if self.ongoing_debt > DECIMAL_ZERO:
        # move excess to credit
        self.credito_no_fecho

  def raise_if_debt_is_positive(self):
    if self.ongoing_debt > DECIMAL_ZERO:
      errmsg = f"Error: debt (={self.ongoing_debt}) cannot be greater than DECIMAL_ZERO"
      raise ValueError(errmsg)

  def process_payments_in_month(self):
    """
    This function receives a debt value and a list of payments.
    It outputs two values: credito_no_fecho, debito_no_fecho
      credito_no_fecho is an excedent out of the payments
      debito_no_fecho signals that the payment was not completed

    This function uses a 'subsystem' that does the credit/debit calculation.
    The 'process' respects duedate and outdated payments,
      on the latter 'mora' is incident.
    """
    self.raise_if_debt_is_positive()
    if len(self.payments) == 0:
      self.treat_no_payments_happened()
      return
    self.treat_payments_ondate_ifany()
    self.treat_payments_out_of_date_ifany()

  def treat_payments_out_of_date_ifany(self):
    if self.credito_no_fecho > DECIMAL_ZERO:
      # notice that credito is always positive, debito is always negative
      # if one of them has value, the other must be zeroed
      if self.debito_no_fecho != DECIMAL_ZERO:
        # oh, oh, error
        errmsg = f"Error: debt (={self.debito_no_fecho}) cannot be different from zero when credito exists."
        raise ValueError(errmsg)
      return
    if self.ongoing_debt < DECIMAL_ZERO:
      self.process_payment_under_mora()


def adhoctest1():
  print("The adhoctests are in the same folder as are the unit-tests.")


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
