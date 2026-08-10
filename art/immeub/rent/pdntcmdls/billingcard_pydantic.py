#!/usr/bin/env python3
"""
art/immeubroutes/pdntcmdls/billing_mod.py

"""
import calendar
import datetime
from dateutil.relativedelta import relativedelta

import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
from decimal import Decimal
from prettytable import PrettyTable
import pydantic
import art.immeub.rent.pdntcmdls.billingitem_pydantic as bipydtc  # bipydtc.PydtcBillingItem
# from art.immeub.rent.pdntcmdls.schema_bizmodels import BillingCard
# locale.setlocale(locale.LC_NUMERIC, "pt_BR")  # "pt_BR.UTF-8"
import art.immeub.rent.pdntcmdls.rentcontract_pydant as rentpydtc  # rentpydtc.PydtcRentContract
import art.immeub.rent.pdntcmdls.immeub_pydant as immeubpydtc  # immeubpydtc.PydtcImmeuble
import art.immeub.rent.pdntcmdls.person_pydant as perspydtc  # perspydtc.PydtcPerson
import art.immeub.rent.testdata.data_example_contract as dataex  # dataex.make_example_contract
import lib.fncfs.credeb_pkg.pay_by_quinhoes_etc as quinhoes  # quinhoes.process_payments
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcafs  # ipcafs.IpcaAPICacherRetriever
import locale
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
MONTHS = rmfs.PT_MESES
PAYMENT_DUE_DAY_IN_MONTH = 10
MONTHLY_FIX_IR_DEC_STR = '0.02'
MONTHLY_FIX_IR_DEC = Decimal(MONTHLY_FIX_IR_DEC_STR)
DECIMAL_ZERO = Decimal('0')


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

  billingcard: BillingCard = pydantic.dataclasses.Field(default_factory=lambda: None)
  refmonth: Optional[datetime.date] = pydantic.Field(default=lambda: rmfs.make_current_refmonth())
  """
  rentcontract: rentpydtc.PydtcRentContract
  refmonth: datetime.date = pydantic.Field(default_factory=lambda: rmfs.make_current_refmonth())
  billingitems: list[bipydtc.PydtcBillingItem] = pydantic.Field(default_factory=lambda: None)
  payments: list[bipydtc.PydtcPayment] = pydantic.Field(default_factory=lambda: [])
  lastpaydate: datetime.date = pydantic.Field(default_factory=lambda: None)
  lastpayprocessdate: datetime.date = pydantic.Field(default_factory=lambda: None)
  credito_no_fecho: Decimal = pydantic.Field(default_factory=lambda: None)
  debito_no_fecho: Decimal = pydantic.Field(default_factory=lambda: None)
  quinhoes_days_vals: list[tuple[int, Decimal]] = pydantic.Field(default_factory=lambda: None)

  @property
  def monthly_fix_ir_dec(self) -> Decimal:
    return self.rentcontract.monthly_fix_ir_dec

  @property
  def location(self) -> immeubpydtc.PydtcImmeuble:
    _location = self.rentcontract.location
    return _location

  @property
  def address(self) -> list[str]:
    _address = self.rentcontract.location.address
    return _address

  @property
  def main_tenant(self) -> perspydtc.PydtcPerson | None:
    _main_tenant = self.rentcontract.main_tenant
    return _main_tenant

  @property
  def rentvalue(self) -> Decimal:
    _rentvalue = self.rentcontract.cur_rentvalue
    return _rentvalue

  def make_n_set_minimum_billingitems(self):
    if self.billingitems is None:
      bitems = self.rentcontract.make_n_get_mininum_billingitems()
      self.billingitems = bitems

  def get_minimum_billingitems(self):
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

  def process_payments_in_month(self):
    """
    Processes payments in month.
    Dispatches processing to quinhoes.process_payments()
    Receives back three variables:
      a) credito_no_fecho
      b) debito_no_fecho
      c) quinhoes_days_vals

    Let's see each one of them:

      a) credito_no_fecho: if payment superseded bill's value.
      b) debito_no_fecho: if payment was below bill's value. This also generates mora.
      c) quinhoes_days_vals: in case of mora, details how this mora is composed in parts.

    """
    total_debito = -self.fatura_total
    self.credito_no_fecho, self.debito_no_fecho = DECIMAL_ZERO, DECIMAL_ZERO
    # first: count payment up to due date
    if len(self.payments) == 0:
      self.credito_no_fecho = total_debito
      return False
    self.payments.sort(key=lambda obj: obj.date)
    # 'credito' é troco, devolução ou adiantamento; 'debito' é item de mora para o próximo mês
    # if one has value, the other must be zeroed: critic (or exception-raising) happens in function process_payments()
    payments = [quinhoes.PaymentInterfaceDateNValue(o.date, o.value) for o in self.payments]
    self.credito_no_fecho, self.debito_no_fecho, self.quinhoes_days_vals = quinhoes.process_payments_in_month(
      valor_a_pagar_como_debito=total_debito,
      payments=payments,
      duedate=self.duedate,
      retrodate_ifinmora=self.retrodate_ifinmora,
      postdate_ifinmora=self.postdate_ifinmora,
      fix_plus_var_ir_dec=self.fix_plus_var_ir_dec,
    )
    return True

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

  def add_payment(self, payment: bipydtc.PydtcPayment):
    """
    At this version, two payments with the same value and date are not allowed.
    TODO this may be allowed by a datetime field instead of only date
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
    self.payments.append(payment)

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
      values = bi.get_the_6_line_values_as_lst()
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
        line = f"mora {moravalue:.2f} foi gerada por {ndays} dias sobre o pagt {payment.value} em {payment.date}"
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
      'cpf':  self.rentcontract.main_tenant.get_fmt_cpf(),
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
    billingitems: list[bipydtc.PydtcBillingItem.MongoJsonRepr]
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
  mkdt = dtfs.make_date_or_raise
  rentcontract = dataex.make_example_contract()
  billingcard = PydtcBillingCard(
    rentcontract=rentcontract,
    refmonth=mkdt('2026-5-1'),
  )
  # billingcard.print_str_table_billingitems()
  print('total', billingcard.str_billingcard())
  mng_dict = billingcard.as_mongo_json_dict()
  print(mng_dict)
  mng_json = billingcard.as_mongo_json_repr()
  print("mng_json = billingcard.as_mongo_json_repr()")
  print(mng_json)
  paydate, payvalue = mkdt('2026-06-11'), Decimal(3000)
  payment = bipydtc.PydtcPayment(
    date=paydate,
    value=Decimal(3000),
  )
  payvalue = payment.value
  paydate = payment.date
  billingcard.add_payment(payment)
  billingcard.process_payments_in_month()
  ostr = """billingcard.process_payment()
  cre = billingcard.credito_no_fecho
  deb = billingcard.debito_no_fecho
  """
  print(ostr)
  cre = billingcard.credito_no_fecho
  deb = billingcard.debito_no_fecho
  moraquinhoes = billingcard.quinhoes_days_vals
  ipca = billingcard.var_ir_as_ipca_dec
  scrmsg = f"""cre={cre:.2f}; deb={deb:.2f} | billsvalue = {billingcard.fatura_total} | duedate={billingcard.duedate} | ipca = {ipca}
   | payvalue={payvalue:.2f} | paydate={paydate} | quinhoes={moraquinhoes}"""
  print(scrmsg)
  report = billingcard.report_quinhoes_days_vals()
  print(report)


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
