#!/usr/bin/env python3
"""
fs/strfs/extractors.py
  Lib functions for extract substrings from string.
"""
import datetime
import re
import string
restr = r'( ML(?P<price>[\d+.\d{2}]) )?'
recmp = re.compile(restr)
# the next regex helps extract a yyyy-mm-dd date when starting a string
re_str_starts_w_date = r"^(?P<date>\d{4}\-\d{2}\-\d{2})"
re_cmp_starts_w_date = re.compile(re_str_starts_w_date)


def extract_date_at_the_beginning_of_str(pstr):
  match_o = re_cmp_starts_w_date.match(pstr)
  if match_o:
    pdate = match_o.group('date')
    try:
      return datetime.datetime.strptime(pdate, '%Y-%m-%d').date()
    except ValueError:
      pass
  return None


def extract_number_at_the_beginning_of_str(pstr, decsep=','):
  """
  The 'contract' in here supposes that char[0] is already a digit-number
  The 'parsing' ends when either a second separator-char is reached or
  a non-number is found
  """
  strnumber = ""
  separator_found = 0
  for c in pstr:
    if c == decsep:
      separator_found += 1
      if separator_found > 1:
        break
      strnumber = strnumber+decsep
      continue
    if c in string.digits:
      strnumber = strnumber+c
      continue
    else:
      break
  strnumber = strnumber.replace(',', '.')
  number = float(strnumber)
  return number


def extract_number_after_its_prefixing_chars(pstr, prefixchars=' ML', decsep=','):
  pos = pstr.find(prefixchars)
  if pos > -1:
    pos = pos + 3  # right-shift pos, 3 is len(' ML')
    if pos < len(pstr) - 1:
      if pstr[pos] in string.digits:
        numberstr = pstr[pos:]
        floatn = extract_number_at_the_beginning_of_str(numberstr, decsep)
        return floatn
  return None


def adhoc_test3():
  t = "2025-11-21 ML99,26 2itens bla foo bar"
  pdate = extract_date_at_the_beginning_of_str(t)
  print('pdate', pdate)
  t = "2025-11-21 ML99,26 2itens bla foo bar"
  price = extract_number_after_its_prefixing_chars(t)
  print('price', price)


def adhoc_test2():
  t = "2025-11-21 ML99,26 2itens bla foo bar"
  floatn = extract_number_after_its_prefixing_chars(t)
  print('floatn', floatn)


def adhoc_test():
  t = "2025-11-21 ML99,26 2itens"
  o = recmp.match(t)
  if o:
    print(1, o)
    print(2, o.group('price'))
  else:
    print('not found')


if __name__ == '__main__':
  """
  adhoc_test()
  """
  adhoc_test3()
