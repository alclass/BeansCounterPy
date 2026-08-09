"""
art/immeub/rent/pydantmodels/__init__.py
  Contains default values for pydantmodels package.
"""
from dotenv import load_dotenv
import os
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
DEFAULT_ENDR_PIX_P_PAGAR = os.getenv("DEFAULT_ENDR_PIX_P_PAGAR", "perguntar")
DEFAULT_3LETTER_CURRENCY = os.getenv("DEFAULT_3LETTER_CURRENCY", "BRL")

def printout_defaults():
  ostr = f"""{__doc__}
  DEFAULT_ENDR_PIX_P_PAGAR = {DEFAULT_ENDR_PIX_P_PAGAR}
  DEFAULT_3LETTER_CURRENCY = {DEFAULT_3LETTER_CURRENCY}
  """
  print(ostr)
  return ostr


if __name__ == "__main__":
  printout_defaults()