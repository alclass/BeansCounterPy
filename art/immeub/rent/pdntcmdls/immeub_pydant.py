#!/usr/bin/env python3
"""
art/immeub/rent/pdntcmdls/immeub_pydant.py
  Contains Beanie/Pydantic class Immeuble.
  (@see diagram context with BillignCard, BillingItem, Contract, Person, etc.).

# from dinero.currencies import BRL
"""
import datetime
from decimal import Decimal
import typing
from typing import Optional
import pydantic
from pydantic import BaseModel, computed_field, model_validator
import json
import lib.datesetc.datefs as dtfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.PydtcPerson
import art.immeub.rent.pdntcmdls.address_pydan as addr  # addr.PydtcAddress
import art.immeub.tribs.onproperties.embedded_taxes_on_immeuble_pydant as embed  # embed.EmbeddedImmeubleTax
DECIMAL_ZERO = Decimal("0")
IMMNICKNAMETYPE = typing.Annotated[str, pydantic.StringConstraints(max_length=6)]


def remove_none_values(data):
  """Recursively removes all None values from dicts and lists."""
  if isinstance(data, dict):
    return {k: remove_none_values(v) for k, v in data.items() if v is not None}
  elif isinstance(data, list):
    return [remove_none_values(v) for v in data if v is not None]
  return data


def get_immeuble_by_nickname(imm_nickname: str) -> "PydtcImmeuble":
  dbname, collname = 'immeub_db', 'immeubles'
  mngfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {'imm_nickname': imm_nickname}
  jsondict = mngfetcher.find_one_w_querydict_n_collname(querydict)
  location = PydtcImmeuble.instantiate_from_jsondict(jsondict)
  return location


class PydtcImmeuble(BaseModel):
  """
  class Immeuble(Document):
    beanie.Document inherits from pydantic.BaseModel
  """
  imm_nickname: IMMNICKNAMETYPE
  inscr_munic: str
  inscr_txincend: Optional[str] = None
  cartorio_inscr: Optional[str] = None
  address: addr.PydtcAddress = pydantic.dataclasses.Field(default_factory=lambda: None)
  owners:  Optional[list[pers.PydtcPerson]] = None
  phys_description: str = ""
  other_characts: str = ""
  tributos: list[embed.EmbeddedImmeubleTax] = pydantic.dataclasses.Field(default_factory=lambda: [])

  @model_validator(mode='before')
  @classmethod
  def populate_owners_from_cpfs(cls, data):
    """
    # 3. This AUTOMATICALLY runs every time you call model_validate()
    """
    if isinstance(data, dict):
      # Check if JSON contains the CPFs list but is missing full objects
      if 'owners_cpfs' in data and not data.get('owners'):
        cpfs = data.pop('owners_cpfs')  # Extract CPFs
        # Fetch full objects using your existing DB lookup function
        owners = pers.get_persons_by_cpfs(cpfs)
        data['owners'] = owners
    return data

  def get_contrnumber_w_inirefmonth(self, p_contr_inidate: datetime.date | str) -> str:
    contr_inidate = dtfs.make_date_or_raise(p_contr_inidate)
    refyyyymm = contr_inidate.strftime('%Y%m')
    contrnumber = f"{self.imm_nickname}{refyyyymm}"
    return contrnumber

  def as_json_str(self):
    """
    try:
      cpfs_owners = list(map(lambda o: o.cpf, self.owners))
      jsondict['cpfs_owners'] = cpfs_owners
    except IndexError:
      pass
    jsondump = json.dumps(jsondict, indent=2)
    """
    jsondump = self.model_dump_json(exclude={'owners'}, indent=2)
    return jsondump

  @computed_field
  @property
  def owners_cpfs(self) -> list[str]:
    return [p.cpf for p in self.owners]

  class Settings:
    name = "immeubles"

  class MongoImmeubRepr:
    pass

  def comma_sep_owner_names(self):
    ostr = ""
    for owner in self.owners:
      ostr += owner.nomecompleto + ", "
    ostr = ostr.rstrip(", ")
    return ostr

  def __repr__(self):
    ostr = f"""{self.imm_nickname} | {self.inscr_munic} | {self.address}"""
    return ostr

  def address_as_str(self, spacing=""):
    if self.address is not None:
      return str(self.address)
    return "n/a"

  def mk_line_this_year_taxes_registered(self):
    total_tribs = self.get_total_this_year_taxes()
    ostr = ""
    for tributo in self.tributos:
      ostr += f"\n{tributo}"
    ostr = ostr.lstrip('\n').rstrip('\n')
    ostr = "n/a" if ostr == "" else ostr
    if ostr != "n/a":
      ostr += f"\n\tTotal em tributos no ano: {total_tribs:.2f}"
    return ostr

  def get_total_this_year_taxes(self) -> Decimal:
    today = datetime.date.today()
    thisyear = today.year
    tributos_this_year = filter(lambda trib: trib.payment_year == thisyear, self.tributos)
    values = [trib.yeartotal for trib in tributos_this_year]
    total = Decimal(sum(values))
    return total

  def to_json(self, indent: int = 2) -> str:
    jsondumpstr = self.model_dump_json(exclude={'owners'}, indent=indent)
    return jsondumpstr

  @classmethod
  def instantiate_from_json_str(cls, json_str: str) -> "PydtcImmeuble":
    _ = json_str
    obj = cls.model_validate_json(json_str)
    return obj

  @classmethod
  def instantiate_from_jsondict(cls, jsondict: dict) -> "PydtcImmeuble":
    """
    The updated version
    pdict = json.loads(jsondict)

    owners_cpfs = jsondict.pop('owners_cpfs')
    owners = pers.get_persons_by_cpfs(owners_cpfs)
    jsondict['owners'] = owners
    jsondict = remove_none_values(jsondict)
    """
    obj = cls.model_validate(jsondict)
    return obj

  def __str__(self):
    lines_tributos = self.mk_line_this_year_taxes_registered()
    ostr = f"{self.__class__.__name__} {self.imm_nickname} | inscr_munic={self.inscr_munic}"
    address = self.address_as_str(spacing="    ")
    ostr += f"\nProprietário(s): {self.comma_sep_owner_names()}"
    ostr += f"\nEndereço:\n{address}"
    ostr += f"\nÚltimos tributos registrados: {lines_tributos}"
    return ostr


def get_immeuble_ex():
  persons = pers.get_persons_by_cpfs([])
  print(persons)
  if persons is None or len(persons) == 0:
    return None
  address = addr.PydtcAddress(
    street='Rua Carmo Douto',
    number="67",
    complement="apt 101",
    neighborhood="Barra Central",
    city="Rio de Janeiro",
    zipcode="22333111",
  )
  immeuble = PydtcImmeuble(
    imm_nickname="CDouto",
    inscr_txincend="1234",
    inscr_munic="12345",
    address=address,
    owners=persons,
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
  print('get_immeuble_ex()')
  location = get_immeuble_ex()
  print('location =>', location)
  iptu = embed.make_example_iptu_1()
  location.tributos.append(iptu)
  funesbom = embed.make_example_funesbom_1()
  location.tributos.append(funesbom)
  if location is not None:
    asdict = location.as_json_str()
    print(asdict)

def adhoctest2():
  imm_nickname = 'CDouto'
  print('imm_nickname', imm_nickname)
  location = get_immeuble_by_nickname(imm_nickname)
  print('location', location)


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
