#!/usr/bin/env python3
"""
art/immeub/rent/billmodels/billingcard_pydantic.py

# from art.immeub.rent.pdntcmdls.schema_bizmodels import BillingCard
# locale.setlocale(locale.LC_NUMERIC, "pt_BR")  # "pt_BR.UTF-8"
"""
import calendar
import datetime
from decimal import Decimal
import locale
from typing import Annotated
import lib.fncfs.credeb_pkg.payment_processor as pproc
from prettytable import PrettyTable
import pydantic
from dateutil.relativedelta import relativedelta
import art.immeub.rent.billmodels.billingitem_pydantic as bipydtc  # bipydtc.PydtcBillingItem
import art.immeub.rent.pdntcmdls.rentcontract_pydant as rentpydtc  # rentpydtc.PydtcRentContract
import art.immeub.rent.pdntcmdls.immeub_pydant as immeubpydtc  # immeubpydtc.PydtcImmeuble
import art.immeub.rent.pdntcmdls.person_pydant as perspydtc  # perspydtc.PydtcPerson
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcafs  # ipcafs.IpcaAPICacherRetriever
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.fncfs.credeb_pkg.payment_processor as pay  # pay.process_payments_in_month
import lib.fncfs.credeb_pkg.samemonthmora as moram  # moram.SameMonthMora
from lib.dbfs import mngdb
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
MONTHS = rmfs.PT_MESES
DEFAULT_PAYMENT_MONTHS_DUEDAY = 10
MONTHLY_FIX_IR_DEC_STR = '0.02'
MONTHLY_FIX_IR_DEC = Decimal(MONTHLY_FIX_IR_DEC_STR)
DECIMAL_ZERO = Decimal('0')
contrnumber_type = Annotated[str, pydantic.StringConstraints(max_length=12)]
find_rentcontract_by_contrnumber = rentpydtc.find_rentcontract_by_contrnumber


def make_current_refmonth_minus_1():
  cur_refmonth = rmfs.make_current_refmonth()
  refmonth = rmfs.make_refmonth_or_current_it_minus_n(cur_refmonth, 1)
  return refmonth


def make_current_months_default_duedate():
  cur_refmonth = rmfs.make_current_refmonth()
  year, month, day = cur_refmonth.year, cur_refmonth.month, DEFAULT_PAYMENT_MONTHS_DUEDAY
  duedate = datetime.date(year=year, month=month, day=day)
  return duedate


def from_to_json(doc):
  billingcard_o = None
  if doc is not None:
    # pdict = srlz.deserialize_mongo_doc(doc, is_data_from_db=True)
    for i, elem in enumerate(doc):
      _ = elem
      elem = {key: value for key, value in elem.items() if value is not None}

      def remove_nones_fr_billingitems(p_list: list):
        """
        None's must be removed from the testdata
        The outer dict was cleaned up above, now we must remove None's in the billing_items
        (Because billing_items is a dictlist, the dict's are recreated, but the list is used mutably.)
        """
        for ii, supposed_billingitem in enumerate(p_list):
          if not isinstance(supposed_billingitem, dict):
            # there are 2 lists in the outer doc, the address one is not a dict, the 'billingitems' is a dict
            continue
          supposed_billingitem = {key: value for key, value in supposed_billingitem.items() if value is not None}
          # the dict is used immutably (it's recreated), the list is used mutably (the new dict goes back in place)
          p_list[ii] = supposed_billingitem

      for key in elem:
        obj = elem[key]
        if isinstance(obj, list):
          # here we look for lists so that we can look for inner dict's that may contain None's
          alist = obj
          remove_nones_fr_billingitems(alist)
      billingcard_o = bcardpydtc.PydtcBillingCard.MongoJsonRepr(**elem)
  self.close_conn()
  return billingcard_o


