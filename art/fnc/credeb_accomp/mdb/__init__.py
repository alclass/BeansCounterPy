"""
art/fnc/credeb_accomp/mdb/__init__.py
  Contains config variables related to its package

"""
from pathlib import Path
import os
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
LOCAL_MONGODB_CONSTR = os.getenv("LOCAL_MONGODB_CONSTR")
IMMEUB_DBNAME = os.getenv("IMMEUB_DBNAME", "immeub_db")
CREDEB_ACCOMP_COLLNAME = os.getenv("CREDEB_ACCOMP_COLL", "credeb_accomp_coll")
