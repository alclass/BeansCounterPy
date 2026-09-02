"""
lib/fncfs/credeb_pkg/pay_dt_val_interrface.py
  Contains class PaymentInterfaceDateNValue
    which is a simple 'interface' with 'exposes'
    date and value of a payment.

To import it:
  import lib.fncfs.credeb_pkg.pay_dt_val_interrface as intrfc  # intrfc.PaymentInterfaceDateNValue

"""
from decimal import Decimal, Context, ROUND_HALF_UP
import datetime
from dataclasses import dataclass, field
DECIMAL_ZERO = Decimal('0')
DECIMAL_ONE = Decimal('1')
M_MINUS_N = 2


# @dataclass
class PaymentInterfaceDateNValue:
  """
  This class is just to contain payment's date and value.
  Clients will use it with obj.date and obj.value

  It aims to simplify the two fields for objects
    coming from a Pydantic class with more attributes.
  """
  def __init__(self, date: datetime.date, value: Decimal):
    self.date: datetime.date
    self.value: Decimal

  def __str__(self):
    ostr = f"payvalue={self.value} on {self.date}"
    return ostr


def adhoctest1():
  """
  """
  pass


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
