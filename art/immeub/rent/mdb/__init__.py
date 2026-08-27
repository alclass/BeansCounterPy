"""
art/immeub/rent/mdb/__init__.py
  Contains config-variables related to this package.

"""
from pathlib import Path
import os
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
MONGODB_CON_STR = os.getenv("MONGODB_CON_STR", "mongodb://localhost:27017")
IMMEUB_MNGDBNAME = os.getenv("IMMEUB_MNGDBNAME", "immeub_db")
# collection names
PERSON_COLLNAME = os.getenv("PERSON_COLLNAME", "persons")
IMMEUBLE_COLLNAME = os.getenv("IMMEUBLE_COLLNAME", "immeubles")
RENTCONTRACT_COLLNAME = os.getenv("CONTRACT_COLLNAME", "rentcontracts")
BILLINGCARD_COLLNAME = os.getenv("BILLINGCARD_COLLNAME", "billingcards")



def show_env_vars():
  """
  print(show_env_vars())
  """
  ostr = f"""
    LOCAL_MONGODB_CONSTR={MONGODB_CON_STR}
    IMMEUB_MNGDBNAME={IMMEUB_MNGDBNAME}
    BILLINGCARD_COLLNAME={BILLINGCARD_COLLNAME}
    PERSON_COLLNAME={PERSON_COLLNAME}
    IMMEUBLE_COLLNAME={IMMEUBLE_COLLNAME}
    CONTRACT_COLLNAME={RENTCONTRACT_COLLNAME}
  """
  return ostr
