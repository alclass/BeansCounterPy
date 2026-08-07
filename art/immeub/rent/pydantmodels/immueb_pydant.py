#!/usr/bin/env python3
"""
art/immeub/rent/pydantmodels/immueb_pydant.py
  Contains Beanie/Pydantic class Immeuble.
  (@see diagram context with BillignCard, BillingItem, Contract, Person, etc.).

# from dinero.currencies import BRL
"""
from dataclasses import dataclass, field   # , asdict
import datetime
from dateutil.relativedelta import relativedelta
from dinero import Dinero
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
from typing import List
from beanie import Document, Link
from pydantic import BaseModel, dataclasses
from pydantic.dataclasses import dataclass


class Immeuble(Document):
  """
  beanie.Document inherits from pydantic.BaseModel
  """
  imm_nickname: str
  inscr_munic: str
  inscr_txincend: str
  address: list[str] = dataclasses.field(default_factory=lambda: [])
  phys_description: str = ""
  other_characts: str = ""

  class Settings:
    name = "immeubs_coll"

  def __repr__(self):
    ostr = f"""{self.imm_nickname} | {self.address}"""
    return ostr


@dataclass
class RentContract(Document):
  imm_nickname: str
  inidate: datetime.date
  cur_rentvalue: Dinero
  ori_rentvalue: Dinero

  location: Link[Immeub]
  # List of references (Many-to-Many / One-to-Many)
  tenants: List[Link[Person]]
  # tenants: list[Person] = field(default_factory=list)
  fiadores: List[Link[Person]]
  # fiadores: list[Person] = field(default_factory=list)
  landlords: List[Link[Person]]
  # landlords: list[Person] = field(default_factory=list)

  nmonths_duration: int = 30
  has_proptax: bool = True
  has_incendtarif: bool = True
  has_condtarif: bool = True

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
    _findate = self.inidate + relativedelta(months=self.nmonths_duration)
    return _findate

  def __repr__(self):
    ostr = f"""Contract: {self.imm_nickname} | from={self.inidate} | to={self.findate}"""
    return ostr

  def __str__(self):
    ostr = f"""{self.__class__.__name__}
    sigla/apelido={self.imm_nickname}
    inidate={self.inidate}
    cur_rentvalue={self.cur_rentvalue}
    ori_rentvalue={self.ori_rentvalue}
    nmonths_duration={self.nmonths_duration}
    has_proptax={self.has_proptax}
    has_incendtarif={self.has_incendtarif}
    has_condtarif={self.has_condtarif}
    tenants={self.tenants}
    fiadores={self.fiadores}
    landlords={self.landlords}
    
    """
    return ostr
