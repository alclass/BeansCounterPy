#!/usr/bin/env python3
"""

import lib.datesetc.datefs as dtfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch
art.immeub.rent.pdntcmdls.cond_pydant as cond # cond.PydtcCondominium
"""
import datetime
from decimal import Decimal
import random
import typing
import pydantic
import art.immeub.rent.pdntcmdls.cond_pydant as cond # cond.PydtcCondominium
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch
from pydantic import BaseModel, computed_field, model_validator
import art.immeub.tribs.onproperties.embedded_taxes_on_immeuble_pydant as embed  # embed.EmbeddedImmeubleTax
DECIMAL_ZERO = Decimal("0")
IMMNICKNAMETYPE = typing.Annotated[str, pydantic.StringConstraints(max_length=6)]


def draw_random_condvalue():
  r_int = random.randint(-100, 100)
  condvalue = Decimal(1600 + r_int)
  return condvalue


def create_json_for_condtarifas(year, imm_nickname):
  json_lst = []
  for m in range(1, 13):
    refmonthstr = f"{year}-{m}"
    refmonth = rmfs.make_refmonth_or_raise(refmonthstr)
    value = draw_random_condvalue()
    cond_o = cond.PydtcCondominium(
      imm_nickname=imm_nickname, refmonth=refmonth, value=value
    )
    json_str = cond_o.to_json_str()
    json_lst.append(json_str)
  # for json_str in json_lst:
  #   print(json_str)
  text = ",".join(json_lst)
  print(text)


def adhoctest1():
  imm_nickname = "CDouto"
  create_json_for_condtarifas(year=2026, imm_nickname=imm_nickname)


def adhoctest2():
  dbname, collname = 'immeub_db', 'condtarifas'
  dbfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  imm_nickname = "CDouto"
  refmonth = rmfs.make_refmonth_or_raise('2026-1')
  querydict = {
    "imm_nickname": imm_nickname,
    "refmonth": refmonth.strftime("%Y-%m-%d"),
  }
  print(querydict)
  dictdoc = dbfetcher.find_one_w_querydict_n_collname_as_dict(querydict)
  print(dictdoc)


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
