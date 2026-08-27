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
import pydantic
from pydantic import field_validator, EmailStr, BaseModel, StringConstraints  # Field
import art.immeub.rent.pdntcmdls.address_pydant as addr  # addr.PydtcAddress
import lib.numberfs.cpf_verifica as ccpf  # cpfv.calcula_cpf_via_reduce
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch  # mngfetch.get_rentcontract_by_number
import art.immeub.rent.mdb.mongofs as mngfs  # .RentMongo
CPFTYPE = Annotated[str, StringConstraints(pattern=r"\d{11}")]


def fetch_persons_by_cpfs(cpfs: list[str]) -> list["PydtcPerson"]:
  persondocs = mngfetch.get_persons_by_cpfs_as_jsonstrlst(cpfs)
  persons = []
  for persondoc in persondocs:
    person = PydtcPerson.instantiate_fr_jsonstr(persondoc)
    persons.append(person)
  return persons


def fetch_person_by_cpf(cpf: str) -> "PydtcPerson | None":
  persons = fetch_persons_by_cpfs([cpf])
  if len(persons) > 0:
    return persons[0]
  return None


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
  address: Optional[addr.PydtcAddress] = None
  obs: list[str] = pydantic.dataclasses.Field(default_factory=lambda: [])
  chavepix: Optional[str] = None
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
    ccpf.raise_ve_if_inconsistent_11char_cpf(value)
    return value

  def get_fmt_cpf(self, adds_dots: bool = True) -> str:
    return ccpf.format_cpf(self.cpf, adds_dots)

  @property
  def cpf_fmt_w_dots(self) -> str:
    return self.get_fmt_cpf(adds_dots=True)


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

  def get_main_email(self) -> EmailStr | None:
    if len(self.emails) > 0:
      return self.emails[0]
    return None

  def to_json(self, indent: int = 2, is_for_db: bool = False) -> str:
    return self.model_dump_json(indent=indent)

  def to_jsondict(self, is_for_db: bool = False) -> str:
    return self.model_dump()

  @classmethod
  def instantiate_fr_jsonstr(cls, json_str) -> "PydtcPerson":
    """
    Useful to recreate an instance from MongoDB JSON doc.
    """
    obj = cls.model_validate_json(json_str)
    return obj

  @classmethod
  def instantiate_fr_jsondict(cls, json_dict: dict):
    _ = json_dict
    json_dict = mngfs.remove_none_values_fr_dict_recurs(json_dict)
    person = cls.model_validate(json_dict)
    return person

  def __repr__(self):
    main_email_addr = "n/a"
    fi_la_name = self.get_first_n_last_names()
    if len(self.emails) > 0:
      main_email_addr = self.emails[0]
    ostr = f"""{fi_la_name} | {self.cpf_fmt_w_dots} | {main_email_addr}"""
    return ostr

  def __str__(self):
    ostr = f"""{self.__class__.__name__}
    nome="{self.firstname} {self.lastname}" | cpf="{self.cpf_fmt_w_dots} | pix={self.chavepix}"
    emails={self.emails} | phones={self.phonenumbers}"""
    return ostr


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
  payee = make_example_person_123456781()
  print('payee', payee)
  json_str = payee.to_json()
  print('json_str', json_str)


def adhoctest3():
  dbname, collname = 'immeub_db', 'persons'
  dbfetch = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {'cpf': '12345678143'}
  docdict = dbfetch.find_one_w_querydict_n_collname_as_dict(querydict)
  print('docdict', docdict)
  if docdict is not None:
    person = PydtcPerson.instantiate_fr_jsondict(docdict)
    print('person', person)
  else:
    print('person docdict', docdict)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest3()
