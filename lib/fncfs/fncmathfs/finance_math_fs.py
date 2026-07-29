"""
lib/fncfs/fncmathfs/finance_math_fs.py

To import it:
  import lib.fncfs.fncmathfs.finance_math_fs as fncmath  # fncmath.calc_ir_incrfact_f_mora_w_idx_n_expo()
"""
from decimal import Decimal
import decimal


def calc_ir_incrfact_f_mora_w_idx_n_expo(
    ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  """
  Returns the multiplier for the (mora) Interest Rate (ir) calculation
    based on an index (ir_idx) and an exponent

  The exponent here is independent on the duration time units (days, months, etc.),
    which might be anyone in the caller. Another function below wraps parameter 'monthduration',
    which then calls this with 'monthduration' as 'exponent'.

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


def calc_finalmontant_w_1inimontant_2ir_3expo(
    inimontant: Decimal, ir_idx: Decimal, exponent: Decimal
  ) -> Decimal:
  try:
    inimontant = Decimal(inimontant)
    ir_idx = Decimal(ir_idx)
    exponent = Decimal(exponent)
  except (ValueError, TypeError, decimal.InvalidOperation) as e:
    errmsg = f"acc index ({ir_idx}) and/or exponent ({exponent}) are invalid: {e}"
    raise ValueError(errmsg)
  increase = inimontant * calc_ir_incrfact_f_mora_w_idx_n_expo(ir_idx, exponent)
  finalmontant = inimontant + increase
  return finalmontant


def calc_finalmontant_w_1inimontant_2fixir_3varir_4monthduration(
    inimontant: Decimal, fixir: Decimal, varir: Decimal, monthduration: Decimal
  ) -> Decimal:
  ir_idx = Decimal(fixir + varir)
  return calc_finalmontant_w_1inimontant_2ir_3expo(
    inimontant=inimontant, ir_idx=ir_idx, exponent=monthduration
  )


def adhoctest1():
  ir_idx, exponent = Decimal(.023), Decimal(2)
  multiplier = calc_ir_incrfact_f_mora_w_idx_n_expo(ir_idx, exponent)
  scrmsg = f"(float res) input: ir_idx={ir_idx:.04f}, exponent={exponent} | output multiplier={multiplier:.04f}"
  print(scrmsg)
  # ===============
  inimontant = Decimal(1000)
  finalmontant = calc_finalmontant_w_1inimontant_2ir_3expo(inimontant, ir_idx, exponent)
  scrmsg = f"(dec res) input: inimontant={inimontant}, ir_idx={ir_idx:.04f}, exponent={exponent} | output finalmontant={finalmontant:.04f}"
  print(scrmsg)
  # ===============
  fixir, varir, monthduration = Decimal(.02), Decimal(.0034), Decimal(2.5)
  finalmontant = calc_finalmontant_w_1inimontant_2fixir_3varir_4monthduration(inimontant, fixir, varir, monthduration)
  scrmsg = f""" Example:
  input:  initial montant={inimontant}, fix ir={fixir:.04f}, var ir={varir:.04f}, month duration={monthduration}
  output: final montant={finalmontant:.04f}"""
  print(scrmsg)
  # ===============


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
