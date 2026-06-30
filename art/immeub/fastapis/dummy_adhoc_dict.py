#!/usr/bin/env python3
"""
art/immeub/fastapis/dummy_adhoc_dict.py
  Contains just a dict with 'adhoc-test-data'

# Sample data – each card contains:
# - payor_name, address (multiline string), email
# - items: list of {description, original_value, add_ons}

import art/immeub/fastapis/dummy_adhoc_dict.py as dum
# dum.BILLING_DATA
"""
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
