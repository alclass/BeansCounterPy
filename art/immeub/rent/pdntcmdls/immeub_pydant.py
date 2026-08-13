#!/usr/bin/env python3
"""
art/immeub/rent/pdntcmdls/immeub_pydant.py
  Contains Beanie/Pydantic class Immeuble.
  (@see diagram context with BillignCard, BillingItem, Contract, Person, etc.).

# from dinero.currencies import BRL
"""
import datetime
from decimal import Decimal
import pydantic
import json
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.Person
from pydantic import BaseModel, computed_field, model_validator
import art.immeub.tribs.onproperties.embedded_taxes_on_immeuble as embed  # embed.EmbeddedImmeubleTax
DECIMAL_ZERO = Decimal("0")


def get_owners_by_cpfs(anyparam=None):
  person = pers.get_person_ex()
  owners = [person]
  return owners



def remove_none_values(data):
  """Recursively removes all None values from dicts and lists."""
  if isinstance(data, dict):
    return {k: remove_none_values(v) for k, v in data.items() if v is not None}
  elif isinstance(data, list):
    return [remove_none_values(v) for v in data if v is not None]
  return data


class PydtcImmeuble(BaseModel):
  """
  class Immeuble(Document):
    beanie.Document inherits from pydantic.BaseModel
  """
  imm_nickname: str
  inscr_munic: str
  inscr_txincend: str = None
  cartorio_inscr: str = None
  address: list[str] = pydantic.dataclasses.Field(default_factory=lambda: [])
  owners:  list[pers.PydtcPerson] = pydantic.dataclasses.Field(default_factory=lambda: [])
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
        owners = mng_rent.get_persons_by_cpfs(cpfs)
        data['owners'] = owners
    return data

  def asdict(self):
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


  @classmethod
  def instantiate_from_json(cls, jsondump):
    """
    The updated version
    """
    pdict = json.loads(jsondump)
    owners_cpfs = pdict.pop('owners_cpfs')
    owners = get_owners_by_cpfs(owners_cpfs)
    pdict['owners'] = owners
    cleaned_data = remove_none_values(pdict)
    obj = cls.model_validate(cleaned_data)
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
  person = pers.get_person_ex()
  immeuble = PydtcImmeuble(
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
