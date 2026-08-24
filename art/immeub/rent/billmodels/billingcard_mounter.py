#!/usr/bin/env python3
"""
art/immeub/rent/billmodels/billingcard_mounter.py
  Contains routines that make/mount a refmonth's billingcard.

from dinero.currencies import BRL  # USD, EUR
"""
import copy

import pydantic
from bson.decimal128 import Decimal128
from decimal import Decimal, ROUND_HALF_UP
import datetime
import lib.datesetc.datefs as dtfs # dfs.stringify_date
import lib.datesetc.refmonth_fs as rmfs # dfs.stringify_date
import lib.fncfs.dinerofs.dinserial_fs as dinfs # dfs.stringify_date
import art.immeub.rent.billmodels as init
import art.immeub.rent.billmodels.billingcard_pydantic as bcard  # bcard.PydtcBillingCard
DEFAULT_FIX_IR_PCT = init.DEFAULT_FIX_IR_PCT
DEFAULT_VAR_IR_PCT = init.DEFAULT_VAR_IR_PCT
stringify_date = dtfs.date_to_str_4y_dash_2m_dash_2d
dinero_serializer = dinfs.dinero_serializer


class Mounter(pydantic.BaseModel):
  billingcard: bcard.PydtcBillingCard




def adhoctest1():
  pass



def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
