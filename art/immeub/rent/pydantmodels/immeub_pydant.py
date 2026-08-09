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
from dinero import Decimal
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
from typing import List
from beanie import Document, Link
import pydantic
import art.immeub.rent.pydantmodels.person_pydant as pers  # pers.Person
from pydantic import BaseModel, dataclasses
from pydantic.dataclasses import dataclass


class Immeuble(BaseModel):
  """
  class Immeuble(Document):
    beanie.Document inherits from pydantic.BaseModel
  """
  imm_nickname: str
  inscr_munic: str
  inscr_txincend: str = None
  cartorio_inscr: str = None
  address: list[str] = pydantic.dataclasses.Field(default_factory=lambda: [])
  owners:  list[pers.Person] = pydantic.dataclasses.Field(default_factory=lambda: [])
  phys_description: str = ""
  other_characts: str = ""

  class Settings:
    name = "immeubs_coll"


  def comma_sep_owner_names(self):
    ostr = ""
    for owner in self.owners:
      ostr += owner.fullname + ", "
    ostr = ostr.rstrip(", ")
    return ostr

  def __repr__(self):
    ostr = f"""{self.imm_nickname} | {self.inscr_munic} | {self.address}"""
    return ostr

  def address_as_str(self, spacing=""):
    ostr = "\n"
    for line in self.address:
      ostr += f"{spacing}{line}\n"
    ostr = ostr.lstrip('\n').rstrip('\n')
    return ostr


  def __str__(self):
    ostr = f"{self.__class__.__name__} {self.imm_nickname} | inscr_munic={self.inscr_munic}"
    address = self.address_as_str(spacing="    ")
    ostr += f"\nProprietário(s): {self.comma_sep_owner_names()}"
    ostr += f"\nEndereço:\n{address}"
    return ostr


def get_immeuble_ex():
  person = pers.get_person_ex()
  immeuble = Immeuble(
    imm_nickname="CDouto",
    inscr_txincend="1234",
    inscr_munic="12345",
    address=["Rio street 67 apt 101", "20222-111 | Barra Central"],
    owners=[person],
  )
  # print(immeuble)
  return immeuble


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
  location = get_immeuble_ex()
  print(location)


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
