#!/usr/bin/env python3
"""
art/immeub/rent/models/fatura_etal_models.py

fatura fields:
  header:
    name
    address:
      address 1
      address 2
    email
    telephone

  fatura_card:
    current:
      aluguel
      condominium
      property tribute
    mora_if_any:
      tipo | aluguel-ou-encargos-em-mora | ref r1 | fator de base | valor
      tipo | aluguel-ou-encargos-em-mora | ref r2 | fator de base | valor
      tipo | aluguel-ou-encargos-em-mora | ref rN | fator de base | valor

import calendar
import copy
import json
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonths_mod as refmonth_fs.py  # refmonth_fs.py.fillin_refmonths_fr_ndayslist
import lib.finfs.indices.indices_fetch_n_fs as cmfs  # refmonth_fs.py.fillin_refmonths_fr_ndayslist
from lib import texts
"""
import datetime
from dateutil import relativedelta
from dinero import Dinero
from dinero.currencies import BRL
from dataclasses import dataclass  # , field, asdict
from typing import List
from beanie import Document, Link
import art.immeub.rent.bill as init  # refmonth_fs.py.fillin_refmonths_fr_ndayslist
import lib.datesetc.refmonth_fs as rmfs
import lib.datesetc.datefs as dtfs
import lib.texts.textfs as txtfs
from art.immeub.rent.models.contract_molder import Immeub, Person, RentContract
DEFAULT_FIX_IR_PCT = init.DEFAULT_FIX_IR_PCT  # this is percentual
DEFAULT_FIX_IR_DEC = DEFAULT_FIX_IR_PCT / 100  # this is decimal


def json_date_serial(obj):
    """JSON serializer for objects not serializable by default JSON code"""
    if isinstance(obj, datetime.date):
        return dtfs.date_to_str_4y_dash_2m_dash_2d(obj)
    if isinstance(obj, Dinero):
      strval = f"{obj.raw_amount:.2f}"
      return strval
    raise TypeError(f"Type {type(obj)} not serializable")


@dataclass
class FaturaLine(Document):
  tipo: str
  description: str
  refmonth: datetime.date
  explain: str
  cred_or_debt: str
  value: Dinero = None


@dataclass
class IncendTax:
  incend_inscr: str
  uf_statesigla: str
  immeub_address: list[str]
  refmonth: datetime.date = None  # has context of duemonth i.e., month of payment (or M+1 if in convention)
  description: str = "taxa de incêndio estadual"
  yearly_value: Dinero = None
  refyear: int = None
  incendtax_url: str = None

  def generate_faturaline(self):
    """
    """
    if self.refyear is None:
      today = datetime.date.today()
      self.refyear = today.year - 1
    faturaline = FaturaLine(
      tipo='AE',
      description=self.description,
      refmonth=self.refmonth,
      explain=f"tx FUNESBOM anual ref {self.refyear}",
      cred_or_debt="D",
      value=self.yearly_value,
    )
    return faturaline


@dataclass
class PropTrib:
  munic_inscr: str
  cityname: str
  immeub_address: list[str]
  refmonth: datetime.date
  yearonepay: Dinero = None
  monthlypay: Dinero = None
  parcels_ifmonthly: int = 10
  inimonth_ifmonthly: int = 2
  finmonth_ifmonthly: int = 11
  _n_parcel: int = None
  description: str = 'IPTU imposto predial'

  @property
  def default_explain(self):
    def_exp = "no prazo ref "
    letter3month = rmfs.get_3letter_extmes(self.refmonth.month)
    def_exp += f"{letter3month}/{self.refmonth.year}"
    return def_exp

  def get_value_by_context(self):
    if self.yearonepay is not None:
      return self.yearonepay
    if not isinstance(self.monthlypay, Dinero):
      errmsg = f"monthlypay ({self.monthlypay}) is not type Dinero. Cannot continue."
      raise ValueError(errmsg)
    return self.monthlypay

  def generate_faturaline(self):
    """
    tipo: str
    description: str
    refmonth: datetime.date
    explain: str
    cred_or_debt: str
    value: Dinero = None
    """
    value = self.get_value_by_context()  # or Dinero("0.0", BRL)
    faturaline = FaturaLine(
      tipo='AE',
      description=self.description,
      refmonth=self.refmonth,
      explain=self.default_explain,
      cred_or_debt="D",
      value=value,
    )
    return faturaline

  def set_parcel_by_refmonth(self):
    try:
      self.n_parcel = self.refmonth.month - 1
    except AttributeError:
      pass

  @property
  def n_parcel(self):
    if self.n_parcel is None:
      self.set_parcel_by_refmonth()
    return self.n_parcel

  @n_parcel.setter
  def n_parcel(self, n_parcel):
    n_parcel = int(n_parcel)
    self._n_parcel = n_parcel


