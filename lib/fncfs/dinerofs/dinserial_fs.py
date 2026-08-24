#!/usr/bin/env python3
"""
lib/fncfs/dinserial_fs.py

  dinfs.dinero_serializer(pdate)
"""
from decimal import Decimal
from dinero.currencies import BRL
from dinero.types import Currency
import dinero


def dinero_serializer(obj):
  """
  # Serialize to a JSON string
  """
  if isinstance(obj, Decimal):
    return {
      "amount": str(obj.amount),  # Convert Decimal to string
      "currency": obj.currency
    }
  raise TypeError("Type not serializable")


def get_custom_currency() -> Currency:
  return {
      "code": "XAU",
      "base": 10,
      "exponent": 2,  # 2 is the same as two decimal places
      "symbol": "Au",
  }



def adhoctest2():
  currency = get_custom_currency()
  din = Decimal('100', currency)
  print(din)


def adhoctest1():
  """
  """
  din = Decimal(10.0, BRL)
  currency_string = din.currency['code']
  notation = din.currency['symbol']
  print(notation, din)
  pdict = dinero_serializer(din)
  print(pdict)
  currency_constant = getattr(dinero.currencies, currency_string)
  print('currency_constant', currency_constant, type(currency_constant))


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
  adhoctest2()
