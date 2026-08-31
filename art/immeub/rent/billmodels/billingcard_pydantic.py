#!/usr/bin/env python3
"""
art/immeub/rent/billmodels/billingcard_pydantic.py
  Contains the Billing Card (pydantic) model class.

  This class is, so to say, the center of the location rent monthly pay processing.
  It gathers the payments, looks up the previous refmonth for either credit or debt (mora),
    it calculates credit/debt and mora, if any,
    and then closes the month's billing on the last day of paymonth.

  Characteristics of the 'closing':
    a) it depends on manual input of the payor's payment(s) within the (open) paymonth;
    b) the closing date is logical to the last day of paymonth, from which starts the (new) open paymonth.

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
# fndr.dbfetch_billingcard_dictdoc_w_refmonth_n_contrnumber
import art.immeub.rent.mdb.objs_finder_from_mongocollections as fndr
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
find_rentcontract_by_contrnumber = rentpydtc.fetch_rentcontract_by_contrnumber


def dbfetch_billingcard_dictdoc_w_refmonth_n_contrnumber(contrnumber: str, refmonth: datetime.date) -> "PydtcBillingItem":
  dictdoc = fndr.dbfetch_billingcard_docdict_w_refmonth_n_contrnumber_asdict(contrnumber=contrnumber, refmonth=refmonth)
  billingcard = PydtcBillingCard.instantiate_fr_json_dict(dictdoc)
  return billingcard


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
  fech_pagts_n_mora: Optional[pproc.PaymentProcessor] = None
  prev_monthmoras: list[moram.SameMonthMora] = pydantic.Field(exclude=True, default_factory=lambda: None)
  prev_debt: Decimal = pydantic.Field(exclude=True, default_factory=lambda: None)
  prev_credit: Decimal = pydantic.Field(exclude=True, default_factory=lambda: None)

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
    try:
      return self.rentcontract.contrnumber
    except AttributeError:
      pass
    return "n/a"

  @pydantic.computed_field
  @property
  def bc_id(self) -> str:
    try:
      imm_nn = self.rentcontract.location.imm_nickname
      _billing_id = f"{imm_nn}MR{self.rm_as_yyyymm}"
      return _billing_id
    except AttributeError:
      pass
    return "n/a"

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
  def paymo_as_3letrasbaryyyy(self) -> str:
    try:
      paymonth = self.rentcontract.get_pay_duedate_fr_refmonth(self.refmonth)
      mes3letras = rmfs.get_pt_3lettermonth_fr_nmonth(paymonth.month)
      rmstr = f"{mes3letras}/{paymonth.year}"
      return rmstr
    except AttributeError:
      pass
    return "n/a"

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
  def duedate(self) -> datetime.date | None:
    """
    Gets due date from refmonth
    The rule is one month later (the next month) on (up to) day 10
      (at this version, day number may be configured via constant PAYMENT_DUE_DAY_IN_MONTH)
    """
    try:
      if self.refmonth is not None:
        return self.rentcontract.get_duedate_fr_refmonth(self.refmonth)
    except AttributeError:
      pass
    return None

  @property
  def payopendate(self) -> datetime.date | None:
    try:
      if self.refmonth is not None:
        return self.rentcontract.get_pay_windowpayopendate_fr_refmonth(self.refmonth)
    except AttributeError:
      pass
    return None

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
    if self.refmonth is None:
      errmsg = "Error: refmonth is None"
      raise ValueError(errmsg)
    self.billingitems = self.rentcontract.make_n_get_standard_billingitems(self.refmonth)

  def make_n_append_ifany_prev_bc_credit_billingitem(self) -> None:
    """
    IMPORTANT (positive/negative number consideration):
      Notice that for the 'billing card' (this), the convention positive/negative is inverted for credit/debt.
      Here, credit is negative, because the total items in debt is considered positive.

    Notice that in process_payment() the positive/negative is conventioned normally
      for debts as negative numbers and credits as positive numbers.
    """
    seq = len(self.billingitems) + 1
    if self.prev_credit <= DECIMAL_ZERO:
      return
    # noinspection bad-argument-type
    prev_rm = rmfs.make_refmonth_it_minus_n_or_raise(self.refmonth, 1)
    billingitem = bitems.PydtcBillingItem(
      seq=seq,
      refmonth=prev_rm,
      descr="crédito na apuração do mês ant.",
      value=-self.prev_credit,
    )
    self.billingitems.append(billingitem)

  def make_n_append_ifany_prev_bc_mora_billingitem(self) -> None:
    if self.prev_debt >= DECIMAL_ZERO:
      return
    if self.prev_bc_totalmora_ifany == DECIMAL_ZERO:
      return
    seq = len(self.billingitems) + 1
    # noinspection bad-argument-type
    prev_rm = rmfs.make_refmonth_it_minus_n_or_raise(self.refmonth, 1)
    billingitem = bitems.PydtcBillingItem(
      seq=seq,
      refmonth=prev_rm,
      descr="mora acum. aluguel/encargos mês ant.",
      value=prev_bc_total_mora,
    )
    self.billingitems.append(billingitem)

  def get_standard_billingitems(self) -> list[bitems.PydtcBillingItem]:
    if self.billingitems is None or len(self.billingitems) == 0:
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

  def instantiate_fech_pagts_n_mora(self) -> None:
    if self.fech_pagts_n_mora is None:
      if self.billingitems is None:
        errmsg = "Error: billingitems is None when attempting to instantiate fech_pagts_n_mora."
        raise ValueError(errmsg)
      ongoing_debt = -self.mesreftotal
      # noinspection bad-argument-type
      self.fech_pagts_n_mora = pay.PaymentProcessor(
        ongoing_debt=ongoing_debt,
        duedate=self.duedate,
        fix_ir_dec=self.monthly_fix_ir_dec,
        has_ipca=True,
      )


  def lookup_n_set_mora_in_previous_refmonth_ifany(self) -> None:
    if self.prev_monthmoras is not None:
      return
    self.prev_monthmoras = []
    self.prev_debt = DECIMAL_ZERO
    self.prev_credit = DECIMAL_ZERO
    previous_rm = rmfs.make_refmonth_it_minus_n_or_raise(self.refmonth, 1)
    previous_bc = None
    try:
      previous_bc = dbfetch_billingcard_dictdoc_w_refmonth_n_contrnumber(
        contrnumber=self.contrnumber, refmonth=previous_rm
      )
      self.prev_monthmoras = previous_bc.fech_pagts_n_mora.monthmoras
      self.prev_debt = previous_bc.fech_pagts_n_mora.ongoing_debt
      self.prev_credit = previous_bc.fech_pagts_n_mora.ongoing_credit
    except AttributeError:
      pass

  def verify_previous_credit_or_debt_ifso_mk_bitem(self) -> None:
    self.lookup_n_set_mora_in_previous_refmonth_ifany()
    if self.prev_credit > DECIMAL_ZERO:
      self.make_n_append_ifany_prev_bc_credit_billingitem()
      return
    if self.prev_debt < DECIMAL_ZERO:
        self.make_n_append_ifany_prev_bc_mora_billingitem()

  def process_payments_in_month(self) -> None:
    """
    Processes payments in month.

    The process flow is the following:
      1) run, or check its presence, the standard billing items formation;
         the standard billing items recur monthly;
      2) look up whether there is mora in the previous refmonth;
         verify, in the previous billing card, whether there is a mora record;
         the mora only exists if it's verified in the previous refmonth;
      3) (this one is not implemented yet) verify an 'adhoc' extra billing item in database;
      4) verify that payments were entered or no payments were done;
      5) after all items above, run self.fech_pagts_n_mora.process_payments() [or process() which is the same]

    From 'fech_pagts_n_mora', it receives back three variables:
      a) credito_no_fecho (or ongoing_credit): if payment superseded bill's value;
         'credito' é troco, devolução ou adiantamento;
      b) debito_no_fecho (or ongoing_debt): if payment was below bill's value. This also generates mora;
         this will also be 'mora' for the next refmonth;
         'debito' é item de mora para o próximo mês;
        Obs:
          credit and debt cannot both have values: either one has and the other is zero or viceversa;
          credit must be positive; debt, negative;

      c) monthmoras: which contains piecewise mora objects according to dates;

    Notice also there is a (boolean/flag) variable in self.fech_pagts_n_mora
      which becomes True after processing making 'process' is run-only-once action.
    (For a reprocess, the client will need to reinstantiate the object (this).)
    """
    if self.billingitems is None or len(self.billingitems) == 0:
      # Step 1: run, or check its presence, the standard billing items formation;
      self.make_n_set_standard_billingitems()
    # Step 2: look up whether there is mora in the previous refmonth;
    self.verify_previous_credit_or_debt_ifso_mk_bitem()
    self.lookup_n_set_mora_in_previous_refmonth_ifany()
    self.instantiate_fech_pagts_n_mora()
    if not self.fech_pagts_n_mora.payment_process_finished:
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
    # noinspection bad-argument-type
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
    paymonth = self.refmonth + relativedelta.relativedelta(months=1)
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
      # notice: the payments list does not belong to this class, but to self.fech_pagts_n_mora.payments
      # because of that, 'billingitems' must be initiated before 'payments'
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
    for bi in self.billingitems:
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


def make_n_get_billingcard_w_1contrnumber_2refmonth(contrnumber, refmonth):
  print('Creating billing card for contrnumber =>', contrnumber, 'refmonth =>', refmonth)
  billingcard = PydtcBillingCard(
    contrnumber=contrnumber,
    refmonth=refmonth,
  )
  return billingcard

def process_billingcard_w_payments(billingcard, payments):
  billingcard.make_n_set_standard_billingitems()
  billingcard.add_payment_lst(payments)
  billingcard.process()
  # print('billingcard =>', billingcard)
  json_str = billingcard.to_json(indent=2, is_for_db=True)
  print('json_str =>', json_str)


def adhoctest1():
  """

  """
  contrnumber = 'CDouto202401'
  # refmonth 2026-4
  refmonth = rmfs.make_refmonth_or_raise('2026-4')
  billingcard = make_n_get_billingcard_w_1contrnumber_2refmonth(contrnumber, refmonth)
  payments = []
  payment = intrfc.PaymentInterfaceDateNValue(date=billingcard.duedate, value=Decimal(1500))
  payments.append(payment)
  paydate = billingcard.duedate + relativedelta(days=11)
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate, value=Decimal(1500))
  payments.append(payment)
  process_billingcard_w_payments(billingcard, payments)


def adhoctest2():
  contrnumber = 'CDouto202401'
  # refmonth 2026-5
  refmonth = rmfs.make_refmonth_or_raise('2026-5')
  billingcard = make_n_get_billingcard_w_1contrnumber_2refmonth(contrnumber, refmonth)
  payments = []
  payment = intrfc.PaymentInterfaceDateNValue(date=billingcard.duedate, value=Decimal(2500))
  payments.append(payment)
  paydate = billingcard.duedate.replace(day=27)
  payment = intrfc.PaymentInterfaceDateNValue(date=paydate, value=Decimal(1500))
  payments.append(payment)
  process_billingcard_w_payments(billingcard, payments)


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
