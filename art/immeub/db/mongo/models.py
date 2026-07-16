from typing import List
from beanie import Document, Link
from pydantic import BaseModel, Field


# 1. Person / Tenant Entity
class Person(Document):
  name: str
  email: str

  class Settings:
    name = "persons"


# 2. Real Estate Location Entity
class Location(Document):
  address: str
  city: str
  monthly_rent: float

  class Settings:
    name = "locations"


# 3. Contract Entity (Referencing Location and multiple People)
class Contract(Document):
  contract_number: str

  # Single reference (One-to-One / Many-to-One)
  location: Link[Location]

  # List of references (Many-to-Many / One-to-Many)
  tenants: List[Link[Person]]

  class Settings:
    name = "contracts"
