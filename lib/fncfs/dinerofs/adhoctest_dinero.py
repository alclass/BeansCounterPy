from dinero import Decimal
from dinero.currencies import BRL
v = Decimal("-1", BRL)
print(v)
r = v / 3
print(r)
r = r * 3
print(r)
dec = r.raw_amount
print('raw_amount', dec)
a2 = dec.copy_abs()
print('dec.copy_abs()', a2)
w = Decimal("-2", BRL)
w = w + 1
print('w', w)
boolval = w == w
print('boolval', boolval)