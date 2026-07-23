"""
art/immeub/inst/cdutra/aliss_dc_accomp/mdb/serialize_dinero_n_decimal.py

For client modules:
    import immeub.inst.cdutra.aliss_dc_accomp.mdb.serialize_dinero_n_decimal as srlz_din_dec


import lib.datesetc.refmonth_fs as rmfs
"""
import datetime
import json
from dataclasses import dataclass, asdict
from dinero import Dinero  # Assuming this is your import path
from dinero.currencies import BRL
import dinero
import datetime
from decimal import Decimal, Context, ROUND_HALF_UP
from bson.decimal128 import Decimal128
from dinero import Dinero
import bson


@dataclass
class Transaction:
  amount: Dinero
  fee: Decimal


def din_dec_dict_fact(data):
  serialized = {}
  # Mathematical rounding safety configurations
  currency_ctx = Context(prec=34, rounding=ROUND_HALF_UP)
  places_dinero = Decimal('0.0001')  # 4 decimal places
  places_index = Decimal('0.00000001')  # 8 decimal places
  for key in data:
    value = data[key]
    # 1. Handle Dinero objects
    if isinstance(value, Dinero):
      rounded_amount = value.raw_amount.quantize(places_dinero, context=currency_ctx)
      serialized[key] = {
        "amount": Decimal128(rounded_amount),
        "currency": value.code  # This stays a string ("BRL") in MongoDB
      }
    # 2. Handle pure Correction Index Decimals
    elif isinstance(value, Decimal):
      rounded_val = value.quantize(places_index, context=currency_ctx)
      serialized[key] = Decimal128(rounded_val)

    # 3. Handle datetime.date objects
    elif isinstance(value, datetime.date):
      serialized[key] = datetime.datetime.combine(value, datetime.time.min)
    else:
      serialized[key] = value
  return serialized


def deserialize_mongo_doc(doc: dict) -> dict:
  """
  Converts BSON data types back to native dataclass fields,
  mapping currency strings to official Dinero currency objects.
  """
  cleaned = {}

  for key, value in doc.items():
    if key == "_id":
      continue

    # 1. Reconstruct Dinero objects using getattr()
    if isinstance(value, dict) and "amount" in value and "currency" in value:
      decimal_amount = value["amount"].to_decimal()
      currency_string = value["currency"]  # e.g., "BRL"

      try:
        # Dynamic lookup: fetches dinero.currencies.BRL object from the string "BRL"
        currency_constant = getattr(dinero.dinero_currencies, currency_string)
      except AttributeError:
        # Fallback safeguard in case an unexpected currency string appears
        raise ValueError(f"Currency symbol '{currency_string}' not found in dinero.currencies")

      cleaned[key] = Dinero(decimal_amount, currency_constant)

    # 2. Convert Decimal128 back to standard Decimal
    elif hasattr(value, "to_decimal"):
      cleaned[key] = value.to_decimal()

    # 3. Convert datetime.datetime back to standard datetime.date
    elif isinstance(value, datetime.datetime):
      cleaned[key] = value.date()

    else:
      cleaned[key] = value

  return cleaned


def example_usage():
    # Example usage
    dinero_obj = Dinero("100.50", BRL)
    decimal_obj = Decimal("2.50")

    tx = Transaction(amount=dinero_obj, fee=decimal_obj)

    # Convert to a dict using the custom factory
    tx_dict = asdict(tx, dict_factory=din_dec_dict_fact)

    # Convert to JSON string
    tx_json = json.dumps(tx_dict, indent=2)
    print(tx_json)


def adhoctest1():
  din = Dinero("100.50", BRL)
  dec = Decimal("2.50")
  today = datetime.date.today()
  pdict = {
    'din': din,
    'dec': dec,
    'dat': today
  }
  print('pdict', pdict)
  serialized = din_dec_dict_fact(pdict)
  print('serialized', serialized)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
