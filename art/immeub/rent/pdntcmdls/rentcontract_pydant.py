#!/usr/bin/env python3
"""
art/immeub/rent/pdntcmdls/rentcontract_pydant.py
  Contains Pydantic class Contract.
  Contract is 'component' of the BillingCard app.
  (@see diagram context with BillignCard, BillingItem, Contract, Person, etc.).

# from dinero.currencies import BRL
from dinero.currencies import BRL
import j_son
"""
import calendar
from prettytable import PrettyTable
import datetime
import dinero
from decimal import Context, Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from typing import List
import pydantic
import typing
# from typing_extensions import Annotated
import art.immeub.rent.pdntcmdls.immeub_pydant as immeub  # immueb.Immeuble
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.Person
import art.immeub.rent.billmodels.billingitem_pydantic as bitem  # pers.Person
import art.immeub.rent.pdntcmdls as init
import art.immeub.tribs.onproperties.mongo_tribs_retriever as funesbom
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch  # mngfetch.get_rentcontract_by_number
import art.immeub.rent.mdb.mongofs as mngfs  # .RentMongo
from tabulate import tabulate
from lib.fncfs.credeb_pkg.credit_debt_fs import ONE_THOUSANDTH_AS_STR
DEFAULT_3LETTER_CURRENCY = init.DEFAULT_3LETTER_CURRENCY
PAYMENT_DUE_DAY_IN_MONTH = 10
DECIMAL_ZERO = Decimal(0)
DEFAULT_MONTHLY_FIX_IR_DEC = Decimal(init.DEFAULT_MONTHLY_FIX_IR_DEC)
MORA_M_MINUS_N_STR = init.MORA_M_MINUS_N
MORA_BEGINS_ON_DAY = 1
CONTRNUMBERTYPE = typing.Annotated[str, pydantic.StringConstraints(max_length=12)]


def mk_contrnumber_w_immnickname_n_refmstr(
    imm_nickname: str, refmonth: datetime.datetime | str
  ) -> str:
  if imm_nickname is None:
    errmsg = f"Error: location imm_nickname cannot be None."
    raise ValueError(errmsg)
  if refmonth is None:
    refmonth = rmfs.make_current_refmonth()
  if not isinstance(refmonth, datetime.datetime):
    refmonth = rmfs.make_refmonth_or_raise(refmonth)
  refmstr = refmonth.strftime('%Y%m')
  contrnumber = f"{imm_nickname}{refmstr}"
  return contrnumber


def find_immeuble_by_nickname(imm_nickname):
  location = mngfetch.find_immeuble_by_nickname_as_dict(imm_nickname)
  return location


def find_rentcontract_by_contrnumber(contrnumber) -> "PydtcRentContract":
  rentcontractdoc = mngfetch.get_rentcontract_by_number(contrnumber)
  rentcontract = PydtcRentContract.instantiate_fr_jsondict(rentcontractdoc)
  return rentcontract


def get_conventioned_mora_m_minus_n():
  try:
    mora_m_minus_n = int(MORA_M_MINUS_N_STR)
    return mora_m_minus_n
  except ValueError:
    pass
  return None


def calc_finmontant_w_inimontant_n_periodic_indices(inimontant, p_indices):
  """
  p_reajustes is a list of tuples with date and Decimal
  """
  indices = p_indices[:]  # copying it
  indices.sort()  # guarantess its in ascendant order
  finmontant = inimontant
  while len(indices) > 0:
    fraction = indices.pop(0)
    finmontant = finmontant * (1 + fraction)
  return finmontant


def make_dinero_fr_decimal(dec, din_currency_dictlike):
  decimal_ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  dec = Decimal(dec, decimal_ctx)
  dec.quantize(Decimal(ONE_THOUSANDTH_AS_STR))
  din = dinero.Dinero(dec, din_currency_dictlike)
  return din


