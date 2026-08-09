from decimal import Decimal
from dinero import Decimal
from dinero.currencies import BRL
import bson

f = 1/2
d = Decimal(f)
bson.decimal128.Decimal128(d)
din = Decimal(1 / 3, BRL)
print(din.raw_amount)
print(din)