@dataclass
class CondTarif:
  condname: str
  immeub_address: list[str]
  refmonth: datetime.date
  tarifvalue: Dinero = None
  espelho_pdf_url: str = None

  def generate_faturaline(self):
    """
    """
    faturaline = FaturaLine(
      tipo='AE',
      description=f"condomium {self.condname}",
      refmonth=self.refmonth,
      explain="tarifa mensal M-1 (cf espelho pdf)",
      cred_or_debt="D",
      value=self.tarifvalue,
    )
    return faturaline


@dataclass
class ImmeubFaturaBaseMold(Document):
  """
  This class is an idea for a possible Contrat.generate() method that may fill in the attributes below
  """
  aluguel: Dinero
  condominium: Dinero
  proptrib: Link[PropTrib]
  # proptrib: PropTrib = None
  incendtax: Link[IncendTax]
  # incendtax: IncendTax = None


@dataclass
class FaturaCard(Document):
  """

  main_tenant
    address: list[str]
    email: str
    telephone: str


  """
  # header
  refmonth: datetime.date
  rentcontract: Link[RentContract]
  immeub: Link[Immeub]  # gets it from contract
  main_landlord: Link[Person]  # gets it from contract
  imobiliaria_ifany: Link[Person]  # gets it from contract
  items: List[Link[FaturaLine]]
  # items: list[FaturaLine] = field(default_factory=list)
  unique_fat_id: str = None  # @see method that forms it
  fat_ready_ts: datetime.datetime = None  # timestamp when it's marked ready in system (at end of month)
  fat_launchdate: datetime.date = None  # when it goes to payor (at end of month)
  rev_letter: str = 'a'  # revision letter (b, c...)  if fatura is ammended a posteriori
  duedate: datetime.date = None  # gets it from contract
  total_a_pagar: Dinero = None  # computed by method calculate()
  boleta_url_ifavail: str = None  # in case of a more formal billing-doc then the Pix-address above


  @property
  def iimmeub(self) -> str:
    return self.immeub

  @property
  def immeub_nn(self) -> str:
    return self.immeub.immeub_nn

  @property
  def endr_pix_a_pagar(self) -> str:

  @property
  def endr_pix_a_pagar(self) -> str:
    return self.main_landlord.endr_pix_a_pagar

  def set_duedate_by_refmonth(self):
    """
    To get duedate one adds one month to refmonth date and adjust its day to 10
      (in case the contract defines a different one, the user may enter it normally during instantiation)
    """
    self.duedate = self.refmonth + relativedelta.relativedelta(months=1)
    self.duedate = datetime.date(year=self.duedate.year, month=self.duedate.month, day=10)

  def set_unique_fat_id(self):
    if self.refmonth is None or self.immeub_nn is None:
      # return '<a calcular>'
      return
    strdate = f"{self.refmonth.year}{self.refmonth.month:02}"
    nickupper = self.immeub_nn.upper()
    self.unique_fat_id = f"{nickupper}{strdate}{self.rev_letter}"
    return

  def calculate(self):
    if self.unique_fat_id is None:
      self.set_unique_fat_id()
    if self.duedate is None:
      self.set_duedate_by_refmonth()
    _total = Dinero("0.0", BRL)
    for item in self.items:
      cred_or_debt = item.cred_or_debt
      if cred_or_debt == 'D':
        _total += item.value
      elif cred_or_debt == 'C':
        _total -= item.value
    self.total_a_pagar = _total

  def close_for_emission(self):
    """
    step 1 - increase rev_letter if a timestamp already exists
    step 2 - (regex)set timestamp fat_ready_ts
    step 3 - freeze it (have to know how) (or make read-only) in MongoDB
    step 4 - schedule email-sending or webpage appearance (this is based on 'launchdate')
    """
    if self.rev_letter == 'a':
      self.rev_letter = txtfs.increase_one_to_letter(self.rev_letter)
    self.set_unique_fat_id()  # to reflect the rev_letter increase
    self.fat_ready_ts = datetime.datetime.now()
    # store to MongoDB and freeze it
    self.fat_launchdate = datetime.date.today()  # available when 'closing for emission', caller may reset it


def adhoctest1():
  pass


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
