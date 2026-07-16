#!/usr/bin/env python3
"""
lib/texts/json_serializers.py
  Contains JSON serializer functions

import lib.texts.re_str_fs as rstrfs
import regex
from typing import Any
"""
from dinero import Dinero


def dinero_serializer(obj):
  """
  # Example Dinero object
  amount = Dinero("100.50", "USD")
  # Serialize to a JSON string
  j_string = json.dumps(amount, default=dinero_serializer, indent=2)
  print(json_string)
  """
  if isinstance(obj, Dinero):
    return {
        "amount": str(obj.amount), # Convert Decimal to string
        "currency": obj.currency
    }
  raise TypeError("Type not serializable")

