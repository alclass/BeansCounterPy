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
from dinero import Dinero
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
from typing import List
from beanie import Document, Link
from pydantic import BaseModel, field_validator, EmailStr


class Person(BaseModel):
  fullname: str
  cpf: str
  phonenumber: str
  email: EmailStr
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


  def __repr__(self):
    ostr = f"""{self.fullname} | {self.cpf_fmt} | {self.phonenumber} | {self.email}"""
    return ostr

  def __str__(self):
    ostr = f"""{self.__class__.__name__}
    fullname = {self.fullname} | cpf={self.cpf_fmt}
    phone={self.phonenumber} | {self.email}"""
    return ostr


def adhoctest1():
  person = Person(
    fullname="John Doe",
    cpf="12345678909",
    phonenumber="99991111",
    email="johndoe@@example.com",
    docid="1234567",
  )
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
