"""
art/immeub/inst/cdutra/aliss_dc_accomp/mdb/serialize_dinero_n_decimal.py

For client modules:
    import immeub.inst.cdutra.aliss_dc_accomp.mdb.serialize_dinero_n_decimal as srlz_din_dec

import lib.datesetc.refmonth_fs as rmfs
import datetime
import bson
import json
"""
from dataclasses import dataclass, asdict
import dinero
from dinero import Dinero
from dinero.currencies import BRL
import datetime
from decimal import Decimal, Context, ROUND_HALF_UP
from bson.decimal128 import Decimal128
from decimal import Decimal
import pprint


@dataclass
class Transaction:
  amount: Decimal
  fee: Decimal


def serialize_credeb_for_json_as_dict(data):
  print('dict(data)', data)
  data = dict(data)
  serialized = {}
  # Mathematical rounding safety configurations
  currency_ctx = Context(prec=34, rounding=ROUND_HALF_UP)
  places_dinero = Decimal('0.0001')  # 4 decimal places
  places_index = Decimal('0.00000001')  # 8 decimal places
  for key in data:
    print('key data', key, data)
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


def deserialize_mongo_doc(doc: dict, is_data_from_db=False) -> dict:
  """
  Converts BSON data types back to native dataclass fields,
  mapping currency strings to official Dinero currency objects.

  if is_data_from_db is True, it avoids updatings in the __post_init__() method in the model class
  """
  cleaned = {}

  for key, value in doc.items():
    if key == "_id":
      continue

    # 1. Reconstruct Dinero objects using getattr()
    if isinstance(value, dict) and "amount" in value and "currency" in value:
      decimal_special_dict = value["amount"]
      decimal_amount = None
      try:
        decimal_amount = decimal_special_dict.to_decimal()
      except (AttributeError, TypeError):
        pass
      if decimal_amount is None:
        decimal_amount = Decimal(decimal_special_dict['$numberDecimal'])
      # scrmsg = f"{__name__} value = {value} | decimal_amount = {decimal_amount} "
      # print(scrmsg)
      currency_string = value["currency"]  # e.g., "BRL"
      try:
        # dynamic lookup: fetches dinero.currencies with getattr(din_curencies, "BRL")
        # it doesn't get the constant (in this case BRL), it gets rather a dict that can instantiate back 'dinero'
        currency_dict = getattr(dinero.currencies, currency_string)
        pass
      except AttributeError:
        # Fallback safeguard in case an unexpected currency string appears
        raise ValueError(f"Currency symbol '{currency_string}' not found in dinero.currencies")
      cleaned[key] = Dinero(decimal_amount, currency_dict)

    # 2. Convert Decimal128 back to standard Decimal
    elif hasattr(value, "to_decimal"):
      cleaned[key] = value.to_decimal()

    # 3. Convert datetime.datetime back to standard datetime.date
    elif isinstance(value, datetime.datetime):
      cleaned[key] = value.date()

    else:
      cleaned[key] = value

  if is_data_from_db:
    cleaned['is_data_from_db'] = True
  return cleaned


def example_usage():
    # Example usage
    dinero_obj = Decimal("100.50", BRL)
    decimal_obj = Decimal("2.50")

    tx = Transaction(amount=dinero_obj, fee=decimal_obj)

    # Convert to a dict using the custom factory
    tx_dict = asdict(tx, dict_factory=serialize_credeb_for_json_as_dict)

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
  print('pdict')
  pprint.pprint(pdict)
  serialized = serialize_credeb_for_json_as_dict(pdict)
  print('serialized')
  pprint.pprint(serialized)
  deserialized = deserialize_mongo_doc(serialized)
  print('deserialized')
  pprint.pprint(deserialized)



def adhoctest2():
  false = False
  pjson = {
    "_id": {
      "$oid": "6a64e686fd0352236c4f78f1"
    },
    "refmonth": {
      "$date": "2026-04-01T00:00:00.000Z"
    },
    "_corrmone_n_intrst_if_any": {
      "amount": {
        "$numberDecimal": "-28.8300"
      },
      "currency": "BRL"
    },
    "finvalue_d2": {
      "amount": {
        "$numberDecimal": "-1990.4500"
      },
      "currency": "BRL"
    },
    "finvalue_res": {
      "amount": {
        "$numberDecimal": "0.0000"
      },
      "currency": "BRL"
    },
    "inivalue_d2": {
      "amount": {
        "$numberDecimal": "-1067.9200"
      },
      "currency": "BRL"
    },
    "inivalue_res": {
      "amount": {
        "$numberDecimal": "0.0000"
      },
      "currency": "BRL"
    },
    "_ipca_dec": {
      "$numberDecimal": "0.00700000"
    },
    "cre_in_pay": {
      "amount": {
        "$numberDecimal": "0.0000"
      },
      "currency": "BRL"
    },
    "cre_in_tasks": {
      "amount": {
        "$numberDecimal": "210.6200"
      },
      "currency": "BRL"
    },
    "cre_in_trnsp_n_frut": {
      "amount": {
        "$numberDecimal": "45.6800"
      },
      "currency": "BRL"
    },
    "deb_giro": {
      "amount": {
        "$numberDecimal": "-650.0000"
      },
      "currency": "BRL"
    },
    "inivalue_d1": {
      "amount": {
        "$numberDecimal": "-21900.0000"
      },
      "currency": "BRL"
    },
    "is_closed_n_in_db": false
  }
  deserialized = deserialize_mongo_doc(pjson)
  print('deserialized')
  pprint.pprint(deserialized)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
