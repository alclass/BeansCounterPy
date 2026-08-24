#!/usr/bin/env python3
"""
art/immeub/rent/pdntcmdls/rentcontract_pydant.py
  Contains Pydantic class Contract.
  Contract is 'component' of the BillingCard app.
  (@see diagram context with BillignCard, BillingItem, Contract, Person, etc.).

# from dinero.currencies import BRL
"""
import calendar
from prettytable import PrettyTable
import datetime
from decimal import Context, Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
import dinero
from dinero.currencies import BRL
from typing import List
import pydantic
import typing
import art.immeub.rent.pdntcmdls.immeub_pydant as immeub  # immueb.Immeuble
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.Person
import art.immeub.rent.pdntcmdls as init
# incendmod.get_incendtarif_fo_location_if_available(imovel_apelido)
import art.immeub.tribs.onproperties.mongo_tribs_retriever as funesbom
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch  # mngfetch.get_rentcontract_by_number
import art.immeub.rent.billmodels.billingitem_pydantic as bipydtc  # bipydtc.BillingItem
from tabulate import tabulate
from lib.fncfs.credeb_pkg.credit_debt_fs import ONE_THOUSANDTH_AS_STR
DEFAULT_3LETTER_CURRENCY = init.DEFAULT_3LETTER_CURRENCY
PAYMENT_DUE_DAY_IN_MONTH = 10
DECIMAL_ZERO = Decimal(0)
DEFAULT_MONTHLY_FIX_IR_DEC = Decimal(init.DEFAULT_MONTHLY_FIX_IR_DEC)
MORA_M_MINUS_N_STR = init.MORA_M_MINUS_N


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


def fetch_monthly_value_ifany_for_iptu(cur_refmonth):
  m = cur_refmonth.month
  if m < 3:
    return None, None
  seq = m - 2
  iptuvalue = Decimal(500)
  iptudescr = f"imposto predial {seq} de 10"
  return iptuvalue, iptudescr


def fetch_monthly_value_ifany_for_cond(cur_refmonth):
  """
  TODO this function must pick up condvalue from a database or raise IOError
  return condpkpg.fetch_monthly_value_for_cond(self.immeub_cond, cur_refmonth)

  r_int = random.randint(-100, 100)
  """
  r_int = 50  # now removing the random, knowing that it was for tests and
  condvalue = Decimal(1200 + r_int)
  conddescr = "tarifa no mês ref"
  return condvalue, conddescr


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
  reajuste_dt: datetime.date
  reajuste_idx: Decimal
  valuebefore: Decimal
  reajuste_sigla: str = 'IGP-M'

  @property
  def reajuste_rm(self) -> datetime.date:
    """ reajuste refmonth derived from reajuste date"""
    if self.reajuste_dt.day == 1:
      # refmonth is, by convention, a date on day 1
      return self.reajuste_dt
    y, m = self.reajuste_dt.year, self.reajuste_dt.month
    refmonth = datetime.date(year=y, month=m, day=1)
    return refmonth

  @property
  def valueafter(self) -> Decimal:
    """ it's valuebefore increased by reajuste index (@see the "montant" expression below)"""
    if self.reajuste_idx < DECIMAL_ZERO:
      # valueafter, by convention, cannot be less than valuebefore
      return self.valuebefore
    # the "montant" expression -> mf = mi * (1 + i)
    va = self.valuebefore * (1 + self.reajuste_idx)
    return va

  def raise_if_reajuste_has_inconsistent_date(self, upperlimitdate:datetime.date):
    """ raises ValueError on two conditions: 1 date in the future 2 date after contract's end-date"""
    upperlimitdate = dtfs.make_date_or_raise(upperlimitdate)
    today = datetime.date.today()
    if self.reajuste_rm > today:
      errmsg = f"reajuste refmonth [{self.reajuste_rm}] cannot be later than today [{today}]."
      raise ValueError(errmsg)
    if self.reajuste_rm > upperlimitdate:
      errmsg = f"reajuste refmonth [{self.reajuste_rm}] cannot be later than contract's final date [{upperlimitdate}]."
      raise ValueError(errmsg)


