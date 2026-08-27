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
from typing import Annotated, Optional
import lib.fncfs.credeb_pkg.payment_processor as pproc
from prettytable import PrettyTable
import pydantic
from dateutil.relativedelta import relativedelta
import art.immeub.rent.billmodels.billingitem_pydantic as bitems  # bipydtc.PydtcBillingItem
import art.immeub.rent.pdntcmdls.rentcontract_pydant as rentpydtc  # rentpydtc.PydtcRentContract
import art.immeub.rent.pdntcmdls.immeub_pydant as immeubpydtc  # immeubpydtc.PydtcImmeuble
import art.immeub.rent.pdntcmdls.person_pydant as perspydtc  # perspydtc.PydtcPerson
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcafs  # ipcafs.IpcaAPICacherRetriever
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
import lib.fncfs.credeb_pkg.payment_processor as pay  # pay.process_payments_in_month
import lib.fncfs.credeb_pkg.samemonthmora as moram  # moram.SameMonthMora
import art.immeub.rent.mdb.mongofs as mngfs  # .RentMongo
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
MONTHS = rmfs.PT_MESES
DEFAULT_PAYMENT_MONTHS_DUEDAY = 10
MONTHLY_FIX_IR_DEC_STR = '0.02'
MONTHLY_FIX_IR_DEC = Decimal(MONTHLY_FIX_IR_DEC_STR)
DECIMAL_ZERO = Decimal('0')
contrnumber_type = Annotated[str, pydantic.StringConstraints(max_length=12)]
find_rentcontract_by_contrnumber = rentpydtc.find_rentcontract_by_contrnumber