class Reajuste(pydantic.BaseModel):
  """
  Models a contract 'reajuste'
  Contains 4 (four) main attributes:
    reajuste_dt: a date which also derive a refmonth or annual anniversary
    reajuste_idx: the decimal index that increases the 'valuebefore'
    valuebefore: the base value on which the 'reajuste' is incident
    reajuste_sigla: an acronym that represents the source from which idx is found on date

  This class is 'composed' by RentContract which may keep a list of its objects.
  """
  reaj_date: datetime.date
  prevalue: Decimal
  reaj_mul_fo_incr: Decimal
  reaj_idxsigla: str = 'IGP-M'

  @property
  def reaj_refmonth(self) -> datetime.date:
    """
    Gets 'reajuste refmonth'.
    'reajuste refmonth' is 'reajuste date' on day 1
    """
    if self.reaj_date.day == 1:
      # refmonth is, by convention, a date on day 1
      return self.reaj_date
    refmonth = self.reaj_date.replace(day=1)
    return refmonth

  @property
  def postvalue(self) -> Decimal:
    """ it's valuebefore increased by reajuste index (@see the "montant" expression below)"""
    if self.reaj_mul_fo_incr < DECIMAL_ZERO:
      # valueafter, by convention, cannot be less than valuebefore
      return self.prevalue
    # the "montant" expression -> mf = mi * (1 + i)
    va = self.prevalue * (1 + self.reaj_mul_fo_incr)
    return va

  def raise_if_reajuste_has_inconsistent_date(self, upperlimitdate: datetime.date):
    """ raises ValueError on two conditions: 1 date in the future 2 date after contract's end-date"""
    upperlimitdate = dtfs.make_date_or_raise(upperlimitdate)
    today = datetime.date.today()
    if self.reaj_refmonth > today:
      errmsg = f"reajuste refmonth [{self.reaj_refmonth}] cannot be later than today [{today}]."
      raise ValueError(errmsg)
    if self.reaj_refmonth > upperlimitdate:
      errmsg = f"reajuste refmonth [{self.reaj_refmonth}] cannot be later than contract's final date [{upperlimitdate}]."
      raise ValueError(errmsg)


