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
DEFAULT_FIX_IR_DEC = Decimal('0.02')


class PaymentProcessor:
  """
  Contains 'logic' to process a monthly payment obligation
    having a due-window-day-range for payment and if
    payment happens in the rest of the month process an incident mora.
  """

  def __init__(
      self,
      ongoing_debt: Decimal,
      duedate: datetime.date,
      fix_ir_dec: Decimal = DEFAULT_FIX_IR_DEC,
      has_ipca: bool = True
    ) -> None:
    self.ongoing_debt: Decimal = ongoing_debt
    self.duedate: datetime.date = duedate
    self.fix_ir_dec: Decimal = fix_ir_dec
    self.has_ipca: bool = has_ipca
    # a list of payment objects that contain date and value
    self.payments: list[intrfc.PaymentInterfaceDateNValue] = []
    # a copy of tardy payments that are pop'ped() on processing
    self.ongo_tardy_payments: list[intrfc.PaymentInterfaceDateNValue] = []
    self._retrodate_ifinmora: Optional[datetime.date] = None
    self._postdate_ifinmora: Optional[datetime.date] = None
    self.credito_no_fecho: Optional[Decimal] = None
    self.debito_no_fecho: Optional[Decimal] = None
    self.monthmoras: list[moram.SameMonthMora] = []
    self._total_paid_ondate: Optional[Decimal] = None
    self.ongoing_credit: Decimal = DECIMAL_ZERO
    self.ongoing_date: datetime.date = None
    self.payment_process_finished: bool = False

  @property
  def total_paid_ondate(self) -> Decimal:
    if self._total_paid_ondate is not None:
      return self._total_paid_ondate
    self._total_paid_ondate = DECIMAL_ZERO
    paid_ondate_lst = [p.value for p in self.payments if p.date <= self.duedate]
    self._total_paid_ondate = Decimal(sum(paid_ondate_lst))
    return self._total_paid_ondate

  def total_paid_inmonth(self) -> Decimal:
    paid_lst = [p.value for p in self.payments]
    _total_paid_inmonth = Decimal(sum(paid_lst))
    return self._total_paid_inmonth

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
  def cre_deb_moras_tuple(self) -> tuple[Decimal, Decimal, list[moram.SameMonthMora]]:
    _cre_deb_moras_tuple = self.ongoing_credit, self.ongoing_debt, self.monthmoras
    return _cre_deb_moras_tuple

  def process_tardy_payments(self):
    """
    Processes payment(s) that were made later (tardy) than duedate.

    Notes on the 'window of payment' and, if payment is tardy, 'mora'
    ========

    When not in mora, a payment window (date range) opens.
    However, if duedate is overtaken, for tardy payments the payment window
      'retrodates' and becomes itself a 'mora' period
      together with the days after dueday
      (the whole month in fact because refmonth is M-1, i.e., the previous month.).

    The general case is the following:
      a) if dueday is the 10th of the month
      b) if a payment 'overtook' duedate
      c) then retroday goes back to the 1st day of month
      d) and postday goes either to paydate or,
         if it is debt remaining, the last day of the month.
      In fact, postday dynamically moves, with payments if any, towards the end of month.
    """
    # safeguard condition
    if self.ongoing_debt >= DECIMAL_ZERO:
      errmsg = (f"Error: debito_em_mora (={self.ongoing_debt:.2f}) cannot be greater than zero"
                f" in tardy payments")
      raise ValueError(errmsg)
    # at this point: debito_em_mora < DECIMAL_ZERO
    self.credit_tardy_payments_ifany()
    # at this point, all payments were processed and a last look at ongoing_debt is needed
    if self.ongoing_debt < DECIMAL_ZERO:
      self.treat_last_mora_after_all_payments_credited()

  def mk_n_get_monthmora_w_todate(self, todate):
    if self.ongoing_date is None:
      self.ongoing_date = self.retrodate_ifinmora
    monthmora = moram.SameMonthMora(
      fromdate=self.ongoing_date,
      todate=todate,
      prevalue=self.ongoing_debt,  # this is negative
      fix_ir_dec=self.fix_ir_dec,
      has_ipca=self.has_ipca,
    )
    self.ongoing_date = todate
    return monthmora

  def credit_tardy_payments_ifany(self):
    """
    Credits tardy payments if any.
    """
    while len(self.ongo_tardy_payments) > 0:
      payment = self.ongo_tardy_payments.pop(0)
      payvalue = payment.value
      paydate = payment.date
      monthmora = self.mk_n_get_monthmora_w_todate(paydate)
      self.monthmoras.append(monthmora)
      # montnsmora.increase must be negative as ongoing_debt is
      self.ongoing_credit, self.ongoing_debt = cdfs.debt_value_to_accounts(
        value=monthmora.increase, cre_account=self.ongoing_credit, deb_account=self.ongoing_debt
      )
      self.ongoing_credit, self.ongoing_debt = cdfs.credit_value_to_accounts(
        value=payvalue, cre_account=self.ongoing_credit, deb_account=self.ongoing_debt
      )

  def treat_last_mora_after_all_payments_credited(self):
    """
    At this point, there may still be debt after duedate and processed payments.
    This is the last 'mora' to be considered if debt is still < 0.
    """
    if self.ongoing_date == self.postdate_ifinmora:
      return
    if self.ongoing_credit >= DECIMAL_ZERO:
      return
    todate = self.postdate_ifinmora
    monthmora = self.mk_n_get_monthmora_w_todate(todate)
    self.monthmoras.append(monthmora)
    self.ongoing_credit, self.ongoing_debt = cdfs.debt_value_to_accounts(
      value=monthmora.increase, cre_account=self.ongoing_credit, deb_account=self.ongoing_debt
    )

  def treat_no_payments_happened(self):
    """
    Treats the case when no payments were made.
    """
    todate = self.postdate_ifinmora
    monthmora = self.mk_n_get_monthmora_w_todate(todate)
    self.monthmoras.append(monthmora)
    self.ongoing_credit, self.ongoing_debt = cdfs.debt_value_to_accounts(
      value=monthmora.increase, cre_account=DECIMAL_ZERO, deb_account=self.ongoing_debt
    )
    self.treat_last_mora_after_all_payments_credited()

  def treat_payments_ondate_ifany(self):
    """
    This method contains a function that credits the total paid to two accounts:
      a) 'cre_acc' - beginning with zero;
      b) 'deb_acc' - beginning with the month's charge (ongoing_debt at the beginning);

    The result of crediting is:
      if it pays exact, both cre_acc and deb_acc will be = 0  (there's no beginning credit, only a beginning debt)
      if it pays below, deb will be < 0 (negative)
      if it pays above, cre will be > 0 (positive)
    """
    credit_value = self.total_paid_ondate
    self.ongoing_credit, self.ongoing_debt = cdfs.credit_value_to_accounts(
      value=credit_value, cre_account=DECIMAL_ZERO, deb_account=self.ongoing_debt
    )
    if self.ongoing_debt < DECIMAL_ZERO and self.ongoing_credit > 0:
      # oh, oh error!
      cre, deb = self.ongoing_credit, self.ongoing_debt
      errmsg = f"Error: credit (={cre}) and debt (={deb}) upon ondate payment(s) cannot both have values."
      raise ValueError(errmsg)

  def credito_no_fecho(self) -> Decimal | None:
    if self.payment_process_finished:
      return self.ongoing_credit
    return None

  def debito_no_fecho(self) -> Decimal | None:
    if self.payment_process_finished:
      return self.ongoing_debtt
    return None

  def raise_va_if_debt_is_positive(self):
    if self.ongoing_debt > DECIMAL_ZERO:
      errmsg = f"Error: debt (={self.ongoing_debt}) cannot be greater than DECIMAL_ZERO"
      raise ValueError(errmsg)

  def credit_tardy_payments_if_any(self):
    """
    Credits tardy payments, if any, after ongoing_debt has been fully paid.
    """
    if self.ongoing_debt < DECIMAL_ZERO:
      errmsg = (f"Error: ongoing debt ({self.ongoing_debt}) cannot be less than ZERO"
                f" in credit_tardy_payments_if_any()")
      raise ValueError(errmsg)
    while len(self.ongo_tardy_payments) > 0:
      tardy_payment = self.ongo_tardy_payments.pop(0)
      self.ongoing_credit += tardy_payment.value

  def process_payments_in_month(self):
    """
    This method starts the processing of a (monthly) debt value against payment(s).
    The processing ends with the formation of the triple:
      t1 credito_no_fecho, t2 debito_no_fecho, t3 monthmoras
    or
      t1 ongoing_credit, t2 ongoing_debt, t3 monthmoras

    This function uses a 'subsystem' (a functions module) that does the credit/debt calculation.
    The 'process' respects duedate and outdated payments,
      the latter on which 'mora' is incident.
    """
    if self.payment_process_finished:
      print('Method process_payments_in_month() already run. Returning.')
      return
    # debt cannot be positive at the beginning
    self.raise_va_if_debt_is_positive()
    if len(self.payments) == 0:
      self.treat_no_payments_happened()
      self.payment_process_finished = True
      return
    self.treat_payments_ondate_ifany()
    self.ongo_tardy_payments = [p for p in self.payments if p.date > self.duedate]
    if self.ongoing_debt >= DECIMAL_ZERO:
      self.credit_tardy_payments_if_any()
    else:
      self.process_tardy_payments()
    self.treat_last_mora_after_all_payments_credited()
    self.payment_process_finished = True


def adhoctest1():
  print("The adhoctests are in the same folder as are the unit-tests.")


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
