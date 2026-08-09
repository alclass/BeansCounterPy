#!/usr/bin/env python3
"""
art/immeub/rent/pydantmodels/contract_molder.py
  This class is the molding for the creation of a rent billing card

# from dinero.currencies import BRL
"""
from dataclasses import dataclass, field   # , asdict
import datetime
from dateutil.relativedelta import relativedelta
from dinero import Decimal
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
from typing import List
from beanie import Document, Link


@dataclass
class ContractMolder(Document):
  pass
