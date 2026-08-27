#!/usr/bin/env python3
"""
art/immeub/rent/billmodels/billingcard_pydantic.py

# from art.immeub.rent.pdntcmdls.schema_bizmodels import BillingCard
# locale.setlocale(locale.LC_NUMERIC, "pt_BR")  # "pt_BR.UTF-8"
"""
import art.immeub.rent.billmodels.billingcard_pydantic as bcards  # bcards.PydtcBillingCard
import lib.datesetc.refmonth_fs as rmfs
mkrm = rmfs.make_refmonth_or_raise
import art.immeub.rent.billmodels.billingitem_pydantic as bitem  # also bitem.PydtcPayment


def adhoctest1():
  """

  """
  billingitems = []
  billingitem = bitem.PydtcBillingItem(
    seq=1,
    description="aluguel",
    value=2000,
    mora_incr=0,
    itemtotal=1.2
  )
  billingitems.append(billingitem)
  refmonth = mkrm('2026-4')
  bcard = bcards.PydtcBillingCard(
    rentcontract='cdouto202401',
    refmonth=refmonth,
    billingitems=billingitems,
  )
  pass


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
