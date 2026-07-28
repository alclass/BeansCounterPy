"""
lib/fncfs/indices/indices_fetch_n_fs.py

import lib.fncfs.indices.indices_fetch_n_fs as ipfs  # ipfs.ipca_for_refmonth
"""
from decimal import Decimal
import decimal


def calc_ir_incrfact_f_mora_w_idx_n_expo(ir_idx, exponent):
  """
  Returns the multiplier for the (mora) Interest Rate (ir) calculation
    based on an index (ir_idx) and an exponent
    (this is independent on the duration time or cycle, which might be anyone in the caller)

  Acronyms:
    ir -> interest rate
    ir idx -> interest rate index
    incrfactor -> interest rate multiplier for finding the 'incr' (increment factor)
  """
  try:
    ir_idx = Decimal(ir_idx)
    exponent = Decimal(exponent)
  except (ValueError, TypeError, decimal.InvalidOperation) as e:
    errmsg = f"acc index ({ir_idx}) and/or exponent ({exponent}) are invalid: {e}"
    raise ValueError(errmsg)
  intermediate = (1 + ir_idx) ** exponent
  multiplier = intermediate - 1
  return multiplier


def get_dec_ir_incrfact_f_mora_w_idx_n_expo(ir_idx, exponent):
  multiplier = calc_ir_incrfact_f_mora_w_idx_n_expo(ir_idx, exponent)
  multiplier = Decimal(multiplier)
  return multiplier


def adhoctest1():
  ir_idx, exponent = 0.023, 2
  multiplier = calc_ir_incrfact_f_mora_w_idx_n_expo(ir_idx, exponent)
  scrmsg = f"(float res) input: ir_idx={ir_idx}, exponent={exponent} | output multiplier={multiplier}"
  print(scrmsg)
  multiplier = get_dec_ir_incrfact_f_mora_w_idx_n_expo(ir_idx, exponent)
  scrmsg = f"(dec res) input: ir_idx={ir_idx}, exponent={exponent} | output multiplier={multiplier}"
  print(scrmsg)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  adhoctest2()
  """
  adhoctest1()
