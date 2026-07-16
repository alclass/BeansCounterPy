#!/usr/bin/env python3
"""
art/immeub/rent/models/contract_molder.py
  This class is the molding for the creation of a rent billing card

# from dinero.currencies import BRL
"""
from dataclasses import dataclass, field   # , asdict
import datetime
from dateutil.relativedelta import relativedelta
from dinero import Dinero
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
from typing import List
from beanie import Document, Link


@dataclass
class Person(Document):
  fullname: str
  cpf: str
  phonenumber: str
  email: str
  email_alt: str = None
  phonenumber_alt: str = None
  docid: str = None
  docid_alt: str = None
  profession: str = None
  birth_date: datetime.date = None
  address: list[str] = field(default_factory=list)
  obs: list[str] = field(default_factory=list)

  @property
  def cpf_fmt(self):
    return cpfv.format_cpf(self.cpf, adds_dots=True)

  def __repr__(self):
    ostr = f"""{self.fullname} | {self.cpf_fmt} | {self.phonenumber} | {self.email}"""
    return ostr


@dataclass
class Immeub(Document):
  imm_nickname: str
  inscr_munic: str
  inscr_txincend: str
  address: list[str] = field(default_factory=list)
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