class PydtcRentContract(pydantic.BaseModel):
  """

  # imm_nickname: str = 'CDouto'
  contrnumber: str = pydantic.PrivateAttr(default_factory=lambda: None)
  CPFTYPE = Annotated[str, StringConstraints(pattern=r"counterbar d{11}")]

  """
  contrnumber: CONTRNUMBERTYPE
  location: immeub.PydtcImmeuble
  inidate: datetime.date
  ori_rentvalue: typing.Annotated[Decimal, pydantic.Field(max_digits=12, decimal_places=4)]
  tenants: typing.Optional[List[pers.PydtcPerson]] = None
  guarantors: typing.Optional[List[pers.PydtcPerson]] = None
  payee: typing.Optional[pers.PydtcPerson] = None
  nmonths_duration: int = 30
  has_proptax: bool = True
  has_incendtarif: bool = True
  has_condtarif: bool = True
  currency3letter: str = 'BRL'
  reajustes: list[Reajuste] = pydantic.dataclasses.Field(default_factory=lambda: [])
  monthly_fix_ir_dec: Decimal = pydantic.dataclasses.Field(default_factory=lambda: DEFAULT_MONTHLY_FIX_IR_DEC)
  has_ipca: bool = True
  _cur_rentvalue: Decimal = pydantic.PrivateAttr(default_factory=lambda: None)

  @pydantic.model_validator(mode='before')
  @classmethod
  def allow_fetching_location_by_key(cls, values: dict) -> dict:
    # If the user passed a raw string/number instead of a contract object
    if "imm_nickname" in values and "location" not in values:
      imm_nickname = values.pop("imm_nickname")
      location = immeub.get_immeuble_by_nickname(imm_nickname)
      values["location"] = location
    if "tenants_cpfs" in values and "tenants" not in values:
      tenants_cpfs = values.pop("tenants_cpfs")
      values["tenants"] = pers.fetch_persons_by_cpfs(tenants_cpfs)
    if "guarantors_cpfs" in values and "guarantors" not in values:
      guarantors_cpfs = values.pop("guarantors_cpfs")
      values["guarantors"] = pers.fetch_persons_by_cpfs(guarantors_cpfs)
    if "payee_cpf" in values and "payee" not in values:
      payee_cpf = values.pop("payee_cpf")
      values["payee"] = pers.make_example_person_123456781()
    return values

  def get_pay_duedate_fr_refmonth(self, refmonth):
    if refmonth is None:
      paymonth = datetime.date.today()
    else:
      paymonth = refmonth + relativedelta(months=1)
    year, month = paymonth.year, paymonth.month
    duedate = datetime.date(year=year, month=month, day=self.get_payment_dueday_in_month())
    return duedate

  @staticmethod
  def get_monthsday_when_moracount_begins():
    return MORA_BEGINS_ON_DAY

  def get_date_when_mora_begins_w_refmonth(
      self, refmonth: datetime.date | str
    ) -> datetime.date:
    """
    retrodate is refmonth itself
    (this rule is not configurable as it seems stable in practice)

    Explaination:
    =============

    When 'in mora', the mora days count is not from duedate (generally 10),
      but from the beginning of the month;
    """
    refmonth = rmfs.make_refmonth_or_raise(refmonth)
    paymonth_on_day1 = refmonth + relativedelta(months=1)
    day = self.get_monthsday_when_moracount_begins()
    if day == 1:
      return paymonth_on_day1
    date_when_mora_begins = paymonth_on_day1.replace(day=day)
    return date_when_mora_begins

  @staticmethod
  def get_lastmonthsday_for_mora(
      paymonth: datetime.date | str
    ) -> int:
    """
    It's the last day in month
    """
    paymonth = rmfs.make_refmonth_or_raise(paymonth)
    _, lastday_inmonth = calendar.monthrange(paymonth.year, paymonth.month)
    return lastday_inmonth

  def get_mora_endingdate_w_refmonth(self, refmonth: datetime.date) -> datetime.date:
    """
    postdate is the last day of month 'refmonth'
    (this rule is not configurable as it seems stable in practice)

    Explaination:
    =============

    When 'in mora' and when a payment is incomplete,
      the remaining debt is 'closed' receiving the mora amount
      that 'completes' the month.

    Example:
      Let's consider the following payment:
      a) duedate is on the 10th day of the month
      b) an incomplete payment happend on the 20th day of the month
    What happens?
      a) the whole month's debt is increased with 20 days 'mora';
      b) the payment credit pays incompletely this updated bill;
      c) the remaining debts increases under the remaining days (20 to month's end);
    So, this attribute gives the date that the c) operation needs as parameter.
    """
    refmonth = rmfs.make_refmonth_or_raise(refmonth)
    paymonth = refmonth + relativedelta(months=1)
    _, ndays_inmonth = calendar.monthrange(refmonth.year, refmonth.month)
    year, month, day = paymonth.year, paymonth.month, ndays_inmonth
    day = self.get_lastmonthsday_for_mora(paymonth=paymonth)
    lastdate_inmonth = datetime.date(year=year, month=month, day=day)
    return lastdate_inmonth

  def make_n_get_standard_billingitems(
      self, p_refmonth: datetime.date | str | None = None
    ) -> list[bitem.PydtcBillingItem]:
    """
    Creates the monthly BillingCard 'main mold'.
    (The 'main mold' are the repetitive billing items. Others enter afterward.)
    The main (generally) items are:
      1 rent itself
      2 iptu (the municipal property tax)
      3 cond (the condominium service tariff)
      4 funesbom (which is an annual fire dept charge)
    If other items apply, they must be included at the end of the billing card 'making' process.
    """
    refmonth = rmfs.make_current_refmonth() \
        if p_refmonth is None \
        else rmfs.make_refmonth_or_raise(p_refmonth)
    billingitems = []
    bi_seq = 1
    bi = bipydtc.PydtcBillingItem(
      seq=bi_seq,
      descr="Aluguel mensal",
      refmonth=refmonth,
      value=self.cur_rentvalue,
    )
    billingitems.append(bi)
    if self.has_proptax:
      value, descr = self.location.fetch_iptu_value_n_descr_w_refmonth(refmonth)
      if value:
        bi_seq += 1
        bi = bipydtc.PydtcBillingItem(
          seq=bi_seq,
          descr=f"IPTU ({descr})",
          refmonth=refmonth,
          value=value,
        )
        billingitems.append(bi)
    if self.has_condtarif:
      value, descr = self.location.fetch_condtarifa_n_descr_w_refmonth(refmonth)
      if value:
        bi_seq += 1
        bi = bipydtc.PydtcBillingItem(
          seq=bi_seq,
          descr=descr,
          refmonth=refmonth,
          value=value,
        )
        billingitems.append(bi)
    incendtarif, incend_descr = self.location.fetch_funesbom_value_n_descr_w_refmonth(refmonth)
    if incendtarif is not None:
      value, descr = incendtarif, incend_descr
      if value:
        bi_seq += 1
        bi = bipydtc.PydtcBillingItem(
          seq=bi_seq,
          descr=f"Funesbom ({descr})",
          refmonth=refmonth,
          value=value,
        )
        billingitems.append(bi)
    return billingitems

  def get_incendtarif_n_descr_if_available(self) -> tuple[Decimal | None, str]:
    imovel_apelido = self.location.imm_nickname
    incendtarif, descr = funesbom.get_incendtarif_fo_location_if_available(imovel_apelido)
    return incendtarif, descr

  @property
  def mora_m_minus_n(self) -> int:
    return get_conventioned_mora_m_minus_n() or 2

  @property
  def main_tenant(self) -> pers.PydtcPerson | None:
    try:
      return self.tenants[0]
    except IndexError:
      return None

  @property
  def other_tenants_ifany(self) -> list[pers.PydtcPerson]:
    if self.tenants is not None:
      if len(self.tenants) > 1:
        return self.tenants[1:]
    return []

  def add_reajuste_w_dt_n_idx(self, reajuste_dt: datetime.date | str, reajuste_idx: Decimal, reajuste_sigla: str = 'IGP-M'):
    reajuste_dt = dtfs.make_date_or_raise(reajuste_dt)
    reajuste = Reajuste(
      reaj_date=reajuste_dt, reaj_mul_fo_incr=reajuste_idx, prevalue=self.cur_rentvalue, reaj_idxsigla=reajuste_sigla
    )    # reajuste.raise_if_inconsistent_to_today_n_contractsend(self.findate)
    # reajuste.calc_n_set_cur_rentvalue()
    self.reajustes.append(reajuste)
    self.calc_n_set_cur_rentvalue()

  def calc_n_set_cur_rentvalue(self):
    if len(self.reajustes) == 0:
      self._cur_rentvalue = self.ori_rentvalue
      return
    self.reajustes.sort(key = lambda obj: obj.reaj_date)
    last_reajuste = self.reajustes[-1]
    self._cur_rentvalue = last_reajuste.postvalue

  def make_triplelist_date_reajuste_newrentvalue(self):
    # first triple has 0.0 reajuste
    triple = self.inidate, DECIMAL_ZERO, self.ori_rentvalue
    date_reajuste_newrentvalue_triplelist = [triple]
    for reajuste in self.reajustes:
      triple = reajuste.reaj_refmonth, reajuste.reaj_mul_fo_incr, reajuste.postvalue
      date_reajuste_newrentvalue_triplelist.append(triple)
    return date_reajuste_newrentvalue_triplelist

  def form_dates_reajustes_newrentvalues(self):
    str_dates_reajustes_newrentvalues = []
    for triple in self.make_triplelist_date_reajuste_newrentvalue():
      pdate, reajuste, newrentvalue = triple
      strdate = pdate.strftime('%d/%m/%Y')
      fmt_value = f"{newrentvalue:.02f}"
      reaj_pct = reajuste * 100
      fmt_reaj_pct = f"{reaj_pct:.02f}%"
      line = strdate, fmt_reaj_pct, fmt_value
      str_dates_reajustes_newrentvalues.append(line)
    return str_dates_reajustes_newrentvalues

  def tabulate_dates_reajustes_newrentvalues(self):
    str_dates_reajustes_newrentvalues = self.form_dates_reajustes_newrentvalues()
    # Print the formatted table
    valor_col_title = f"valor em {self.get_currency_symbol()}"
    headers = ["testdata",  "reajuste %", valor_col_title]
    print(tabulate(str_dates_reajustes_newrentvalues, headers=headers, tablefmt="grid"))

  def pprint_dates_n_rentvalues(self):
    str_dates_reajustes_newrentvalues = self.form_dates_reajustes_newrentvalues()
    table = PrettyTable()
    valor_col_title = f"valor em {self.get_currency_symbol()}"
    headers = ["testdata",  "reajuste %", valor_col_title]
    table.field_names = headers
    [table.add_row(r) for r in str_dates_reajustes_newrentvalues]
    print(table)

  @property
  def cur_rentvalue(self) -> Decimal:
    if self._cur_rentvalue is not None:
      return self._cur_rentvalue
    # the next line is not necessary but helped avoid the IDE type-complaining
    self._cur_rentvalue = self.ori_rentvalue
    self.calc_n_set_cur_rentvalue()
    return self._cur_rentvalue

  @property
  def imm_nickname(self) -> str:
    try:
      return self.location.imm_nickname
    except (AttributeError, NameError):
      pass
    return 'n/a'

  def to_json_str(self, indent: int = 2, is_for_db: bool = False):
    """
    Produces the Object's JSON string representation.
    If parameter is_for_db is True, fields {'location','tenants','guarantors'} are excluded.
    Else, if parameter is_for_db is False, the embedded objects go included.
    """

    param_set = set()
    if is_for_db:
      param_set.add('location')
      param_set.add('tenants')
      param_set.add('guarantors')
    # jsondict = self.model_dump(exclude=param_set)
    # # remove_none_values_fr_dict_recurs
    # print('jsondict', jsondict)
    jsondump = self.model_dump_json(exclude=param_set, indent=indent)
    # jsondump = json.dumps(jsondict, indent=2)
    return jsondump

  def to_json_str_for_db(self):
    """
    Produces the Object's JSON string representation for MongoDB (location and persons go with primary keys).
    Dispatches to to_json_str() with is_for_db=True.
    """
    return self.to_json_str(indent=indent, is_for_db=True)

  @pydantic.computed_field
  @property
  def tenants_cpfs(self) -> list[str]:
    if self.tenants is None:
      return []
    return [p.cpf for p in self.tenants]

  @pydantic.computed_field
  @property
  def guarantors_cpfs(self) -> list[str]:
    if self.guarantors is None:
      return []
    return [p.cpf for p in self.guarantors]

  @pydantic.computed_field
  @property
  def payee_cpf(self) -> str:
    if self.payee is None:
      return "n/a"
    return self.payee.cpf

  @pydantic.computed_field
  @property
  def imm_nickname(self) -> immeub.IMMNICKNAMETYPE:
    if self.location is not None:
      return self.location.imm_nickname
    if self.contrnumber is not None:
      try:
        imm_nn = self.contrnumber[:-6]
        return imm_nn
      except IndentationError:
        pass
    return "n/a"

  @classmethod
  def instantiate_fr_jsondict(cls, jsondict) -> "PydtcRentContract":
    """
    The updated version with cls.model_validate(cleaned_data)
    The previous one had cls(**pdict)
    """
    if jsondict is None:
      return None
    jsondict = mngfs.remove_none_values_fr_dict_recurs(jsondict)
    # if 'location' in cleaned_data:
    # pass
    obj = cls.model_validate(jsondict)
    return obj

  @property
  def commasep_landlords(self) -> str:
    try:
      landlords = self.location.owners
      if len(landlords) > 0:
        return self.location.comma_sep_owner_names()
    except (AttributeError, NameError):
      pass
    return 'n/a'

  def commasep_tenants(self):
    ostr = ""
    if len(self.tenants) > 0:
      for tenant in self.tenants:
        ostr += tenant.nomecompleto + ", "
      ostr = ostr.rstrip(", ")
      return ostr
    return 'n/a'

  def commasep_fiadores(self):
    ostr = "n/a"
    if self.guarantors is not None:
      if len(self.guarantors) > 0:
        for fiador in self.guarantors:
          ostr += fiador.nomecompleto + ", "
        ostr = ostr.rstrip(", ")
    return ostr

  @property
  def din_currency_dictlike(self) -> dinero.types.Currency:
    dincurrencydict = getattr(dinero.currencies, self.currency3letter)
    return dincurrencydict

  def make_din_fr_dec(self, dec) -> Decimal:
    din = make_dinero_fr_decimal(dec, self.din_currency_dictlike)
    return din

  @property
  def din_cur_rentvalue(self) -> Decimal:
    return self.make_din_fr_dec(self.cur_rentvalue)

  @property
  def din_ori_rentvalue(self) -> Decimal:
    return self.make_din_fr_dec(self.ori_rentvalue)

  @staticmethod
  def morarules():
    """
    incidence is on payment still remaining

    This method is still not fully implemented
    For the time being, the rules are hardcoded
    """
    actions = []
    action = 'INCIDENT_IF_PAYMENT_MISSED_ON_DUEDATE'
    actions.append(action)
    action = 'MULTIPLIER_CONTAINS_FIXMONTHLYIR_PARCEL'
    actions.append(action)
    action = 'MULTIPLIER_CONTAINS_VARMONTHLYINFL_PARCEL'
    actions.append(action)
    return actions

  @property
  def findate(self) -> datetime.date:
    _findate = self.inidate + relativedelta(months=self.nmonths_duration) - relativedelta(days=1)
    return _findate

  @staticmethod
  def get_payment_dueday_in_month() -> int:
    return PAYMENT_DUE_DAY_IN_MONTH

  def get_duedate_fr_refmonth(self, p_refmonth: datetime.date) -> datetime.date:
    """
    Gets due date from refmonth
    The rule is one month later (the next month) on (up to) day 10
      (at this version, day number may be configured via constant PAYMENT_DUE_DAY_IN_MONTH)
    """
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    nextmonth = refmonth + relativedelta(months=1)
    dueday = self.get_payment_dueday_in_month()
    duedate =  nextmonth.replace(day=dueday)
    return duedate

  def get_currency_symbol(self):
    din = self.make_din_fr_dec(self.ori_rentvalue)
    return din.currency['symbol']

  def fmt_din(self, dec):
    din = self.make_din_fr_dec(dec)
    fmt_din = f"{din.currency['symbol']} {din.raw_amount:.02f}"
    return fmt_din

  def __repr__(self):
    """
    pdate.strftime('%b %Y %I:%M %p') -> example: Jun 2026 12:00 AM
    """
    datafinal = self.findate.strftime('%d/%m/%Y')
    ostr = f"Locação: {self.contrnumber} | duração: {self.nmonths_duration} meses (até {datafinal})"
    ostr += f" | alug ini: {self.fmt_din(self.ori_rentvalue)} | alug atual: {self.fmt_din(self.cur_rentvalue)}"
    qtd_reajustes = len(self.reajustes)
    ostr += f" (nº reajustes: {qtd_reajustes})"
    return ostr

  def line(self):
    return self.__repr__()

  def __str__(self):
    """

    ori_rentvalue={self.ori_rentvalue}

    """
    ostr = f"""{self.__class__.__name__}
    sigla/apelido={self.imm_nickname} | contrnumber={self.contrnumber}
    inidate={self.inidate} | nmonths_duration={self.nmonths_duration} | findate={self.findate}  
    ori_rentvalue={self.fmt_din(self.ori_rentvalue)} | cur_rentvalue={self.fmt_din(self.cur_rentvalue)}
    has_proptax={self.has_proptax} | has_incendtarif={self.has_incendtarif} | has_condtarif={self.has_condtarif}
    tenants={self.commasep_tenants()} | fiadores={self.commasep_fiadores()} | landlords={self.commasep_landlords}
    reajustes={self.reajustes}
    """
    return ostr


