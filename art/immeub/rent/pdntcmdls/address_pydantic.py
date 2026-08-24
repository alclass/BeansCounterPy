"""
art/immeub/rent/pdntcmdls/address_pydantic.py

To import PydtcAddress elsewhere:
  import art.immeub.rent.pdntcmdls.address_pydantic as addr  # addr.PydtcAddress
"""
import json
from decimal import Decimal
from typing import Annotated, Optional
import datetime
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
from beanie import Document, Link
from pydantic import field_validator, EmailStr, BaseModel, StringConstraints  # Field
import pydantic
CPFTYPE = Annotated[str, StringConstraints(pattern=r"\d{11}")]
STREETNAMETYPE = Annotated[str, StringConstraints(max_length=80)]
ZIPCODETYPE = Annotated[str, StringConstraints(max_length=8)]
STREETNUMBERTYPE = ZIPCODETYPE


class PydtcAddress(BaseModel):
  """
  import art.immeub.rent.pdntcmdls.address_pydantic as addr  # addr.PydtcAddress
  """
  street: STREETNAMETYPE
  number: STREETNUMBERTYPE
  zipcode: ZIPCODETYPE
  complement: Optional[STREETNAMETYPE] = None
  neighborhood: Optional[STREETNAMETYPE] = None
  city: Optional[STREETNAMETYPE] = None
  state: Optional[str] = None
  country: Optional[str] = None
  refplace: Optional[STREETNAMETYPE] = None
  lat: Optional[Decimal] = None
  lon: Optional[Decimal] = None
  gmt_tz: Optional[int] = None

  @classmethod
  def instantiate_fr_jsondict(cls, jsondict):
    address = cls.model_validate(jsondict)
    return address

  @property
  def fmt_zipcode(self):
    _zc = self.zipcode
    adds_dots, adds_dash = False, False
    if _zc is not None:
      if len(_zc) > 4:
        adds_dots = True
        if len(_zc) > 7:
          adds_dash = True
    if adds_dots:
      _zc = _zc[:2] + '.' + _zc[2:]
    if adds_dash:
      _zc = _zc[:6] + '-' + _zc[6:]
    return _zc

  def __str__(self):
    """
    Address is composed of 3 lines
    A line has a 70-char size
    """
    lines = []
    complement = f", {self.complement:11}" if self.complement else ""
    line = f"{self.street}, {self.number:04}{complement}"
    lines.append(line)
    zipcode = ""
    if self.zipcode is not None:
      zipcode = f"{self.fmt_zipcode}"
    line = zipcode
    if self.neighborhood is not None:
      line += f" {self.neighborhood}"
    lines.append(line)
    line = ""
    if self.city is not None:
      line = f"{self.city}"
      if self.state is not None:
        line += f" {self.state}"
    if len(line) > 0:
      lines.append(line)
    trunktext = '\n'.join(lines)
    return trunktext


def make_example_address_1():
  """
  Example address
  """
  address = PydtcAddress(
    street="Rua Camilo Douto",
    number="123",
    zipcode='22333111',
  )
  return address


def adhoctest1():
  address1 = make_example_address_1()
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
  adhoctest1()
