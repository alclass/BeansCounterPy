#!/usr/bin/env python3
"""
art/immeub/rent/pydantmodels/rentcontract_pydant.py
  Contains Pydantic class Contract.
  Contract is 'component' of the BillingCard app.
  (@see diagram context with BillignCard, BillingItem, Contract, Person, etc.).

# from dinero.currencies import BRL
"""
import pprint
from prettytable import PrettyTable
from dataclasses import dataclass, field   # , asdict
import datetime
from decimal import Decimal, ROUND_HALF_UP
import dinero
from dateutil.relativedelta import relativedelta
from dinero import Decimal
from dinero.currencies import BRL
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
from typing import List
from beanie import Document, Link
import pydantic
import typing
from pydantic import BaseModel
import art.immeub.rent.pydantmodels.immeub_pydant as immeub  # immueb.Immeuble
import art.immeub.rent.pydantmodels.person_pydant as pers  # pers.Person
import art.immeub.rent.pydantmodels as init
import lib.datesetc.datefs as dtfs
from tabulate import tabulate
DEFAULT_3LETTER_CURRENCY = init.DEFAULT_3LETTER_CURRENCY


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


class RentContract(pydantic.BaseModel):
  """

  # imm_nickname: str = 'CDouto'
  """
  location: immeub.Immeuble
  inidate: datetime.date
  ori_rentvalue: typing.Annotated[Decimal, pydantic.Field(max_digits=12, decimal_places=4)]
  nmonths_duration: int
  has_proptax: bool
  # List of references (Many-to-Many / One-to-Many)
  # tenants: list[Person] = field(default_factory=list)
  tenants: List[pers.Person] = pydantic.dataclasses.Field(default=[])
  fiadores: List[pers.Person] = pydantic.dataclasses.Field(default_factory=lambda: [])
  nmonths_duration: int = 30
  has_proptax: bool = True
  has_incendtarif: bool = True
  has_condtarif: bool = True
  currency3letter: str = 'BRL'
  date_n_reajuste_tuplelist: list[tuple[datetime.date, Decimal]] = pydantic.dataclasses.Field(default_factory=lambda: [])
  _cur_rentvalue: Decimal = pydantic.PrivateAttr(default_factory=lambda: None)
  _contrnumber: str = pydantic.PrivateAttr(default_factory=lambda: None)

  # @property
  # def imm_nickname(self) -> str:
  #   return self.location.imm_nickname

  def raise_if_inconsistent_reajuste_date(self, pdate:datetime.date):
    indate = pdate
    today = datetime.date.today()
    if indate > today:
      errmsg = f"reajuste date [{indate}] cannot be later than today [{today}]."
      raise ValueError(errmsg)
    if indate > self.findate:
      errmsg = f"reajuste date [{indate}] cannot be later than contract's final date [{self.findate}]."
      raise ValueError(errmsg)

  def add_date_n_reajusteindice(self, pdate: datetime.date | str, reajusteindice: Decimal):
    indate = dtfs.make_date_or_raise(pdate)
    self.raise_if_inconsistent_reajuste_date(indate)
    inreajusteindice = Decimal(reajusteindice)
    self.date_n_reajuste_tuplelist.append((indate, inreajusteindice))
    self.calc_n_set_cur_rentvalue()

  def calc_n_set_cur_rentvalue(self):
    if len(self.date_n_reajuste_tuplelist) == 0:
      self._cur_rentvalue = self.ori_rentvalue
    self.date_n_reajuste_tuplelist.sort(key = lambda tupl: tupl[0])
    indices = [tupl[1] for tupl in self.date_n_reajuste_tuplelist]
    inimontant = self.ori_rentvalue
    self._cur_rentvalue = calc_finmontant_w_inimontant_n_periodic_indices(inimontant, indices)

  @property
  def contrnumber(self) -> str:
    if self._contrnumber is not None:
      return self._contrnumber
    strdate = self.inidate.strftime('%Y%m%d')
    self._contrnumber = f"{self.imm_nickname}{strdate}"
    return self._contrnumber

  def dates_n_rentvalues_n_reajustes(self):
    # first
    triple = self.inidate, self.ori_rentvalue, Decimal('0.0')
    _dates_n_rentvalues_n_reajustes = [triple]
    inimontant = self.ori_rentvalue
    for date_n_reajuste in self.date_n_reajuste_tuplelist:
      pdate, reajuste = date_n_reajuste
      finmontant = inimontant * (1 + reajuste)
      triple = (pdate, finmontant, reajuste)
      _dates_n_rentvalues_n_reajustes.append(triple)
      inimontant = finmontant
    return _dates_n_rentvalues_n_reajustes

  def form_dates_n_rentvalues_n_reajustes(self):
    str_dates_n_rentvalues_n_reajustes = []
    for triple in self.dates_n_rentvalues_n_reajustes():
      pdate, rentvalue, reajuste = triple
      strdate = pdate.strftime('%d/%m/%Y')
      fmt_value = f"{rentvalue:.02f}"
      reaj_pct = reajuste * 100
      fmt_reaj_pct = f"{reaj_pct:.02f}%"
      line = strdate, fmt_value, fmt_reaj_pct
      str_dates_n_rentvalues_n_reajustes.append(line)
    return str_dates_n_rentvalues_n_reajustes

  def tabulate_dates_n_rentvalues(self):
    str_dates_n_rentvalues_n_reajustes = self.form_dates_n_rentvalues_n_reajustes()
    # Print the formatted table
    valor_col_title = f"valor em {self.get_currency_symbol()}"
    headers = ["data", valor_col_title, "reajuste %"]
    print(tabulate(str_dates_n_rentvalues_n_reajustes, headers=headers, tablefmt="grid"))

  def pprint_dates_n_rentvalues(self):
    str_dates_n_rentvalues_n_reajustes = self.form_dates_n_rentvalues_n_reajustes()
    table = PrettyTable()
    valor_col_title = f"valor em {self.get_currency_symbol()}"
    headers = ["data", valor_col_title, "reajuste %"]
    table.field_names = headers
    [table.add_row(r) for r in str_dates_n_rentvalues_n_reajustes]
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
        ostr += tenant.fullname + ", "
      ostr = ostr.rstrip(", ")
      return ostr
    return 'n/a'

  def commasep_fiadores(self):
    ostr = ""
    if len(self.fiadores) > 0:
      for fiador in self.fiadores:
        ostr += fiador.fullname + ", "
      ostr = ostr.rstrip(", ")
      return ostr
    return 'n/a'

  @property
  def din_currency_dict(self) -> dinero.types.Currency:
    dincurrencydict = getattr(dinero.currencies, self.currency3letter)
    return dincurrencydict

  def make_din_fr_dec(self, dec) -> Decimal:
    dec.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    din = Decimal(dec, self.din_currency_dict)
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
    action = 'CALCULATE_INTEREST_RATE_W_FIX_N_VAR_IDS'
    actions.append(action)
    return actions

  @property
  def findate(self) -> datetime.date:
    _findate = self.inidate + relativedelta(months=self.nmonths_duration) - relativedelta(days=1)
    return _findate

  # def __repr__(self):
  #   ostr = f"""Contract: {self.imm_nickname} | from={self.inidate} | to={self.findate}"""
  #   return ostr

  def get_currency_symbol(self):
    din = self.make_din_fr_dec(self.ori_rentvalue)
    return din.currency['symbol']

  def fmt_din(self, dec):
    din = self.make_din_fr_dec(dec)
    fmt_din = f"{din.currency['symbol']} {din.raw_amount:.02f}"
    return fmt_din

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
    reajustes={self.date_n_reajuste_tuplelist}
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
  person = pers.get_person_ex()
  location = immeub.get_immeuble_ex()
  rentvalue = Decimal(1000)
  rent = RentContract(
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
  rent.add_date_n_reajusteindice('2025-1-1', Decimal('0.035'))
  rent.add_date_n_reajusteindice('2026-1-1', Decimal('0.027'))
  print(rent)
  rent.tabulate_dates_n_rentvalues()
  rent.pprint_dates_n_rentvalues()


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