def adhoctest1():
  """
  persondoc = PersonDoc(
    fullname="John Doe",
    cpf="12345678909",
    phonenumber="99991111",
    email="johndoe@example.com",
    docid="1234567",
  )
  print(persondoc)


    tenants=[person],
    fiadores=[person],
  """
  persons = mngfetch.get_persons_by_cpfs_as_jsonstrlst([])
  if persons is None or len(persons) == 0:
    print('No persons found. Returning.')
    return
  person = persons[0]
  print('person =', person)
  location = immeub.get_immeuble_ex()
  print('location =', type(location), location)
  rentvalue = Decimal(1000)
  inidate = rmfs.make_refmonth_or_raise('202404')
  contrnumber = location.imm_nickname + inidate.strftime('%y%m')
  rent = PydtcRentContract(
    contrnumber=contrnumber,
    location=location,
    inidate=inidate,
    ori_rentvalue=rentvalue,
    nmonths_duration=30,
    has_proptax=True,
    has_incendtarif=True,
    has_condtarif=True,
    # currency3letter=DEFAULT_3LETTER_CURRENCY,
    # imm_nickname='Jack',
  )
  print(rent)
  rent.add_reajuste_w_dt_n_idx('2025-1-1', Decimal('0.035'))
  rent.add_reajuste_w_dt_n_idx('2026-1-1', Decimal('0.027'))
  print(rent)
  print(rent.line())
  rent.tabulate_dates_reajustes_newrentvalues()
  rent.pprint_dates_n_rentvalues()
  bitems = rent.make_n_get_standard_billingitems()
  print(bitems)


def adhoctest2():
  contrnumber = 'CDouto202401'
  rentcontract_doc = mngfetch.get_rentcontract_by_number(contrnumber)
  print('contrnumber', contrnumber)
  print('rentcontract_doc', rentcontract_doc)
  rentcontract = PydtcRentContract.instantiate_fr_jsondict(rentcontract_doc)
  print(rentcontract)



def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest2()
