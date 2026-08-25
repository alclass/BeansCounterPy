"""
art/immeub/rent/testdata/rentcontracts_createdata.py
  Contains instantiation examples for the 'rent app'.
"""
from decimal import Decimal
import art.immeub.rent.billmodels.billingcard_pydantic as bcard
import art.immeub.rent.pdntcmdls.immeub_pydant as immeub  # immueb.Immeuble
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.Person
import art.immeub.rent.pdntcmdls.rentcontract_pydant as rentpydtc
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch
import lib.datesetc.datefs as dtfs
DEFAULT_3LETTER_CURRENCY = 'BRL'


def make_rentcontract_1() -> rentpydtc.PydtcRentContract:
  """
  art.immeub.rent.bill.data_example_contract.make_example_contract
  import art.immeub.rent.bill.data_example_contract as dataex  # dataex.make_example_contract
  """
  persons = pers.get_persons_by_cpfs([])
  location = immeub.get_immeuble_ex()
  monthlyrentvalue = Decimal(1000)
  contr_inidate = dtfs.make_date_or_raise("2024-1-1")
  contrnumber = location.get_contrnumber_w_inirefmonth(contr_inidate)
  rentcontract = rentpydtc.PydtcRentContract(
    contrnumber=contrnumber,
    location=location,
    inidate=contr_inidate,
    tenants=persons,
    ori_rentvalue=monthlyrentvalue,
    nmonths_duration=30,
    has_proptax=True,
    has_incendtarif=True,
    has_condtarif=True,
    currency3letter=DEFAULT_3LETTER_CURRENCY,
  )
  rentcontract.add_reajuste_w_dt_n_idx('2025-1-1', Decimal('0.035'))
  rentcontract.add_reajuste_w_dt_n_idx('2026-1-1', Decimal('0.027'))
  print(rentcontract)
  jsonstr = rentcontract.to_json_str()
  print(jsonstr)
  return rentcontract


def make_billingcard_1() -> bcard.PydtcBillingCard:
  mkdt = dtfs.make_date_or_raise
  rentcontract = dataex.make_rentcontract_1()
  billingcard = PydtcBillingCard(
    rentcontract=rentcontract,
    refmonth=mkdt('2026-5-1'),
  )
  # billingcard.print_str_table_billingitems()
  print('total', billingcard.str_billingcard())
  mng_dict = billingcard.as_mongo_json_dict()
  print(mng_dict)
  mng_json = billingcard.as_mongo_json_repr()
  print("mng_json = billingcard.as_mongo_json_repr()")
  print(mng_json)
  paydate, payvalue = mkdt('2026-06-11'), Decimal(3000)
  payment = bipydtc.PydtcPayment(
    date=paydate,
    value=Decimal(3000),
  )
  payvalue = payment.value
  paydate = payment.date
  billingcard.add_payment(payment)
  billingcard.process_payments_in_month()
  ostr = """billingcard.process_payment()
  cre = billingcard.credito_no_fecho
  deb = billingcard.debito_no_fecho
  """
  print(ostr)
  cre = billingcard.credito_no_fecho
  deb = billingcard.debito_no_fecho
  moraquinhoes = billingcard.quinhoes_days_vals
  ipca = billingcard.var_ir_as_ipca_dec
  scrmsg = f"""cre={cre:.2f}; deb={deb:.2f} | billsvalue = {billingcard.fatura_total} | duedate={billingcard.duedate} | ipca = {ipca}
   | payvalue={payvalue:.2f} | paydate={paydate} | quinhoes={moraquinhoes}"""
  print(scrmsg)
  report = billingcard.report_quinhoes_days_vals()
  print(report)
  return billingcard


def make_example_person():
  person = pers.PydtcPerson(
    nomecompleto="John Doe",
    cpf="12345678909",
    phonenumbers=["99991111"],
    emails=["johndoe@example.com"],
    docum_id="1234567",
  )
  print('via constructor', person)
  pdict = {
    'nomecompleto': "John Doe",
    'cpf': "12345678909",
    'phonenumbers': ["99991111"],
    'emails': ["johndoe@example.com"],
    'docum_id': "1234567",
  }
  person = pers.PydtcPerson.instantiate_from_jsondict(pdict)
  print('via instantiate_fr_json', person)


def make_example_rentcontract():
  rent = make_rentcontract_1()
  print(rent)
  print(rent.line())
  rent.tabulate_dates_reajustes_newrentvalues()
  rent.pprint_dates_n_rentvalues()
  bitems = rent.make_n_get_mininum_billingitems()
  print(rent)
  print(rent.line())
  rent.tabulate_dates_reajustes_newrentvalues()
  rent.pprint_dates_n_rentvalues()
  for bitem in bitems:
    print(bitem.model_dump_json(indent=2))


def adhoctest1():
  """
  make_example_person()

  """
  make_rentcontract_1()


def process():
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
