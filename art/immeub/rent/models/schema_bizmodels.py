#!/usr/bin/env python3
"""
art/immeub/rent/models/schema_bizmodels.py

# ==========================================
# MONGO DOCUMENTS (DB LAYOUT)
# ==========================================
"""
import datetime
from dinero import Dinero
from typing import List
from beanie import Document, Link


class Person(Document):
  name: str
  cpf: str
  birthcity: str
  birthdate: str
  address: list[str]
  marital_st: str
  city: str
  ident_alt: str
  phone: list[str]
  email: list[str]

  class Settings:
    name = "persons"  # Mongo-collection name


class Location(Document):
  nickname: str
  condname: str
  address: list[str]
  municip: str
  uf: str
  municip_inscr: str
  ff_inscr: str
  cartorio_inscr: str
  est_rent_m_price_range: tuple[float, float]
  est_cond_m_price_range: tuple[float, float]
  est_ptax_y_price_range: tuple[float, float]
  est_fftar_y_price_range: tuple[float, float]
  lat_lon: tuple[float, float]
  owners: list[Person]
  physcharacteristics: str
  nonphyscharacteristics: str

  class Settings:
    name = "locations"  # Mongo-collection name


class Contract(Document):
  refcode: str
  location: Link[Location]
  tenants: List[Link[Person]]
  inidate: datetime.date
  duration_in_months: int
  ori_monthly_price: Dinero
  cur_monthly_price: Dinero
  history_prices: dict[datetime.date, Dinero]
  fix_m_monecorr_dec: float
  var_m_monecorr_idxname: str
  monthly_dueday: int
  comments: str

  class Settings:
    name = "contracts"  # Mongo-collection name


class BillingItem(Document):
  seq: int
  description: str
  value: Dinero
  refmonth: datetime.date
  mora: Dinero
  explains: str
  itemtotal: Dinero
  comments: str

  class Settings:
    name = "billingitems"  # Mongo-collection name


class BillingCard(Document):
  bill_refcode: str
  contract: Contract
  remonth: datetime.date
  duedate: datetime.date
  readydate: datetime.date
  closedate: datetime.date
  billingitems: list[BillingItem]
  total: Dinero
  comments: str

  class Settings:
    name = "billingcards"  # Mongo-collection name
