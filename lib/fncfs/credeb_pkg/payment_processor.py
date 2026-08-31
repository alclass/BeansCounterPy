"""
lib/fncfs/credeb_pkg/payment_processor.py
  Contains class PaymentProcessor that models payment to monthly debt that include 'mora' after duedate.
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
from decimal import Decimal  # , Context, ROUND_HALF_UP
import datetime
from typing import Optional
import pydantic
from dateutil.relativedelta import relativedelta
import lib.datesetc.refmonth_fs as rmfs  # cdfs.debt_value_to_accounts
import lib.fncfs.credeb_pkg.credit_debt_fs as cdfs  # cdfs.debt_value_to_accounts
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as fncach  # fncach.IpcaAPICacherRetriever
import lib.fncfs.credeb_pkg.samemonthmora as moram  # moram.SameMonthMora
DECIMAL_ZERO = Decimal('0')
DEFAULT_FIX_IR_DEC = Decimal('0.02')


class StepByStepMonthValuesKeeper:
  date: datetime.date
  inivalue: Decimal
  finvalue: Decimal
  credit_values: list[Decimal]
  debtvalue: list[Decimal]
  ndays: int
  debts: list[intrfc.PaymentInterfaceDateNValue]


class PaymentProcessor(pydantic.BaseModel):
  """
  Contains 'logic' to process a monthly payment obligation
    having a due-window-day-range for payment.
  The explanatory description of this process is found
    in the accompanying doc.md in the package.

  # before inherint from pydantic.BaseModel
  def __init__(
      self,
      ongoing_debt: Decimal,
      duedate: datetime.date,
      fix_ir_dec: Decimal = DEFAULT_FIX_IR_DEC,
      has_ipca: bool = True
    ) -> None:

  """
  ongoing_debt: Decimal
  duedate: datetime.date
  fix_ir_dec: Decimal = pydantic.Field(default_factory=lambda: DEFAULT_FIX_IR_DEC)
  payments: list[intrfc.PaymentInterfaceDateNValue] = pydantic.Field(default_factory=lambda: [])  # bipydtc.PydtcPayment
  monthmoras: list[moram.SameMonthMora] = pydantic.Field(default_factory=lambda: [])
  _total_paid_ondate: Optional[Decimal] = None
  _retrodate_ifinmora: Optional[datetime.date] = None
  _postdate_ifinmora: Optional[datetime.date] = None
  ongoing_credit: Optional[Decimal] = DECIMAL_ZERO  # at __init__() time, it's zero
  orig_monthsdebt: Optional[Decimal] = None
  ongoing_date: Optional[datetime.date] = None
  has_ipca: bool = True
  payment_process_finished: bool = False

  @property
  def total_paid_uptoduedate(self) -> Decimal:
    if self._total_paid_ondate is not None:
      return self._total_paid_ondate
    self._total_paid_ondate = DECIMAL_ZERO
    paid_upto_duedate_values = [p.value for p in self.getcp_duedate_payments()]
    self._total_paid_ondate = Decimal(sum(paid_upto_duedate_values))
    # noinspection bad-return
    return self._total_paid_ondate

  def total_paid_inmonth(self) -> Decimal:
    paid_lst = [p.value for p in self.payments]
    _total_paid_inmonth = Decimal(sum(paid_lst))
    return self._total_paid_inmonth

  @property
  def retrodate_ifinmora(self) -> datetime.date:
    """
    Gets the date (inclusive) from which the first mora calculation begins.
    @see <same_module>_doc.md for more information/explanation.
    """
    if self._retrodate_ifinmora is not None:
      return self._retrodate_ifinmora
    year, month = self.duedate.year, self.duedate.month
    monthsfirstdaydate = datetime.date(year=year, month=month, day=1)
    self._retrodate_ifinmora = monthsfirstdaydate
    # noinspection bad-return
    return self._retrodate_ifinmora

  @property
  def postdate_ifinmora(self) -> datetime.date:
    """
    Gets the date (inclusive) to which the last mora calculation ends.
    @see <same_module>_doc.md for more information/explanation.
    """
    if self._postdate_ifinmora is not None:
      return self._postdate_ifinmora
    year, month = self.duedate.year, self.duedate.month
    _, lastdayinmonth = calendar.monthrange(year, month)
    monthslastdaydate = datetime.date(year=year, month=month, day=lastdayinmonth)
    self._postdate_ifinmora = monthslastdaydate
    # noinspection bad-return
    return self._postdate_ifinmora

  @property
  def refmonth(self) -> datetime.date:
    """
    Notice that refmonth is, in general, the previous month to paymonth.
    """
    _refmonth = rmfs.make_refmonth_it_minus_n_or_raise(self.duedate, 1)
    return _refmonth

  @property
  def cre_deb_moras_after_process(self) -> tuple[Decimal | None, Decimal | None, list[moram.SameMonthMora] | None]:
    if not self.payment_process_finished:
      return None, None, None
    _cre_deb_moras_tuple = self.ongoing_credit, self.ongoing_debt, self.monthmoras
    return _cre_deb_moras_tuple

  @property
  def tot_mor_val(self) -> Decimal:
    increases = [mo.increase for mo in self.monthmoras]
    _tot_mor_val = Decimal(sum(increases))
    return _tot_mor_val

  @staticmethod
  def mkstr_payments_as_date_n_value_lines_w_lst(payments) -> str:
    lines = []
    for p in payments:
      line = f"Em {p.date} pagos {p.value}"
      lines.append(line)
    if len(lines) == 0:
      msgsempagt = "Não houve pagamento(s) dentro do prazo."
      return msgsempagt
    optext = '\n'.join(lines)
    return optext

  def getcp_duedate_payments(self) -> list[intrfc.PaymentInterfaceDateNValue]:
    payments = [p for p in self.payments if p.date <= self.duedate]
    return payments

  def getcp_tardy_payments(self) -> list[intrfc.PaymentInterfaceDateNValue]:
    payments = [p for p in self.payments if p.date > self.duedate]
    return payments

  def get_payments_on_daydate(self, pdate) -> list[intrfc.PaymentInterfaceDateNValue]:
    payments = [p for p in self.payments if p.date == pdate]
    return payments

  def mkstr_payments_uptoduedate_as_date_n_value_lines(self) -> str:
    payments = self.getcp_duedate_payments()
    return self.mkstr_payments_as_date_n_value_lines_w_lst(payments)

  def monthly_bill_to_embed_as_dict(self) -> dict:
    """
    The processing when finished (also: closed) is recorded
      embedded in MongoDB's collection doc related to its corresponding 'refmonth' BillingCard.
    Then, fields that are already in the BillingCard must be removed in this selection.
    """
    _ = self
    return {}

  def history_backtrack(self) -> str:
    if not self.payment_process_finished:
      return "Processing has not finished yet. Retry later."
    lines = []
    line = "history_backtrack"
    lines.append(line)
    # noinspection string-format,string-format
    origdebt = f"{self.orig_monthsdebt: .2f}"
    line = f"valor mensal: {origdebt} | total pagt no prazo: {self.total_paid_uptoduedate}"
    lines.append(line)
    line = self.mkstr_payments_uptoduedate_as_date_n_value_lines()
    line += f' | total mora = {self.tot_mor_val:.2f}'
    lines.append(line)
    monthmoras = self.monthmoras[:]
    monthmoras.sort(key=lambda mmo: mmo.todate)
    while len(monthmoras) > 0:
      mm = monthmoras.pop(0)
      line = f"{mm.todate} | mora: {mm.increase} | valor no momento: {mm.prevalue} | ajustado: {mm.postvalue}"
      lines.append(line)
      payments = self.get_payments_on_daydate(mm.todate)
      line = self.mkstr_payments_as_date_n_value_lines_w_lst(payments)
      lines.append(line)
    return '\n'.join(lines)

  def is_monthsbill_fully_paid(self) -> bool | None:
    if not self.payment_process_finished:
      return None
    if self.debito_no_fecho < DECIMAL_ZERO:
      return False
    return True

  def process_tardy_payments_if_any(self) -> None:
    """
    Processes payment(s) that were made later (or tardier)
      than duedate.
    @see <same_module>_doc.md for more information/explanation.
    """
    # safeguard condition
    tardypayments = self.getcp_tardy_payments()
    if len(tardypayments) == 0:
      return
    # tardypayments is not supposed to be a 'huge' list
    # so it's not an efficiency issue to recopy it 'downstream'
    self.credit_tardy_payments()

  def mk_n_get_monthmora_w_findate(self, todate) -> moram.SameMonthMora | None:
    if self.ongoing_date is None:
      self.ongoing_date = self.retrodate_ifinmora
    if self.ongoing_date == todate:
      return None
    ipca_cacher = fncach.IpcaAPICacherRetriever()
    rm_minus_2 = rmfs.make_refmonth_it_minus_n_or_raise(self.refmonth, 2)
    ipca_dec = ipca_cacher.fetch_ipca_dec_for_refmonth(rm_minus_2)
    # noinspection bad-argument-type
    monthmora = moram.SameMonthMora(
      fromdate=self.ongoing_date,
      todate=todate,
      prevalue=self.ongoing_debt,  # this is negative
      fix_ir_dec=self.fix_ir_dec,
      var_ir_dec=ipca_dec,
      var_ir_sigla="IPCA",
    )
    self.ongoing_date = todate + relativedelta(days=1)
    return monthmora

  def credit_tardy_payments(self) -> None:
    """
    Credits tardy payments.
    @see <same_module>_doc.md for more information/explanation.
    """
    tardy_payments = self.getcp_tardy_payments()
    while len(tardy_payments) > 0:
      payment = tardy_payments.pop(0)
      payvalue = payment.value
      paydate = payment.date
      monthmora = self.mk_n_get_monthmora_w_findate(paydate)
      if monthmora is None:
        continue
      self.monthmoras.append(monthmora)
      self.debt_to_ongoingdebt(monthmora.increase)
      self.credit_to_debt(payvalue)

  def add_closing_mora_ifany(self) -> None:
    """
    Adds a closing mora on any remaining month debt if any;
    @see <same_module>_doc.md for more information/explanation.
    """
    if self.ongoing_date == self.postdate_ifinmora:
      # a payment on the last day might have happened
      return
    if self.ongoing_credit > DECIMAL_ZERO:
      # if there's credit, there's no debt
      return
    if self.ongoing_debt == DECIMAL_ZERO:
      # there's no debt
      return
    todate = self.postdate_ifinmora
    monthmora = self.mk_n_get_monthmora_w_findate(todate)
    if monthmora is None:
      return
    self.monthmoras.append(monthmora)
    self.debt_to_ongoingdebt(monthmora.increase)

  def debt_to_ongoingdebt(self, debt_value) -> None:
    """
    Debts a debt_value (generally a 'mora') to ongoing debt.
    """
    # noinspection bad-argument-type
    self.ongoing_credit, self.ongoing_debt = cdfs.debt_value_to_accounts(
      value=debt_value, cre_account=self.ongoing_credit, deb_account=self.ongoing_debt
    )

  def treat_no_payments_happened(self) -> None:
    """
    Treats the case when no payments were made.
    """
    todate = self.postdate_ifinmora
    monthmora = self.mk_n_get_monthmora_w_findate(todate)
    if monthmora is None:
      return
    self.monthmoras.append(monthmora)
    self.ongoing_credit, self.ongoing_debt = cdfs.debt_value_to_accounts(
      value=monthmora.increase, cre_account=DECIMAL_ZERO, deb_account=self.ongoing_debt
    )
    self.add_closing_mora_ifany()

  def credit_payments_upto_duedate(self) -> None:
    """
    Credits payments up to duedate.
    @see <same_module>_doc.md for more information/explanation.
    """
    credit_value = self.total_paid_uptoduedate
    self.credit_to_debt(credit_value)

  def credit_to_debt(self, credit_value) -> None:
    """
    Credits a payment to both the debt and credit accounts,
      and, as a second step, compensate, if needed, credit against debt.
    @see <same_module>_doc.md for more information/explanation.
    """
    # 1st step: credit value to deb_acc (with month's debt) and, if any remains, to cre_acc
    self.ongoing_credit, self.ongoing_debt = cdfs.credit_value_to_accounts(
      value=credit_value, cre_account=DECIMAL_ZERO, deb_account=self.ongoing_debt
    )
    # 2nd step: in case a credit coexists with debt, compensate the first to the latter
    # noinspection bad-argument-type
    self.ongoing_credit, self.ongoing_debt = cdfs.credit_value_to_deb_account(
      cre_value=self.ongoing_credit, deb_account=self.ongoing_debt
    )

  @property
  def credito_no_fecho(self) -> Decimal | None:
    if self.payment_process_finished:
      return self.ongoing_credit
    return None

  @property
  def debito_no_fecho(self) -> Decimal | None:
    if self.payment_process_finished:
      return self.ongoing_debt
    return None

  def raise_va_if_debt_is_positive(self) -> None:
    if self.ongoing_debt > DECIMAL_ZERO:
      errmsg = f"Error: debt (={self.ongoing_debt}) cannot be greater than DECIMAL_ZERO"
      raise ValueError(errmsg)

  def process_payments_upto_duedate_ifany(self) -> None:
    if self.total_paid_uptoduedate > DECIMAL_ZERO:
      self.credit_payments_upto_duedate()

  def raise_va_if_some_paydate_are_not_in_paymonth(self) -> None:
    paydates = [p.date for p in self.payments]
    firstdate = self.retrodate_ifinmora
    lastdate = self.postdate_ifinmora
    outofmonthdates =  [d for d in paydates if lastdate < d < firstdate ]
    if len(outofmonthdates) > 0:
      errmsg = f"Error: some dates ({outofmonthdates}) do not belong to pay month."
      raise ValueError(errmsg)

  def raise_va_if_some_payvalues_are_negative(self) -> None:
    negativevalues = [p.value for p in self.payments if p.value < 0]
    if len(negativevalues) > 0:
      allpayvalues = [p.value for p in self.payments]
      errmsg = f"Error: payments ({allpayvalues}) cannot contain negative values."
      raise ValueError(errmsg)

  def check_processors_data_consistency_or_raise_va(self) -> None:
    # debt cannot be positive at the beginning
    self.raise_va_if_debt_is_positive()
    # payments cannot contain dates outside pay month
    self.raise_va_if_some_paydate_are_not_in_paymonth()
    # payments cannot contain negative values
    self.raise_va_if_some_payvalues_are_negative()

  def process_payments_in_month(self) -> None:
    """
    Starts the processing of a (monthly) debt value against payment(s).
    @see <same_module>_doc.md for more information/explanation.
    """
    if self.payment_process_finished:
      print('Method process_payments_in_month() already run. Returning.')
      return
    self.check_processors_data_consistency_or_raise_va()
    self.orig_monthsdebt = self.ongoing_debt
    self.process_payments_upto_duedate_ifany()
    self.process_tardy_payments_if_any()
    self.add_closing_mora_ifany()
    self.payment_process_finished = True

  process_month = process_payments_in_month
  process = process_month

  def __str__(self):
    ostr = self.history_backtrack()
    return ostr


def adhoctest1():
  print("The adhoctests are in the same folder as are the unit-tests.")


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