class PydtcBillingCard(pydantic.BaseModel):
  """
  Class that models a 'billing card' which contains:
    a) a rentcontract (link or object)
    b) a refmonth (the month to whicy payment is due)
    c) its billing-items whose sum makes up the billing card total
    d) the pay_processor object (fech_pagts_n_mora) which in turn contains
        d1 payments
        d2 and mora parts if anty
      and processes payment(s) and closes (*) the BC (Billing Card) for the next month.
      (*) the BC closing is a logical one, it happens when the next refmonth opens for payment;
      (*) if mora exists at closing, it becomes a billing_item to the next BC.
  """
  rentcontract: rentpydtc.PydtcRentContract = pydantic.Field(default_factory=lambda: None)
  refmonth: Optional[datetime.date]  # = pydantic.Field(default=lambda: rmfs.make_current_refmonth())
  billingitems: list[bitems.PydtcBillingItem] = pydantic.Field(default_factory=lambda: None)
  fech_pagts_n_mora: pproc.PaymentProcessor = pydantic.Field(default_factory=lambda: None)

  @pydantic.model_validator(mode='before')
  @classmethod
  def allow_fetching_by_number(cls, values: dict) -> dict:
    # If the user passed a raw string/number instead of a contract object
    if "contrnumber" in values and "rentcontract" not in values:
      cnumber = values.pop("contrnumber")
      values["rentcontract"] = find_rentcontract_by_contrnumber(cnumber)
    if "refmonth" not in values:
      values["refmonth"] = rmfs.make_refmonth_or_current_it_minus_n(None, 1)
    return values

  @pydantic.computed_field
  @property
  def contrnumber(self) -> str:
    # Convenient access to the inner attribute without data duplication
    if self.rentcontract is None:
      return "n/a"
    return self.rentcontract.contrnumber

  @pydantic.computed_field
  @property
  def billing_id(self) -> str:
    if self.rentcontract is None:
      return "n/a"
      if self.rentcontract.location is None:
        return "n/a"
    rmstr = self.rm_as_yyyymm
    _billing_id = f"{self.rentcontract.location.imm_nickname}MR{rmstr}"
    return _billing_id

  @property
  def rm_as_yyyymm(self) -> str:
    rmstr = self.refmonth.strftime("%Y%m")
    return rmstr

  @property
  def rm_as_3letrasbaryyyy(self) -> str:
    mes3letras = rmfs.get_pt_3lettermonth_fr_nmonth(self.refmonth.month)
    rmstr = f"{mes3letras}/{self.refmonth.year}"
    return rmstr

  @property
  def paym_as_3letrasbaryyyy(self) -> str:
    if self.rentcontract is None:
      return "n/a"
    paymonth = self.rentcontract.get_pay_duedate_fr_refmonth(self.refmonth)
    mes3letras = rmfs.get_pt_3lettermonth_fr_nmonth(paymonth.month)
    rmstr = f"{mes3letras}/{paymonth.year}"
    return rmstr

  @property
  def currency3letter_n_symbol(self) -> tuple[str, str]:
    currency3letter, symbol = "", ""
    if self.rentcontract is not None:
      currency3letter = self.rentcontract.currency3letter
      symbol = self.rentcontract.get_currency_symbol()
    return currency3letter, symbol


  @property
  def charging_month(self) -> datetime.date | None:
    """
    It's the month following refmonth
    """
    if self.refmonth is None:
      return None
    return rmfs.make_refmonth_it_minus_n_or_raise(self.refmonth, 1)

  @property
  def credito_no_fecho(self) -> Decimal | None:
    if not self.fech_pagts_n_mora.payment_process_finished:
      return None
    _credito_no_fecho = self.fech_pagts_n_mora.cre_deb_moras_after_process[0]
    return _credito_no_fecho

  @property
  def debito_no_fecho(self) -> Decimal | None:
    if not self.fech_pagts_n_mora.payment_process_finished:
      return None
    _debito_no_fecho = self.fech_pagts_n_mora.cre_deb_moras_after_process[1]
    return _debito_no_fecho

  @property
  def monthmoras(self) -> list[moram.SameMonthMora]:
    if not self.fech_pagts_n_mora.payment_process_finished:
      return []
    _monthmoras = self.fech_pagts_n_mora.cre_deb_moras_after_process[2]
    if _monthmoras is None:
      # this None case does not happen after the 'if' above,
      # but IDE looks upat the returning type-hint, so this 'if' is for the IDE
      return []
    return _monthmoras

  @property
  def monthly_fix_ir_dec(self) -> Decimal:
    return self.rentcontract.monthly_fix_ir_dec

  @property
  def location(self) -> immeubpydtc.PydtcImmeuble:
    _location = self.rentcontract.location
    return _location

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

  def make_n_set_standard_billingitems(self):
    self.billingitems = self.rentcontract.make_n_get_standard_billingitems(self.refmonth) or []

  def get_standard_billingitems(self) -> list[bitems.PydtcBillingItem]:
    if self.billingitems is None:
      self.make_n_set_standard_billingitems()
    return self.billingitems

  def add_billingitem(self, bitem: bitems.PydtcBillingItem) -> None:
    self.billingitems.append(bitem)

  def add_billingitem_w_fields(
      self, descr: str, refmonth: datetime.date | str, value: Decimal, seq: int | None = None
    ) -> None:
    nitems = len(self.billingitems)
    if seq is None:
      seq = nitems + 1
    refmonth = rmfs.make_refmonth_or_raise(refmonth)
    bitem = bitems.PydtcBillingItem(seq=seq, descr=descr, refmonth=refmonth, value=value)
    self.add_billingitem(bitem)

  @pydantic.computed_field
  @property
  def mesreftotal(self) -> Decimal:
    totais = list(map(lambda obj: obj.value, self.billingitems))
    _fatura_total = sum(totais)
    if not isinstance(_fatura_total, Decimal):
      _fatura_total = Decimal(_fatura_total)
    return _fatura_total

  def instantiate_fech_pagts_n_mora(self):
    if self.fech_pagts_n_mora is not None:
      return
    if self.billingitems is None:
      errmsg = "Error: billingitems is None when attempting to instantiate fech_pagts_n_mora."
      raise ValueError(errmsg)
    ongoing_debt = -self.mesreftotal
    self.fech_pagts_n_mora = pay.PaymentProcessor(
      ongoing_debt=ongoing_debt,
      duedate=self.duedate,
      fix_ir_dec=self.monthly_fix_ir_dec,
      has_ipca=True,
    )


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
    # 'credito' é troco, devolução ou adiantamento; 'debito' é item de mora para o próximo mês
    # if one has value, the other must be zeroed: critic (or exception-raising) happens in function process_payments()
    self.instantiate_fech_pagts_n_mora()
    self.fech_pagts_n_mora.payments.sort(key=lambda obj: obj.date)
    self.fech_pagts_n_mora.process()

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
    return self.rentcontract.get_mora_endingdate_w_refmonth(paymonth)

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
    return self.rentcontract.get_date_when_mora_begins_w_refmonth(paymonth)

  def add_payment_lst(self, payments: list[intrfc.PaymentInterfaceDateNValue]) -> None:
    """
    TODO update, when possible, payment type to bipydtc.PydtcPayment
    At this version, two payments with the same value and date are not allowed.
    TODO this may be allowed by a
     datetime field instead of only date
    """
    bills_payment = []
    if payments is None or len(payments) == 0:
      return
    if self.billingitems is None:
      errmsg = f"Error: attempt to input payments at a point when billingitems is still None."
      raise ValueError(errmsg)
    for payment in payments:
      bills_payment.append(payment)
    self.instantiate_fech_pagts_n_mora()
    self.fech_pagts_n_mora.payments = bills_payment

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
    for bi in self.get_standard_billingitems():
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
    if self.rentcontract is not None:
      _duedate = self.rentcontract.get_duedate_fr_refmonth(self.refmonth)
      return _duedate
    return "n/a"

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
    fatura_total = self.mesreftotal
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
      'fatura_total': self.mesreftotal,
    }
    return pdict

  class MongoJsonRepr(pydantic.BaseModel):
    contrnumber: str
    refmonth: datetime.date
    duedate: datetime.date
    payor: str
    cpf: str
    address: list[str]
    billingitems: list[bitems.PydtcBillingItem]  # .MongoJsonRepr]
    fatura_total: Decimal

  def as_pydantic_to_mongo(self):
    """
    return json.dumps(self.as_mongo_json_dict())
    return self.model_dump_json(indent=2)
    """
    pydantic_to_mongo = self.MongoJsonRepr(**self.as_mongo_json_dict())
    return pydantic_to_mongo

  def to_json(self, indent: int = 2, is_for_db=False) -> str:
    """
    Transforms the object into a JSON str for sending (e.g. to MongoDB).

    Notice that:
      exclude={'rentcontract', 'payments' ...}
    Because:
      a) contrnumber is primary key for finding rentcontract;
      b) payment is kept in fech_pagts_n_mora;
    """
    excludeset = {}
    if is_for_db:
      excludeset = {'rentcontract'}
    jsondump = self.model_dump_json(exclude=excludeset, indent=indent)
    return jsondump

  @classmethod
  def instantiate_fr_json_dict(cls, jsondict: dict) -> "PydtcBillingCard":
    """
    Instantiates (back) the object from JSON dict.

    """
    if jsondict is None:
      return None
    jsondict = mngfs.remove_none_values_fr_dict_recurs(jsondict)
    obj = cls.model_validate(jsondict)
    return obj

  @classmethod
  def instantiate_fr_json_str(cls, json_str) -> "PydtcBillingCard":
    """
    Instantiates (back) the object from JSON str.
    """
    obj = cls.model_validate_json(json_str)
    return obj

  def process(self):
    self.process_payments_in_month()

  def __repr__(self):
    duedate = 'n/a' if self.duedate is None else self.duedate
    _, symbol = self.currency3letter_n_symbol
    total = f"{symbol} {self.mesreftotal:.2f}"
    n_items = len(self.billingitems)
    ostr = f"fatura: contrnumber={self.contrnumber}, refmonth={self.refmonth}, duedate={duedate}, items={n_items}, total={total}"
    return ostr

  def __str__(self):
    ostr = self.to_json(indent=2, is_for_db=False)
    return ostr


def adhoctest1():
  """

  """
  contrnumber = 'CDouto202401'
  print('contrnumber =>', contrnumber)
  billingcard = find_rentcontract_by_contrnumber('CDouto202401')
  print('rentcontract =>', billingcard)
  contrnumber = 'CDouto202401'
  print('contrnumber =>', contrnumber)
  billingitems = bitems.make_4_billingitems()
  refmonth = rmfs.make_refmonth_or_raise('2026-4')
  billingcard = PydtcBillingCard(
    refmonth=refmonth,
    contrnumber='CDouto202401',
    billingitems=billingitems
  )
  payments = []
  paydate = billingcard.rentcontract.get_duedate_fr_refmonth(refmonth)
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate, value=Decimal(1500))
  payments.append(payment)
  paydate = paydate + relativedelta(days=11)
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate, value=Decimal(1500))
  payments.append(payment)
  billingcard.add_payment_lst(payments)
  billingcard.process()
  print('billingcard =>', billingcard)
  json_str = billingcard.to_json(indent=2, is_for_db=True)
  print('json_str =>', json_str)


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
