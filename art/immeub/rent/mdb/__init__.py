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
LOCAL_MONGO_CONSTR = os.getenv("LOCAL_MONGO_CONSTR")
IMMEUB_MNGDBNAME = os.getenv("IMMEUB_MNGDBNAME")
COBRANCA_MNGCOLLNAME = os.getenv("COBRANCA_MNGCOLLNAME")
FECHO_MNGCOLLNAME = os.getenv("FECHO_MNGCOLLNAME")
PERSON_MNGCOLLNAME = os.getenv("PERSON_MNGCOLLNAME")
IMMEUB_MNGCOLLNAME = os.getenv("IMMEUB_MNGCOLLNAME")
CONTRACT_MNGCOLLNAME = os.getenv("CONTRACT_MNGCOLLNAME")


def repres():
  ostr = f"""
    {LOCAL_MONGO_CONSTR}
    {IMMEUB_MNGDBNAME}
    {COBRANCA_MNGCOLLNAME}
    {FECHO_MNGCOLLNAME}
    {PERSON_MNGCOLLNAME}
    {IMMEUB_MNGCOLLNAME}
    {CONTRACT_MNGCOLLNAME}
  """
  return ostr
