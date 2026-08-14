"""
lib/dbfs/mngdb/__init__.py
  Contains config-variables for the package.
"""
from pathlib import Path
import os
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
MONGODB_URI_CON_STR = os.getenv("MONGODB_URI_CON_STR", "mongodb://localhost:27017")
MONGODB_DBNAME = os.getenv("MONGODB_DBNAME", "immeub_db")
