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
import datetime
from decimal import Decimal
import bson


@dataclass
class Transaction:
  amount: Dinero
  fee: Decimal


def din_dec_dict_fact(data):
  serialized = {}
  for key, value in data:
    # 1. Handle Dinero objects
    if isinstance(value, Dinero):
      # Convert the underlying Decimal amount to MongoDB's native Decimal128
      flo = value.raw_amount
      serialized[key] = {
        "amount": bson.decimal128.Decimal128(flo),
        "currency": value.code
      }

    # 2. Handle pure Decimal objects
    elif isinstance(value, Decimal):
      # Save as native MongoDB numeric Decimal128 instead of a string
      serialized[key] = bson.decimal128.Decimal128(value)

    # 3. Handle datetime.date objects
    elif isinstance(value, datetime.date):
      # Convert to a midnight datetime object
      # This allows MongoDB to treat it as a true Date type for sorting/filtering
      serialized[key] = datetime.datetime.combine(value, datetime.time.min)

    # 4. Leave all other fields (strings, ints, floats, booleans) as they are
    else:
      serialized[key] = value

  return serialized


def din2(data):
  """
  Recursively convert custom objects to JSON-compatible primitives.

    Obs:
      This factory function is prepared for @dataclass DebCredAccompanier
      in art/immeub/inst/cdutra/aliss_dc_accomp/alssn_deb_cre_accompanying.py

      However, because it contains 'types'
        Dinero, Decimal (with 4 decimal places), and datetime.date,
      it may be reused for other classes that do not need more than 4 decimal places in their 'decimals'.
  """
  serialized = {}
  for key, value in data:
    if isinstance(value, Dinero):
    # Convert Dinero object to its dict or string representation
      serialized[key] = {
        "amount": str(value.amount),
        "currency": value.code
      }
    elif isinstance(value, Decimal):
      # Convert Decimal to string (best practice for JSON to avoid precision loss)
      # the only one field in 'CreDebAccompanier' is _ipca_dec
      serialized[key] = f"{value:.04f}"
    elif isinstance(value, datetime.date):
      # refmonth (though field 'day' is always 1) is a datetime.date type
      # other date's may be included in 'CreDebAccompanier'
      # refmonth is only yyyy-mm but let it be yyy-mm-dd because it is a 'logical type' with type date
      strdate = value.strftime("%Y-%m-%d")
      serialized[key] = strdate
    else:
      serialized[key] = value
  return serialized


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


def process():
  """
  """
  pass


if __name__ == '__main__':
  process()
