#!/usr/bin/env python3
"""
art/immeubroutes/cdutra/rent/addon_mod.py

"""
import datetime
import art.immeub.rent.models.addon_mod as addonmod  # AddOnItem
import art.immeub.rent.adhocs.discontinued_mora_calc_month_n_list as mc  # mc.MonthRangeMoraMounter


def adhoctest1():
  addonmod.AddOnItem()
  iptu_o = iptu_m.get_adhoc_iptu_obj()
  price_cmp = monthlyprice_maincomponents_namedtuple(
    reais_baserent=1000, cond_tariff=1200, fire_comb_obj=100, iptu_obj=iptu_o
  )
  refdate = datetime.date(2020, 5, 1)
  biller = RentBiller(
    immeub_code=10,
    price_components=price_cmp,
    refdate=refdate,
    refyear=refdate.year,
    refmonth=refdate.month,
  )
  print(biller)

  priceitem = AddOnItem(
    coditem=None,
    seqitem=None,
    refyear=None,
    refmonth='2025-05',
    refdate=None,
    price=2000.0,
    b_inrefcycle=None,
    n_cota=None,
    totalcotas=None,
    ptype=None,
    descr_line1=None,
    descr_line2=None,
    )
  print(priceitem)


def adhoctest2():
  mounter = mc.MonthRangeMoraMounter(
    inimontant=1000,
    inidate=datetime.date(2025, 8, 1),
    findate=datetime.date(2026, 2, 28),
    fix_ir_pct=0.02
  )
  print(mounter)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  adhoctest()
  process()
  pass
  """
  adhoctest2()
