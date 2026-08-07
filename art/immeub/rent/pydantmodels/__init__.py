from dotenv import load_dotenv
import os
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
env_path = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
DEFAULT_ENDR_PIX_P_PAGAR = os.getenv("DEFAULT_ENDR_PIX_P_PAGAR")
