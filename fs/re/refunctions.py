#!/usr/bin/env python3
"""
fs/re/refunctions.py
  contains text tranforming functions using regular expressions

In particular, the functions:

  1  step1_remove_thousands_point_sep_in_numbers_via_re(input_text):
  2  step2_convert_commasep_to_pointsep_in_numbers_via_re(input_text):

are used to convert texts with decimal place comma marker to those with the point marker instead.
"""
import re
point_decimal_place_compiled_re = re.compile(r'(?<=\d)\.(?=\d)')
comma_decimal_place_compiled_re = re.compile(r'(?<=\d),(?=\d)')


def step1_remove_thousands_point_sep_in_numbers_via_re(input_text):
  """
  Step 1: remove all thousands points in numbers
          this will avoid their being wrongly seen as decimal points after the comma-decimal conversion next
  """
  output_text = point_decimal_place_compiled_re.sub('', input_text)
  return output_text


def step2_convert_commasep_to_pointsep_in_numbers_via_re(input_text):
  """
  Step 2: replace all comma decimal points to point ones in numbers
          notice that in Step 1 thousands points were removed (above)
  """
  output_text = comma_decimal_place_compiled_re.sub('.', input_text)
  return output_text


def convert_decimalplace_comma_to_point_via_re_for(input_text):
  """
    Calls the two functions as the 2-step process to convert comma to point in numbers in text
  """
  # Step 1
  midtext = step1_remove_thousands_point_sep_in_numbers_via_re(input_text)
  # Step 2
  return step2_convert_commasep_to_pointsep_in_numbers_via_re(midtext)


def adhoctests():
  input_text = '3,14 23.42 0,123 00,732 15 1'
  result = convert_decimalplace_comma_to_point_via_re_for(input_text)
  print('input_text', input_text)
  print('convert_decimalplace_comma_to_point_via_re_for() result', result)
  extracted_numbers = []
  for str_n in result.split(' '):
    try:
      n = float(str_n)
      extracted_numbers.append(n)
    except ValueError:
      continue
  print('extracted_numbers', str(extracted_numbers))


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctests()
