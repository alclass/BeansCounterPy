#!/usr/bin/env python3
"""
art/immeub/rent/testdata/billingcards_createdata.py

import datetime
import lib.datesetc.datefs as dtfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch
from decimal import Decimal
import lib.datesetc.refmonth_fs as rmfs
"""
import art.immeub.rent.create_adhoc_objects.prettytable_bitems as ppbitems  # ppbitems.PrettyTableForBI
import art.immeub.rent.billmodels.billingitem_pydantic as bitems  # bipydtc.PydtcBillingItem


def adhoctest1():
  bitems.make_4_billingitems()


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  process()
  adhoctest2()
  """
  adhoctest1()
