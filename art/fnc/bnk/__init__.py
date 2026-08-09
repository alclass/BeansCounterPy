"""
art/fnc/bnk/__init__.py
  Contains config-variables for the package
"""
import os
from pathlib import Path
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
BB_FI_EXTRACTS_ROOT_FOLDERNAME = os.getenv(
  "BB_FI_EXTRACTS_ROOT_FOLDERNAME", "FI Extratos Mensais Ano a Ano BB OD"
)
BB_FI_EXTRACTS_FOLDERNAME_YEAR_INTERPOL = os.getenv(
  "BB_FI_EXTRACTS_FOLDERNAME_YEAR_INTERPOL", "{year} FI Extratos Mensais BB"
)
BB_FI_EXTRACT_FILENAME_YEARMONTH_INTERPOL = os.getenv(
  "BB_FI_EXTRACT_FILENAME_YEARMONTH_INTERPOL", '{year}-{month:02d} FI extrato BB.txt'
)
SUBFOLDER_BANKDATA = os.getenv("SUBFOLDER_BANKDATA", 'bankdata')
