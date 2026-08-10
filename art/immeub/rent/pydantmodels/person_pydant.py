#!/usr/bin/env python3
"""
art/immeub/rent/pydantmodels/person_pydant.py
  Contains Beanie/Pydantic class Person.
  (@see diagram context with BillignCard, BillingItem, Contract, Person, etc.).

# from dinero.currencies import BRL
"""
from dataclasses import dataclass, field   # , asdict
import datetime
from dateutil.relativedelta import relativedelta
import dinero
from decimal import Decimal
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
from typing import List
from beanie import Document, Link
from pydantic import field_validator, EmailStr, BaseModel  # Field
import pydantic


class PydtcPerson(BaseModel):
  """
  class Person(Document):

  """
  fullname: str
  cpf: str
  phonenumber: str
  email: pydantic.EmailStr
  email_alt: pydantic.EmailStr = None
  phonenumber_alt: str = None
  docid: str = None
  docid_alt: str = None
  profession: str = None
  birth_date: datetime.date = None
  address: list[str] = pydantic.dataclasses.Field(default_factory=lambda: [])
  obs: list[str] = pydantic.dataclasses.Field(default_factory=lambda: [])

  @property
  def cpf_fmt(self) -> str:
    return cpfv.format_cpf(self.cpf, adds_dots=True)

  def get_fmt_cpf(self) -> str:
    return self.cpf_fmt

  @field_validator('cpf')
  @classmethod
  def validate_cpf(cls, cpf: str) -> str:
    """
    Just to record. Via __post_init__() the cpf-validation did not work.
    """
    if cpfv.is_11char_cpf_valid(cpf):
      return cpf
    errmsg = f"CPF {cpf} invalid."
    raise ValueError(errmsg)

  @field_validator('email')
  @classmethod
  def validate_email(cls, email: str) -> str:
    return email

  def get_first_n_last_names(self):
    firstname = self.fullname.split()[0]
    lastname = self.fullname.split()[-1]
    firstname_lastname = f"{firstname} {lastname}"
    return firstname_lastname

  def get_first_last_names_n_fmt_cpf(self):
    _nome_n_cpf = f"{self.get_first_n_last_names()} | CPF {self.cpf_fmt}"
    return _nome_n_cpf

  def __repr__(self):
    ostr = f"""{self.fullname} | {self.cpf_fmt} | {self.phonenumber} | {self.email}"""
    return ostr

  def __str__(self):
    ostr = f"""{self.__class__.__name__}
    fullname = {self.fullname} | cpf={self.cpf_fmt}
    phone={self.phonenumber} | {self.email}"""
    return ostr


class PersonDoc(PydtcPerson, Document):
  class Settings:
    name = "persons"


def get_person_ex():
  person = PydtcPerson(
    fullname="John Doe",
    cpf="12345678909",
    phonenumber="99991111",
    email="johndoe@example.com",
    docid="1234567",
  )
  return person


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
  """
  person = get_person_ex()
  print(person)


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
