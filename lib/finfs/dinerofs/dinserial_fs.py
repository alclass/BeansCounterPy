#!/usr/bin/env python3
"""
lib/finfs/dinserial_fs.py

  dinfs.dinero_serializer(pdate)
"""
from dinero import Dinero


def dinero_serializer(obj):
  """
  # Serialize to a JSON string
  """
  if isinstance(obj, Dinero):
    return {
      "amount": str(obj.amount),  # Convert Decimal to string
      "currency": obj.currency
    }
  raise TypeError("Type not serializable")
