#!/usr/bin/env python3
"""
lib/texts/textfs.py

"""
import re
# import string
lowerletters = 'abcdefghijklmnopqrstuvwxyz'  # string.ascii_lowercase
# Any = any
from typing import Any


def is_all_letters_asciilower(word):
  bool_list = list(map(lambda x: x in lowerletters, word))
  if False in bool_list:
    return False
  return True


def cleanup_str_leaving_only_numbers_or_dashes(p_stri: Any | None) -> str | None:
  """

  # rstrfs.cleanup_str_leaving_only_numbers_or_dashes()
  Example:
    input:  "Phone: +1-555-867-5309 (Cell!)"
    output: 1-555-867-5309
  """
  if p_stri is None:
    return None
  try:
    in_str = str(p_stri)
    # matches anything that is NOT a number or a hyphen
    cleaned_str = re.sub(r'[^0-9-]', '', in_str)
    return cleaned_str
  except (TypeError, ValueError):
    pass
  return None


def increase_one_to_letter(p_word):
  """
  It adds 'one' to the letters in word as it were a number
  This function implements a carry-one mechanism for adding one to letters indefinitely

  Examples:
    'a' => 'b'
    'z' => 'aa'
    'blah' => 'blai'
    'blai' => 'blaj'
    'zyz' => 'zza'
    'zza' => 'zzb'
    'zzz' => 'aaaa'
  """
  if p_word is None or len(p_word) == 0:
    return ''
  p_word = p_word.lower()
  if not is_all_letters_asciilower(p_word):
    errmsg = f"{p_word} is not all ASCII lowercase"
    raise ValueError(errmsg)
  letterlist = list(p_word)
  letter = letterlist.pop()  # removes and get letterlist[-1]
  if letter == 'z':
    if len(letterlist) == 0:
      return 'aa'
    word = ''.join(letterlist)
    leftside = increase_one_to_letter(word)
    return leftside + 'a'
  idx = lowerletters.index(letter)
  nextletter = lowerletters[idx+1]
  if len(letterlist) == 0:
    return nextletter
  word = ''.join(letterlist) + nextletter
  return word


def adhoctest1():
  word = 'blah'
  result = increase_one_to_letter(word)
  print(word, '=>', result)
  word = result
  result = increase_one_to_letter(word)
  print(word, '=>', result)
  word = 'zyz'
  result = increase_one_to_letter(word)
  print(word, '=>', result)
  word = result
  result = increase_one_to_letter(word)
  print(word, '=>', result)
  word = 'açz'
  boolvalue = is_all_letters_asciilower(word)
  print(word, '=> is all letters asciilower', boolvalue)
  word = 'agz'
  boolvalue = is_all_letters_asciilower(word)
  print(word, '=> is all letters asciilower', boolvalue)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