class PydtcRentContract(pydantic.BaseModel):
  """

  # imm_nickname: str = 'CDouto'
  """
  location: immeub.PydtcImmeuble
  inidate: datetime.date
  ori_rentvalue: typing.Annotated[Decimal, pydantic.Field(max_digits=12, decimal_places=4)]
  nmonths_duration: int
  has_proptax: bool
  # List of references (Many-to-Many / One-to-Many)
  # tenants: list[Person] = field(default_factory=list)
  tenants: List[pers.PydtcPerson] = pydantic.dataclasses.Field(default=[])
  fiadores: List[pers.PydtcPerson] = pydantic.dataclasses.Field(default_factory=lambda: [])
  nmonths_duration: int = 30
  has_proptax: bool = True
  has_incendtarif: bool = True
  has_condtarif: bool = True
  currency3letter: str = 'BRL'
  reajustes: list[Reajuste] = pydantic.dataclasses.Field(default_factory=lambda: [])
  monthly_fix_ir_dec: Decimal = pydantic.dataclasses.Field(default_factory=lambda: DEFAULT_MONTHLY_FIX_IR_DEC)
  _cur_rentvalue: Decimal = pydantic.PrivateAttr(default_factory=lambda: None)
  _contrnumber: str = pydantic.PrivateAttr(default_factory=lambda: None)

  @staticmethod
  def get_retrodate_ifinmora(refmonth: datetime.date) -> datetime.date:
    """
    retrodate is refmonth itself
    (this rule is not configurable as it seems stable in practice)

    Explaination:
    =============

    When 'in mora', the mora days count is not from duedate (generally 10),
      but from the beginning of the month;
    """
    refmonth = rmfs.make_refmonth_or_raise(refmonth)
    return refmonth

  @staticmethod
  def get_postdate_ifinmora(refmonth: datetime.date) -> datetime.date:
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
    _, ndays_inmonth = calendar.monthrange(refmonth.year, refmonth.month)
    year, month, day = refmonth.year, refmonth.month, ndays_inmonth
    lastdate_inmonth = datetime.date(year=year, month=month, day=day)
    return lastdate_inmonth

  def make_n_get_mininum_billingitems(
      self, p_refmonth: datetime.date | str | None = None
    ) -> list[bipydtc.PydtcBillingItem]:
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
    cur_refmonth = rmfs.make_current_refmonth() \
        if p_refmonth is None \
        else rmfs.make_refmonth_or_raise(p_refmonth)
    billingitems = []
    bi_seq = 1
    bi = bipydtc.PydtcBillingItem(
      seq=bi_seq,
      descr="Aluguel mensal",
      refmonth=cur_refmonth,
      value=self.cur_rentvalue,
    )
    billingitems.append(bi)
    if self.has_proptax:
      value, descr = fetch_monthly_value_ifany_for_iptu(cur_refmonth)
      if value:
        bi_seq += 1
        bi = bipydtc.PydtcBillingItem(
          seq=bi_seq,
          descr=f"IPTU ({descr})",
          refmonth=cur_refmonth,
          value=value,
        )
        billingitems.append(bi)
    if self.has_condtarif:
      value, descr = fetch_monthly_value_ifany_for_cond(cur_refmonth)
      if value:
        bi_seq += 1
        bi = bipydtc.PydtcBillingItem(
          seq=bi_seq,
          descr=f"Condomínio ({descr})",
          refmonth=cur_refmonth,
          value=value,
        )
        billingitems.append(bi)
    incendtarif, incend_descr = self.get_incendtarif_n_descr_if_available()
    if self.has_incendtarif and incendtarif is not None:
      value, descr = incendtarif, incend_descr
      if value:
        bi_seq += 1
        bi = bipydtc.PydtcBillingItem(
          seq=bi_seq,
          descr=f"Funesbom ({descr})",
          refmonth=cur_refmonth,
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
  def contrnumber(self) -> str:
    if self._contrnumber is not None:
      return self._contrnumber
    strdate = self.inidate.strftime('%Y%m')
    self._contrnumber = f"{self.imm_nickname}{strdate}"
    return self._contrnumber

  # @property
  # def imm_nickname(self) -> str:
  #   return self.location.imm_nickname

  def add_reajuste_w_dt_n_idx(self, reajuste_dt: datetime.date | str, reajuste_idx: Decimal, reajuste_sigla: str = 'IGP-M'):
    reajuste_dt = dtfs.make_date_or_raise(reajuste_dt)
    reajuste = Reajuste(
      reajuste_dt=reajuste_dt, reajuste_idx=reajuste_idx, valuebefore=self.cur_rentvalue, reajuste_sigla=reajuste_sigla
    )    # reajuste.raise_if_inconsistent_to_today_n_contractsend(self.findate)
    # reajuste.calc_n_set_cur_rentvalue()
    self.reajustes.append(reajuste)
    self.calc_n_set_cur_rentvalue()

  def calc_n_set_cur_rentvalue(self):
    if len(self.reajustes) == 0:
      self._cur_rentvalue = self.ori_rentvalue
      return
    self.reajustes.sort(key = lambda obj: obj.reajuste_dt)
    last_reajuste = self.reajustes[-1]
    self._cur_rentvalue = last_reajuste.valueafter

  def make_triplelist_date_reajuste_newrentvalue(self):
    # first triple has 0.0 reajuste
    triple = self.inidate, DECIMAL_ZERO, self.ori_rentvalue
    date_reajuste_newrentvalue_triplelist = [triple]
    for reajuste in self.reajustes:
      triple = reajuste.reajuste_rm, reajuste.reajuste_idx, reajuste.valueafter
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
    ostr = ""
    if len(self.fiadores) > 0:
      for fiador in self.fiadores:
        ostr += fiador.nomecompleto + ", "
      ostr = ostr.rstrip(", ")
      return ostr
    return 'n/a'

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
    The rule is one month later up to day 10
      (at this version, it's hardcorded in constant PAYMENT_DUE_DAY_IN_MONTH)
    """
    # 'remake' refmonth to make sure it's a date on day 1
    rm = p_refmonth
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    deltadays = self.get_payment_dueday_in_month() - 1
    duedate = refmonth + relativedelta(months=1, days=deltadays)
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
  persons = mngfetch.get_persons_by_cpfs([])
  if persons is None or len(persons) == 0:
    print('No persons found. Returning.')
    return
  person = persons[0]
  print('person =', person)
  location = immeub.get_immeuble_ex()
  rentvalue = Decimal(1000)
  rent = PydtcRentContract(
    location=location,
    inidate=dtfs.make_date_or_raise("2024-1-1"),
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
  bitems = rent.make_n_get_mininum_billingitems()
  print(bitems)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
