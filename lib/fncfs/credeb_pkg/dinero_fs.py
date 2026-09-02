from dinero import Dinero
from dinero.currencies import BRL
DINERO_ZERO = Dinero(str("0"), BRL)


def make_decimal_w_appcontext(val: str | int | float | Decimal, n_decimal_places: int = 4) -> Decimal:
  if n_decimal_places == 4:
    str_decimal_places = ONE_THOUSANDTH_AS_STR
  else:
    str_decimal_places = '0.' + '0'*(n_decimal_places-1) + '1'
  return Decimal(val, DECIMAL_CTX).quantize(Decimal(str_decimal_places))


def get_brl_dinero(value):
  """
  DEPRECATED (in the sense of no longer used)
  In this app, Dinero has become Decimal
  """
  if isinstance(value, Decimal):
    return value
  try:
    flo = float(value)
    din = Dinero(flo, BRL)
    return din
  except ValueError:
    pass
  try:
    strvalue = str(value)
    # if strvalue is a representation of Dinero, it may contain ',' for thousands
    # which should be removed or else a dinero.exceptions.InvalidOperationError exception will be raised
    strvalue = strvalue.replace(',', '')
    din = Dinero(strvalue, BRL)
    return din
  except dinero.exceptions.InvalidOperationError as e:
    errmsg = f"Error: The value {value} (type {type(value)}) is not a valid dinero."
    raise ValueError(errmsg + str(e))
