#!/usr/bin/env python3
"""
art/immeubroutes/pydantmodels/billing_mod.py

"""
import datetime
import functools  # for functools.reduce (that sums up total items to general total)
import lib.datesetc.refmonth_fs as rmfs
from decimal import Decimal
from prettytable import PrettyTable
import pydantic
import art.immeub.rent.bill.billingitem_pydantic as bipydtc  # bipydtc.PydtcBillingItem
# from art.immeub.rent.pydantmodels.schema_bizmodels import BillingCard
# locale.setlocale(locale.LC_NUMERIC, "pt_BR")  # "pt_BR.UTF-8"
import art.immeub.rent.pydantmodels.rentcontract_pydant as rentpydtc  # rentpydtc.PydtcRentContract
import art.immeub.rent.pydantmodels.immeub_pydant as immeubpydtc  # immeubpydtc.PydtcImmeuble
import art.immeub.rent.pydantmodels.person_pydant as perspydtc  # perspydtc.PydtcPerson
import art.immeub.rent.bill.data_example_contract as dataex  # dataex.make_example_contract
import lib.fncfs.credeb_pkg.pay_by_quinhoes_etc as quinhoes  # quinhoes.process_payments
import locale
locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
MONTHS = rmfs.PT_MESES
PAYMENT_DUE_DAY_IN_MONTH = 10
MONTHLY_FIX_IR_DEC_STR = '0.02'
MONTHLY_FIX_IR_DEC = Decimal(MONTHLY_FIX_IR_DEC_STR)
DECIMAL_ZERO = Decimal('0')


class PydtcBillingCard(pydantic.BaseModel):
  """

  billingcard: BillingCard = pydantic.dataclasses.Field(default_factory=lambda: None)
  refmonth: Optional[datetime.date] = pydantic.Field(default=lambda: rmfs.make_current_refmonth())
  """
  rentcontract: rentpydtc.PydtcRentContract
  refmonth: datetime.date = pydantic.Field(default_factory=lambda: rmfs.make_current_refmonth())
  today: datetime.date = pydantic.Field(default_factory=lambda: datetime.date.today())
  billingitems: list[bipydtc.PydtcBillingItem] = pydantic.Field(default_factory=lambda: None)
  payments: list[bipydtc.PydtcPayment] = pydantic.Field(default_factory=lambda: [])
  monthly_fix_ir_dec: Decimal = pydantic.Field(default_factory=lambda: MONTHLY_FIX_IR_DEC)
  credito_no_fecho: Decimal = pydantic.Field(default_factory=lambda: None)
  debito_no_fecho: Decimal = pydantic.Field(default_factory=lambda: None)

  @property
  def location(self) -> immeubpydtc.PydtcImmeuble:
    _location = self.rentcontract.immeuble
    return _location

  @property
  def address(self) -> list[str]:
    _address = self.rentcontract.immeuble.address
    return _address

  @property
  def main_tenant(self) -> perspydtc.PydtcPerson:
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
    totais = map(lambda obj: obj.total_item, self.billingitems)
    _fatura_total = functools.reduce(lambda x, y: x + y, totais, 0)
    return _fatura_total

  def process_payment(self):
    total_debito = -self.fatura_total
    # first: count payment up to due date
    if len(self.payments) == 0:
      return False
    self.payments.sort(key=lambda obj: obj.date)
    # 'credito' é troco, devolução ou adiantamento; 'debito' é item de mora para o próximo mês
    # if one has value, the other must be zeroed: critic (or exception-raising) happens in function process_payments()
    payments = [quinhoes.PaymentInterfaceDateNValue(o.date, o.value) for o in self.payments]
    self.credito_no_fecho, self.debito_no_fecho = quinhoes.process_payments(
      valor_a_pagar_como_debito=total_debito,
      payments=payments,
      duedate=self.duedate,
      monthly_fix_ir_dec=self.rentcontract.monthly_fix_ir_dec,
    )
    return True

  def has_been_paid_after_payment_processed(self):
    if self.debito_no_fecho == DECIMAL_ZERO:
      return True
    return False

  def str_table_billingitems(self):
    """
    outstr = f"{self.descr} | {self.refmmm} | {fmt_value} | {self.mora} | {self.total_item}"
    """
    table = PrettyTable()
    headers = ["seq",  "descrição", "data-ref",  "valor-item", "mora-item", "total-item"]
    table.field_names = headers
    for bi in self.get_minimum_billingitems():
      values = bi.get_the_6_line_values_as_lst()
      table.add_row(values)
    str_table = str(table)
    return str_table

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
  rentcontract = dataex.make_example_contract()
  billingcard = PydtcBillingCard(
    rentcontract=rentcontract
  )
  # billingcard.print_str_table_billingitems()
  print('total', billingcard.str_billingcard())
  mng_dict = billingcard.as_mongo_json_dict()
  print(mng_dict)
  mng_json = billingcard.as_mongo_json_repr()
  print("mng_json = billingcard.as_mongo_json_repr()")
  print(mng_json)


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
