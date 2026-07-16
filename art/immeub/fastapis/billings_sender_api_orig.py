#!/usr/bin/env python3
"""
art/immeubroutes/fastapis/billings_sender_api.py

uvicorn art/immeubroutes/fastapis/billings_sender_api:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Sample data – each card contains:
# - payor_name, address (multiline string), email
# - items: list of {description, original_value, add_ons}
BILLING_DATA = [
  {
    "payor_name": "Acme Corp",
    "address": "123 Main St\nSuite 400\nSpringfield, IL 62701",
    "email": "billing@acme.com",
    "items": [
      {"description": "Consulting services", "original_value": 1200.00, "add_ons": 150.00},
      {"description": "Software license", "original_value": 500.00, "add_ons": 0.00},
      {"description": "Training session", "original_value": 800.00, "add_ons": 200.00},
    ]
  },
  {
    "payor_name": "Beta Industries",
    "address": "456 Oak Ave\nBuilding B\nMetropolis, NY 10001",
    "email": "finance@beta.com",
    "items": [
      {"description": "Equipment rental", "original_value": 2000.00, "add_ons": 350.00},
      {"description": "Maintenance plan", "original_value": 300.00, "add_ons": 0.00},
    ]
  }
]


def process():
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  """
  process()

app = FastAPI()
# Allow requests from your Node.js frontend (default port 3000)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_methods=["GET"],
)


@app.get("/api/billing")
async def get_billing():
    return BILLING_DATA
