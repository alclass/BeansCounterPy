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
from pydantic import BaseModel, computed_field, model_validator
import art.immeub.tribs.onproperties.embedded_taxes_on_immeuble_pydant as embed  # embed.EmbeddedImmeubleTax
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

  def to_json_str(self, indent: int = 2, is_for_db: bool = False):
    """
    """

    jsondump = self.model_dump_json(indent=indent)
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
  adhoctest2()
