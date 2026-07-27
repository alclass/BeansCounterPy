"""
art/immeub/inst/cdutra/credeb_accomp_pkg/__init__.py
  Contains config-variables at this package level.

  Such as:
    REFMONTH_INI_FOR_META
    VALOR_META_MENSAL_IN_BRL
    MORA_FIX_DEC
"""
from pathlib import Path
import os
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
# ================
# 1 date config-vars
# ================
# the refmonth below is the beginning of the credeb accompanying
REFMONTH_INI_FOR_META = os.getenv("REFMONTH_INI_FOR_META")
# ================
# 2 money or finance factor config-vars
# ================
# the convention or agreement of the monthly payment goal amount
VALOR_META_MENSAL_IN_BRL = os.getenv("VALOR_META_MENSAL_IN_BRL")
MORA_FIX_FLOAT = os.getenv("MORA_FIX_FLOAT")
