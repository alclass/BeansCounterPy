#!/usr/bin/env python3
"""
art/immeub/rent/pdntcmdls/immeub_pydant.py
  Contains Beanie/Pydantic class Immeuble.
  (@see diagram context with BillignCard, BillingItem, Contract, Person, etc.).

# from dinero.currencies import BRL
To import this module:
  art.immeub.rent.pdntcmdls.cond_pydant as cond # cond.PydtcCondominium
import lib.datesetc.datefs as dtfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch
"""
import datetime
from decimal import Decimal
import typing
import pydantic
from pydantic import BaseModel  # , computed_field, model_validator
DECIMAL_ZERO = Decimal("0")
IMMNICKNAMETYPE = typing.Annotated[str, pydantic.StringConstraints(max_length=6)]


class PydtcCondominium(BaseModel):
  """
  class Immeuble(Document):
    beanie.Document inherits from pydantic.BaseModel
  """
  imm_nickname: IMMNICKNAMETYPE
  refmonth: datetime.date
  value: Decimal
  condname: typing.Optional[str] = None
  administradora: typing.Optional[str] = None

  def to_json_str(self, indent: int = 2, is_for_db: bool = False):
    """
    """
    excludeset = {}
    if is_for_db:
      # for the time being, excludeset = {'administradora'} is not needed
      # because exclude_none=True removes the None-value fields
      pass
    jsondump = self.model_dump_json(exclude=excludeset, exclude_none=True, indent=indent)
    return jsondump


def adhoctest1():
  """
  """
  pass


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
