"""
art/immeub/rent/pdntcmdls/__init__.py
  Contains default values for pdntcmdls package.
"""
from dotenv import load_dotenv
import os
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
DEFAULT_ENDR_PIX_P_PAGAR = os.getenv("DEFAULT_ENDR_PIX_P_PAGAR", "perguntar")
DEFAULT_3LETTER_CURRENCY = os.getenv("DEFAULT_3LETTER_CURRENCY", "BRL")
DEFAULT_MONTHLY_FIX_IR_DEC = os.getenv("DEFAULT_MONTHLY_FIX_IR_DEC", "0.02")
MORA_M_MINUS_N = os.getenv("MORA_M_MINUS_N", 2)


def printout_defaults():
  ostr = f"""{__doc__}
  DEFAULT_ENDR_PIX_P_PAGAR = {DEFAULT_ENDR_PIX_P_PAGAR}
  DEFAULT_3LETTER_CURRENCY = {DEFAULT_3LETTER_CURRENCY}
  DEFAULT_MONTHLY_FIX_IR_DEC = {DEFAULT_MONTHLY_FIX_IR_DEC}
  MORA_M_MINUS_N = {MORA_M_MINUS_N}
  """
  print(ostr)
  return ostr


if __name__ == "__main__":
  printout_defaults()
