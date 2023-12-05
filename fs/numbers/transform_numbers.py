#!/usr/bin/env python3
""""
transform_numbers.py module
Mainly it transform the European number representation (dots for thousands and comma for decimal places)
  into Python's American-like format (just the dot for decimal place)
"""


def invert_strchars(stri):
  if stri is None:
    return None
  if len(stri) == 0:
    return ''
  if len(stri) == 1:
    return stri
  if stri.find(','):
    stri = stri.replace(',', '')
  lista = list(stri)
  lista.reverse()
  reversed_str = ''.join(lista)
  return reversed_str


def place_thousand_dots_in_number_as_strnumber(str_or_number):
  strdecplace = ''
  str_or_number = str(str_or_number)
  if str_or_number.find(','):
    pp = str_or_number.split('.')
    strintnumber = pp[0]
    strdecplace = pp[1]
  else:
    strintnumber = str_or_number
  dottednumber = strintnumber
  reversed_strn = invert_strchars(strintnumber)
  stack = []
  while 1:
    if len(reversed_strn) > 3:
      trunk = reversed_strn[0:3]
      stack.append(trunk)
      reversed_strn = reversed_strn[3:]
    else:
      if len(reversed_strn) > 0:
        stack.append(reversed_strn)
        dottednumber = '.'.join(stack)
        dottednumber = invert_strchars(dottednumber)
      break
  if len(strdecplace) == 0:
    strdecplace = '00'
  dottednumber = dottednumber + ',' + strdecplace
  return dottednumber


def swap_thousandcommas_n_decplacecomma_to_europeanformat(str_or_number):
  if str_or_number is None:
    return None
  try:
    n = float(str_or_number)
  except ValueError:
    return None
  # at this point, str_or_number does represent a number (int or float)
  str_or_number = str(str_or_number)
  if str_or_number.find('.') > -1:
    str_or_number = str_or_number.replace('.', '_')
  if n >= 1000 or n <= -1000:  # the idea is to put a dot if number is 1000 or above or its negative reflexive
    if str_or_number.find(',') > -1:
      str_or_number = str_or_number.replace(',', '.')
    else:
      str_or_number = place_thousand_dots_in_number_as_strnumber(str_or_number)


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
  strnumber = "209.046,56"
  print('strnumber =>', strnumber)
  floatnumber = transform_european_stringnumber_to_pythonfloat(strnumber)
  print('transform to floatnumber =>', floatnumber)

  """
  str_or_number = '1,000,432.34'
  dottednumber = place_thousand_dots_in_number_as_strnumber(str_or_number)
  print(str_or_number, 'place_thousand_dots_in_number_as_strnumber =>', dottednumber)


if __name__ == '__main__':
  test1()
