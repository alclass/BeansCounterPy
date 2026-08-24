#!/usr/bin/env python3
"""
art/immeub/rent/pdntcmdls/person_pydant.py
  Contains Beanie/Pydantic class Person.
  (@see diagram context with BillignCard, BillingItem, Contract, Person, etc.).

Recipe when needing annotated BeforeValidator
=============================================

# 1. Define the transformation function
def parse_custom_date(value: Any) -> date:
    if isinstance(value, str):
        # Change "%d/%m/%Y" to match your specific incoming string format
        return datetime.strptime(value, "%d/%m/%Y").date()
    return value

# 2. Create a reusable custom type alias
CustomDate = Annotated[date, BeforeValidator(parse_custom_date)]
"""
import json
from typing import Annotated, Optional
import datetime
import art.immeub.rent.pdntcmdls.address_pydantic as addr  # addr.PydtcAddress
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch  # mngfetch.get_rentcontract_by_number
from beanie import Document, Link
from pydantic import field_validator, EmailStr, BaseModel, StringConstraints  # Field
import pydantic
CPFTYPE = Annotated[str, StringConstraints(pattern=r"\d{11}")]


def get_persons_by_cpfs(cpfs: list[str]):
  persondocs = mngfetch.get_persons_by_cpfs(cpfs)
  persons = []
  for persondoc in persondocs:
    person = PydtcPerson.instantiate_from_json(persondoc)
    persons.append(person)
  return persons


class PydtcPerson(BaseModel):
  """
  Models a person (tenants, owners, guarantors, etc.) to the app.

  To import it:
  import art.immeub.rent.pdntcmdls.PydtcPerson as pers  # pers.PydtcPerson(...)
  """
  nomecompleto: str
  cpf: CPFTYPE
  emails: list[pydantic.EmailStr] = pydantic.dataclasses.Field(default_factory=lambda: [])
  phonenumbers: Optional[list[str]] = []
  address: addr.PydtcAddress = pydantic.dataclasses.Field(default_factory=lambda: None)
  obs: list[str] = pydantic.dataclasses.Field(default_factory=lambda: [])
  birthdate: Optional[datetime.date] = None
  birthcity: Optional[str] = None
  marital_st: Optional[str] = None
  profession: Optional[str] = None
  docum_id: Optional[str] = None
  docum_id_alt: Optional[str] = None

  @field_validator('cpf', mode='after')
  @classmethod
  def verify_cpf(cls, value: str) -> str:
    # Pydantic has already guaranteed that 'value' is a string
    cpfv.raise_ve_if_inconsistent_11char_cpf(value)
    return value

  def get_fmt_cpf(self, adds_dots: bool = True) -> str:
    return cpfv.format_cpf(self.cpf, adds_dots)

  @property
  def cpf_fmt_w_dots(self) -> str:
    return self.get_fmt_cpf(adds_dots=True)

  @classmethod
  def instantiate_from_jsondict(cls, pdict: dict):
    person = cls.model_validate(pdict)
    return person

  @classmethod
  def instantiate_from_json(cls, jsondump: str):
    pdict = json.loads(jsondump)
    return cls.instantiate_from_jsondict(pdict)

  @property
  def firstname(self):
    try:
      _firstname = self.nomecompleto.split(' ')[0]
    except (AttributeError, IndexError):
      _firstname = 'n/a'
    return _firstname

  @property
  def lastname(self):
    _lastname = 'n/a'
    try:
      pp = self.nomecompleto.split(' ')
      if len(pp) > 1:
        _lastname = pp[-1]
        return _lastname
    except AttributeError:
      pass
    return _lastname

  def get_first_n_last_names(self):
    lastname = self.nomecompleto.split()[-1]
    firstname_lastname = f"{self.firstname} {self.lastname}"
    return firstname_lastname

  def get_first_last_names_n_fmt_cpf(self):
    _nome_n_cpf = f"{self.get_first_n_last_names()} | CPF {self.cpf_fmt_w_dots}"
    return _nome_n_cpf

  def __repr__(self):
    ostr = f"""{self.nomecompleto} | {self.cpf_fmt_w_dots} | {self.phonenumber} | {self.email}"""
    return ostr

  def __str__(self):
    ostr = f"""{self.__class__.__name__} "{self.firstname} {self.lastname}"
    cpf={self.cpf_fmt_w_dots} | emails ={self.emails} | phones={self.phonenumbers}"""
    return ostr


class PersonDoc(PydtcPerson, Document):
  class Settings:
    name = "persons"


def make_address_1():
  address_1 = addr.PydtcAddress(
    street="Rua Camilo Douto",
    number="123",
    complement="apt 101",
    zipcode="20222333",
    city="Niterói",
    state="RJ",
  )
  return address_1


def adhoctest1():
  """
  """

  person = PydtcPerson(
    nomecompleto="John Doe",
    cpf="12345678909",
    phonenumbers=["99991111"],
    emails=["johndoe@example.com"],
    docum_id="1234567",

  )
  print(person)


def adhoctest2():
  address1 = make_address_1()
  print('address1', address1)
  print(address1)


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
