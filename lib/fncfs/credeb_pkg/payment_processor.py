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
import art.immeub.rent.billmodels.payment_pydant as bipydtc  # bipydtc.PydtcPayment
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as fncach  # fncach.IpcaAPICacherRetriever
import lib.fncfs.credeb_pkg.samemonthmora as moram  # moram.SameMonthMora
from art.immeub.rent.pdntcmdls.rentcontract_pydant import MORA_M_MINUS_N_STR
MORA_M_MINUS_N = int(MORA_M_MINUS_N_STR)
DECIMAL_ZERO = Decimal('0')
DEFAULT_FIX_IR_DEC = Decimal('0.02')


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
  payments: list[bipydtc.PydtcPayment] = pydantic.Field(default_factory=lambda: [])  # bipydtc.PydtcPayment
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

  def getcp_duedate_payments(self) -> list[bipydtc.PydtcPayment]:
    payments = [p for p in self.payments if p.date <= self.duedate]
    return payments

  def getcp_tardy_payments(self) -> list[bipydtc.PydtcPayment]:
    payments = [p for p in self.payments if p.date > self.duedate]
    return payments

  def get_payments_on_daydate(self, pdate) -> list[bipydtc.PydtcPayment]:
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

  def mk_n_get_monthmora_w_findate(self, todate) -> moram.SameMonthMora | None:
    if self.ongoing_date is None:
      # retrodate_ifinmora, if contract does not say differently, is the first day of the month
      self.ongoing_date = self.retrodate_ifinmora
    if self.ongoing_date >= todate:
      # the '=' means mora has already been counted
      # the '>' means mora has been counted and also that a payment happened on the last day of month
      # because at the method's end: self.ongoing_date = todate + relativedelta(days=1)
      # and if a payment happened on month's last dat, self.ongoing_date will be position on next month's first day
      # out of the 2 callers to this method, the second, add_closing_mora(), considers this
      # the first one throws an exception upon receiving None
      return None
    if self.ongoing_debt >= DECIMAL_ZERO:
      # case which an ongoing_credit might have occurred
      # notice this method is called by '2 clients'
      # one of them will throw an exception if it gets None
      # because this method should not be called under that condition
      # the second caller, add_closing_mora(), considers this
      return None
    ipca_cacher = fncach.IpcaAPICacherRetriever()
    rm_minus_2 = rmfs.make_refmonth_it_minus_n_or_raise(self.refmonth, MORA_M_MINUS_N)
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

  def process_tardy_payments_ifany(self) -> None:
    """
    Processes tardy payments (i.e., those in month after duedate) if any.

    @see also <same_module>_doc.md in the same folder as this for more information/explanation.
    """
    tardy_payments = self.getcp_tardy_payments()
    while len(tardy_payments) > 0:
      payment = tardy_payments.pop(0)
      payvalue = payment.value
      paydate = payment.date
      if self.ongoing_debt < DECIMAL_ZERO:
        monthmora = self.mk_n_get_monthmora_w_findate(paydate)
        if monthmora is None:
          errmsg = f"Error: monthmora for payment {payvalue} on {paydate} returned None."
          raise ValueError(errmsg)
        self.monthmoras.append(monthmora)
        # noinspection bad-argument-type
        self.ongoing_credit, self.ongoing_debt = cdfs.debt_value_to_accounts_n_compensate(
          deb_value=monthmora.increase, cre_account=self.ongoing_credit, deb_account=self.ongoing_debt
        )
      # at this point, payment is credited whether mora happened (debt occuring case) or not (credit occurring case)
      # noinspection bad-argument-type
      self.ongoing_credit, self.ongoing_debt = cdfs.credit_value_to_accounts_n_compensate(
        cre_value=payvalue, cre_account=self.ongoing_credit, deb_account=self.ongoing_debt
      )

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
    # noinspection bad-argument-type
    self.ongoing_credit, self.ongoing_debt = cdfs.debt_value_to_accounts_n_compensate(
      deb_value=monthmora.increase, cre_account=self.ongoing_credit, deb_account=self.ongoing_debt
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
    self.ongoing_credit, self.ongoing_debt = cdfs.credit_or_debt_value_to_accounts_n_compensate(
      value=monthmora.increase, cre_account=DECIMAL_ZERO, deb_account=self.ongoing_debt
    )
    self.add_closing_mora_ifany()

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

  def raise_va_if_debt_is_positive_or_credit_negative(self) -> None:
    if self.ongoing_debt > DECIMAL_ZERO:
      errmsg = f"Error: debt (={self.ongoing_debt}) cannot be a positive number."
      raise ValueError(errmsg)
    if self.ongoing_credit and self.ongoing_credit < DECIMAL_ZERO:
      errmsg = f"Error: credit (={self.ongoing_credit}) cannot be a negative number."
      raise ValueError(errmsg)

  def process_payments_upto_duedate_ifany(self) -> None:
    """

    Processes payment(s) up to duedate, if any, crediting them.
    @see <same_module>_doc.md for more information/explanation.
    """
    if self.total_paid_uptoduedate > DECIMAL_ZERO:
      credit_value = self.total_paid_uptoduedate
      # noinspection bad-argument-type
      self.ongoing_credit, self.ongoing_debt = cdfs.credit_value_to_accounts_n_compensate(
        cre_value=credit_value, cre_account=self.ongoing_credit, deb_account=self.ongoing_debt
      )

  def raise_va_if_some_paydates_are_after_paymonth(self) -> None:
    paydates = [p.date for p in self.payments]
    # firstdate = self.retrodate_ifinmora
    lastdate = self.postdate_ifinmora
    outofmonthdates =  [d for d in paydates if lastdate < d]  #  < firstdate
    if len(outofmonthdates) > 0:
      errmsg = f"Error: some dates ({outofmonthdates}) are after paymonth."
      raise ValueError(errmsg)

  def raise_va_if_some_payvalues_are_negative(self) -> None:
    negativevalues = [p.value for p in self.payments if p.value < 0]
    if len(negativevalues) > 0:
      allpayvalues = [p.value for p in self.payments]
      errmsg = f"Error: payments ({allpayvalues}) cannot contain negative values."
      raise ValueError(errmsg)

  def check_consistency_in_payment_list(self) -> None:
    # payments cannot contain dates after paymonth (though it can contain a date in a previous month)
    self.raise_va_if_some_paydates_are_after_paymonth()
    # payments cannot contain negative values
    self.raise_va_if_some_payvalues_are_negative()

  def check_processors_data_consistency_or_raise_va(self) -> None:
    # debt cannot be positive at the beginning
    self.raise_va_if_debt_is_positive_or_credit_negative()
    self.check_consistency_in_payment_list()

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
    self.process_tardy_payments_ifany()
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
