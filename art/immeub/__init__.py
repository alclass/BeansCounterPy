"""
art/immeub/__init__.py
  Contains config variables related to its package

"""
from pathlib import Path
import os
from dotenv import load_dotenv
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
# 1 MongoDB dbnamne
IMMEUB_DBNAME = os.getenv("IMMEUB_DBNAME")
