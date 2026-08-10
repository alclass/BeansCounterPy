"""
art/immeubroutes/rent/db/__init__.py
  Contains config-variables related to this package.

"""
from pathlib import Path
import os
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
LOCAL_MONGODB_CONSTR = os.getenv("LOCAL_MONGODB_CONSTR")
IMMEUB_DBNAME = os.getenv("IMMEUB_DBNAME", "immeub_db")
# collection names
BILLINGCARD_COLLNAME = os.getenv("BILLINGCARD_COLLNAME", "billingcards")
IMMEUBLE_COLLNAME = os.getenv("IMMEUBLE_COLLNAME", "immeub_db")
PERSON_COLLNAME = os.getenv("PERSON_COLLNAME", "persons")
CONTRACT_COLLNAME = os.getenv("CONTRACT_COLLNAME", "contracts")


def show_env_vars():
  """
  print(show_env_vars())
  """
  ostr = f"""
    LOCAL_MONGODB_CONSTR={LOCAL_MONGODB_CONSTR}
    IMMEUB_DBNAME={IMMEUB_DBNAME}
    BILLINGCARD_COLLNAME={BILLINGCARD_COLLNAME}
    PERSON_COLLNAME={PERSON_COLLNAME}
    IMMEUBLE_COLLNAME={IMMEUBLE_COLLNAME}
    CONTRACT_COLLNAME={CONTRACT_COLLNAME}
  """
  return ostr
