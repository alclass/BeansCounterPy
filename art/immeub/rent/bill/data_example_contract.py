"""

"""
from decimal import Decimal
import art.immeub.rent.pydantmodels.immeub_pydant as immeub  # immueb.Immeuble
import art.immeub.rent.pydantmodels.person_pydant as pers  # pers.Person
import art.immeub.rent.pydantmodels.rentcontract_pydant as rentpydtc  # rentpydtc.PydtcRentContract
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs


def make_example_contract() -> rentpydtc.PydtcRentContract:
  """
  art.immeub.rent.bill.data_example_contract.make_example_contract
  import art.immeub.rent.bill.data_example_contract as dataex  # dataex.make_example_contract
  """
  person = pers.get_person_ex()
  location = immeub.get_immeuble_ex()
  rentvalue = Decimal(1000)
  rent = rentpydtc.PydtcRentContract(
    location=location,
    inidate=dtfs.make_date_or_raise("2024-1-1"),
    tenants=[person],
    ori_rentvalue=rentvalue,
    nmonths_duration=30,
    has_proptax=True,
    has_incendtarif=True,
    has_condtarif=True,
    # currency3letter=DEFAULT_3LETTER_CURRENCY,
    # imm_nickname='Jack',
  )
  print(rent)
  rent.add_reajuste_w_dt_n_idx('2025-1-1', Decimal('0.035'))
  rent.add_reajuste_w_dt_n_idx('2026-1-1', Decimal('0.027'))
  return rent


def adhoctest1():
  rent = make_example_contract()
  print(rent)
  print(rent.line())
  rent.tabulate_dates_reajustes_newrentvalues()
  rent.pprint_dates_n_rentvalues()
  bitems = rent.make_mininum_billingitems()
  print(rent)
  print(rent.line())
  rent.tabulate_dates_reajustes_newrentvalues()
  rent.pprint_dates_n_rentvalues()
  bitems = rent.make_mininum_billingitems()
  print(bitems)


def process():
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
