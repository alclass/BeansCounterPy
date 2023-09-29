#!/usr/bin/env python3
""""
transform_numbers.py module
Mainly it transform the European number representation (dots for thousands and comma for decimal places)
  into Python's American-like format (just the dot for decimal place)
"""


def transform_european_stringnumber_to_pythonfloat(p_strnumber):
  if p_strnumber is None or len(p_strnumber) == 0:
    return None
  try:
    strnumber = str(p_strnumber)
    strnumber = strnumber.replace('.', '')
    strnumber = strnumber.replace(',', '.')
    return float(strnumber)
  except ValueError:
    pass
  return None


def test1():
  """

  """
  strnumber = "209.046,56"
  print('strnumber =>', strnumber)
  floatnumber = transform_european_stringnumber_to_pythonfloat(strnumber)
  print('transform to floatnumber =>', floatnumber)


if __name__ == '__main__':
  test1()