class PydtcBillingCard(pydantic.BaseModel):
  """

  Mora, if any, explained
  =======================
  This can be explained with a simple example.
  Let's consider this context/situation:
    a) duedate is on month's day 10
    b) payment happened lately incomplete on month's day 20
  How 'mora' is calculated?
    1 first, a 20 day (after day 1) mora will increase the whole month's pay;
    2 then the pay on the 20th will credit the updated month's bill;
    3 then the remaining balance will increase to the rest of month
      (day 31, in this case, it increases another 10 days);
    4 this remaining is then closed (frozen),
       and is passed on to a new billing entry on the subsequent month's bill
    5 if another payment happens in between day 21 to month's end,
      payment_process() must be rerun and calculates again either credit or debit.

  When the month transitions (i.e., the next month comes),
    the 'mora' becomes a new 'billing item' itself and
    does not correct for the 10-day payment window.
    However, it goes into the same treatment as the other items
    in case a new mora becomes incident after duedate.

  billingcard: BillingCard = pydantic.dataclasses.Field(default_factory=lambda: None)
  refmonth: Optional[datetime.date] = pydantic.Field(default=lambda: rmfs.make_current_refmonth())
  """
  contrnumber: contrnumber_type
  billingitems: list[bipydtc.PydtcBillingItem] = pydantic.Field(default_factory=lambda: [])
  payprocessor: pproc.PaymentProcessor

  class BillingCardClean(pydantic.BaseModel):
    contract: Contract

    @pydantic.model_validator(mode='before')
    @classmethod
    def allow_fetching_by_number(cls, values: dict) -> dict:
      # If the user passed a raw string/number instead of a contract object
      if "contrnumber" in values and "contract" not in values:
        cnumber = values.pop("contrnumber")
        values["contract"] = find_rentcontract_by_contrnumber(cnumber)
      return values

    @property
    def contract_number(self) -> str:
      # Convenient access to the inner attribute without data duplication
      return self.contract.contract_number

  @pydantic.computed_field
  @property
  def rentcontract(self) -> rentpydtc.PydtcRentContract:
    _rentcontract = rentpydtc.find_rentcontract_by_contrnumber(self.contrnumber)
    if _rentcontract is None:
      errmsg = f"Not Found Error: rent contract not found for contrnumber: {self.contrnumber}"
      raise ValueError(errmsg)
    return _rentcontract

  @property
  def refmonth(self) -> datetime.date:
    return self.rentcontract.make_contracts_pay_refmonth()

  @property
  def duedate(self) -> datetime.date:
    return self.rentcontract.get_contracts_duedate()

  @property
  def payments(self) -> list[intrfc.PaymentInterfaceDateNValue]:  # bipydtc.PydtcPayment
    if self.payprocessor is None:
      return []
    return self.payprocessor.payments

  @property
  def credito_no_fecho(self) -> Decimal | None:
    if not self.payprocessor.payment_process_finished:
      return None
    _credito_no_fecho = payprocessor.cre_deb_moras_after_process[0]
    return _credito_no_fecho

  @property
  def debito_no_fecho(self) -> Decimal | None:
    if not self.payprocessor.payment_process_finished:
      return None
    _debito_no_fecho = payprocessor.cre_deb_moras_after_process[1]
    return _debito_no_fecho

  @property
  def monthmoras(self) -> list[moram.SameMonthMora]:
    if not self.payprocessor.payment_process_finished:
      return []
    _monthmoras = payprocessor.cre_deb_moras_after_process[2]
    return _monthmoras

  @property
  def monthly_fix_ir_dec(self) -> Decimal:
    return self.rentcontract.monthly_fix_ir_dec

  @property
  def location(self) -> immeubpydtc.PydtcImmeuble:
    _location = self.rentcontract.location
    return _location

  @property
  def address(self) -> list[str]:
    _address = self.location.address
    return _address

  @property
  def first_payor(self) -> perspydtc.PydtcPerson | None:
    _first_payor = self.rentcontract.main_tenant
    return _first_payor

  @property
  def second_payors(self) -> list[perspydtc.PydtcPerson]:
    other_tenants = self.rentcontract.other_tenants_ifany
    return other_tenants

  @property
  def first_cpf_fmt_w_dots(self) -> str:
    if self.first_payor:
      return self.first_payor.cpf_fmt_w_dots
    return "n/a"

  @property
  def rentvalue(self) -> Decimal:
    _rentvalue = self.rentcontract.cur_rentvalue
    return _rentvalue

  def make_n_set_minimum_billingitems(self):
    if self.billingitems is None:
      bitems = self.rentcontract.make_n_get_mininum_billingitems()
      self.billingitems = bitems or []
    errmsg = f"Programming Error: tried to run make_n_set_minimum_billingitems() a second time."
    raise ValueError(errmsg)

  def get_minimum_billingitems(self) -> list[bipydtc.PydtcBillingItem]:
    if self.billingitems is None:
      self.make_n_set_minimum_billingitems()
    return self.billingitems

  @property
  def fatura_total(self) -> Decimal:
    totais = list(map(lambda obj: obj.value, self.billingitems))
    # _fatura_total = functools.reduce(lambda x, y: x + y, totais, 0)
    _fatura_total = sum(totais)
    if not isinstance(_fatura_total, Decimal):
      _fatura_total = Decimal(_fatura_total)
    return _fatura_total

  def process_payments_in_month(self) -> None:
    """
    Processes payments in month.
    Dispatches processing to quinhoes.process_payments() in library.
    This process may be run once all payments are known. It may run at each pay,
      but it always reruns from the beginning.

    Receives back three variables:
      a) credito_no_fecho
      b) debito_no_fecho
      c) quinhoes_days_vals

    Let's see each one of them:

      a) credito_no_fecho: if payment superseded bill's value.
      b) debito_no_fecho: if payment was below bill's value. This also generates mora.
      c) monthmoras

    """
    # sort payments date-asc
    self.payments.sort(key=lambda obj: obj.date)
    # 'credito' é troco, devolução ou adiantamento; 'debito' é item de mora para o próximo mês
    # if one has value, the other must be zeroed: critic (or exception-raising) happens in function process_payments()
    payments = [intrfc.PaymentInterfaceDateNValue(o.date, o.value) for o in self.payments]
    ongoing_debt = -self.fatura_total
    pprocessor = pay.PaymentProcessor(
      ongoing_debt=ongoing_debt,
      duedate=self.duedate,
      fix_ir_dec=self.monthly_fix_ir_dec,
      has_ipca=True,
    )
    pprocessor.payments = payments
    pprocessor.process()

  @property
  def fix_plus_var_ir_dec(self) -> Decimal:
    fix_ir_dec = self.rentcontract.monthly_fix_ir_dec
    _fix_plus_var_ir_dec = fix_ir_dec + self.var_ir_as_ipca_dec
    return _fix_plus_var_ir_dec

  @property
  def var_ir_as_ipca_dec(self) -> Decimal:
    ipcacacher = ipcafs.IpcaAPICacherRetriever()
    ipcadec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(self.refmonth, self.mora_m_minus_n)
    if ipcadec is None:
      ipcadec = Decimal('0')
    return ipcadec

  @property
  def mora_m_minus_n(self) -> int:
    return self.rentcontract.mora_m_minus_n

  @property
  def postdate_ifinmora(self) -> datetime.date:
    """
    Returns postdate_ifinmora, which is the last day (or other) of paymonth
    Obs: the last day (or another one) is given by rentcontract
    Example:
      if refmonth is '2026-5':
        duedate is '2026-6-10' and
          retrodate_ifinmora = '2026-6-1'
          -> postdate_ifinmora =  '2026-6-30'
    """
    paymonth = self.refmonth + relativedelta(months=1)
    return self.rentcontract.get_postdate_ifinmora(paymonth)

  @property
  def retrodate_ifinmora(self) -> datetime.date:
    """
    Returns retrodate_ifinmora, which is the first day (or other) of paymonth
    Obs: the first day (or another one) is given by rentcontract
    Example:
      if refmonth is '2026-5':
        duedate is '2026-6-10' and
          -> retrodate_ifinmora = '2026-6-1'
          postdate_ifinmora =  '2026-6-30'
    """
    paymonth = self.refmonth + relativedelta(months=1)
    return self.rentcontract.get_retrodate_ifinmora(paymonth)

  def add_payment(self, payment: intrfc.PaymentInterfaceDateNValue):
    """
    TODO update, when possible, payment type to bipydtc.PydtcPayment
    At this version, two payments with the same value and date are not allowed.
    TODO this may be allowed by a
     datetime field instead of only date
    """
    if not isinstance(payment, bipydtc.PydtcPayment):
      errmsg = f"Error: payment [{payment}] is of wrong type."
      raise ValueError(errmsg)
    boolarr = map(lambda o: o.date == payment.date and o.value == payment.value, self.payments)
    boolarr = list(boolarr)
    if True in boolarr:
      errmsg = f"Error: payment [{payment}] date and value has already been entered.."
      errmsg += f"\n\t if two payments are equal on the same day, they should be consolidated."
      raise ValueError(errmsg)
    #  okay, at this payment may be appended
    self.payments.append(payment)
    # all the time a payment is entered, a new process_payment must happen
    # but the client must call it with obj.process_payments_in_month()

  def lastpaydate(self):
    # sort it asc and return lastpaydate
    self.payments.sort(key=lambda o: o.date)
    lastpayment = self.payments[-1]
    _lastpaydate = lastpayment.date
    return _lastpaydate

  def has_been_paid_after_payment_processed(self):
    if self.debito_no_fecho == DECIMAL_ZERO:
      return True
    return False

  def str_table_billingitems(self):
    """
    outstr = f"{self.descr} | {self.refmmm} | {fmt_value} | {self.mora} | {self.total_item}"
    """
    table = PrettyTable()
    headers = ["seq",  "descrição", "testdata-ref",  "valor-item", "mora-item", "total-item"]
    table.field_names = headers
    for bi in self.get_minimum_billingitems():
      values = bi.get_the_4_billingitem_values_as_lst()
      table.add_row(values)
    str_table = str(table)
    return str_table

  def report_quinhoes_days_vals(self) -> str:
    """
    quinhoes_days_vals is a tuple list whose tuples contain:
      (ndays, moravalue)
    WHERE:
      ndays is the number of numbers that received 'mora'
      moravalue is the increased value due to the 'mora'

    What else can be reported?
    The elements in quinhoes_days_vals are related to payments.

    Example:
      if a payment was late (post duedate), it will:
      a) create one item to quinhoes_days_vals if it's fully compensates debt
      b) create two items in quinhoes_days_vals if a residue debt was left
    """
    tardypaymentsdict = {o.date.day: o for o in self.payments}
    if len(tardypaymentsdict) == 0:
      return "No tardy payments"
    lines = []
    line = 'Report/report_quinhoes_days_vals():'
    lines.append(line)
    _, ndaysinmonth = calendar.monthrange(self.duedate.year, self.duedate.month)
    report_tuple = None
    for tupl in self.quinhoes_days_vals:
      report_tuple = tupl
      payment = None
      try:
        ndays, moravalue = tupl
        payment = tardypaymentsdict[ndays]
        line = f"mora {moravalue:.2f} foi gerada por {ndays} dias em {payment.date} com o pagt {payment.value}"
        lines.append(line)
      except KeyError:
        pass
    report_text = '\n'.join(lines)
    return report_text

  def print_str_table_billingitems(self):
    print(self.str_table_billingitems())

  @property
  def duedate(self) -> datetime.date:
    rm = self.refmonth
    _duedate = self.rentcontract.get_duedate_fr_refmonth(self.refmonth)
    return _duedate

  @property
  def refmmmyyyy(self) -> str:
    mmm_mes = rmfs.get_pt_3lettermonth_fr_date(self.refmonth)
    _refmmmyyyy = f"{mmm_mes}/{self.refmonth.year}"
    return _refmmmyyyy

  def str_billingcard(self):
    """
    """
    fmt_duedate = self.duedate.strftime("%d/%m/%Y")
    ostr = f"""\n    *** Cobrança mensal de aluguel ***
    mês referência: {self.refmmmyyyy} | pagamento até o dia: {fmt_duedate}
    Locação: {self.rentcontract.contrnumber} | Inquilino responsável: {self.rentcontract.main_tenant.get_first_last_names_n_fmt_cpf()}
    Endereço: {self.rentcontract.location.address}\n"""
    # at this version, billingitems will be [dynamically] created at this point
    ostr += self.str_table_billingitems()
    fatura_total = self.fatura_total
    fmt_total_mes = f"{fatura_total:.02f}"
    strtotal = f"\n               Total mês: {fmt_total_mes}\n"
    ostr += strtotal
    return ostr

  def as_mongo_json_dict(self):
    billingitems_dictlist = [bitem.instantiate_as_mongojsonrepr_class() for bitem in self.billingitems]
    pdict = {
      'contrnumber': self.rentcontract.contrnumber,
      'refmonth': self.refmonth,
      'duedate': self.duedate,
      'payor': self.rentcontract.main_tenant.get_first_n_last_names(),
      'cpf':  self.rentcontract.main_tenant.cpf_fmt_w_dots,
      'address': self.rentcontract.location.address,
      'billingitems': billingitems_dictlist,
      'fatura_total': self.fatura_total,
    }
    return pdict

  class MongoJsonRepr(pydantic.BaseModel):
    contrnumber: str
    refmonth: datetime.date
    duedate: datetime.date
    payor: str
    cpf: str
    address: list[str]
    billingitems: list[bipydtc.PydtcBillingItem]  # .MongoJsonRepr]
    fatura_total: Decimal

  def as_pydantic_to_mongo(self):
    """
    return json.dumps(self.as_mongo_json_dict())
    return self.model_dump_json(indent=2)
    """
    pydantic_to_mongo = self.MongoJsonRepr(**self.as_mongo_json_dict())
    return pydantic_to_mongo

  def as_mongo_json_repr(self):
    pydantic_to_mongo = self.as_pydantic_to_mongo()
    mongojsonrepr = pydantic_to_mongo.model_dump_json(indent=2)
    return mongojsonrepr

  def process(self):
    pass


def adhoctest1():
  """

  """
  pass


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
