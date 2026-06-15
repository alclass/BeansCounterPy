#!/usr/bin/env python3
"""
lib/datesetc/stringify_datetimes.py
  Contains stringify functions for datetimes objects
    that do not have a "direct" string-representation

  The first one here is stringify_timedelta()
"""
import datetime


def stringify_timedelta(duration, if_none_returns_strna=False):
  """
  import lib.datesetc.stringify_datetimes.stringify_timedelta as strtdelta
  strtdelta.stringify_timedelta(duration)
  """
  try:
    if isinstance(duration, datetime.timedelta):
      totsecs = int(duration.total_seconds())
      hs, remainder = divmod(totsecs, 3600)
      mins, secs = divmod(remainder, 60)
      # format as string
      duration_str = f"{hs:02}:{mins:02}:{secs:02}"
      return duration_str
  except (AttributeError, TypeError, ValueError):
    pass
  if if_none_returns_strna:
    return "n/a"
  return None
