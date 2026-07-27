from decimal import Decimal
from dinero import Dinero
from dinero.currencies import BRL
import bson

f = 1/2
d = Decimal(f)
bson.decimal128.Decimal128(d)
din = Dinero(1/3, BRL)
print(din.raw_amount)
print(din)