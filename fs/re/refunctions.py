#!/usr/bin/env python3
"""
fs/re/refunctions.py
  contains tranforming text functions using regular expressions

In particular, the functions:

  1  step1_convert_thousands_points_to_empty_in_text_via_regexp(input_text):
  2  step2_convert_comma_to_point_in_text_via_regexp(input_text):

are used to convert texts with decimal place comma marker to those with the point marker instead.
"""
import re
point_decimal_place_compiled_re = re.compile(r'(?<=\d)\.(?=\d)')
comma_decimal_place_compiled_re = re.compile(r'(?<=\d),(?=\d)')


def step1_convert_thousands_points_to_empty_in_text_via_regexp(input_text):
  """
  Step 1: remove all thousands points in numbers
          this will avoid their being wrongly seen as decimal points after the comma-decimal conversion next
  """
  output_text = point_decimal_place_compiled_re.sub('', input_text)
  return output_text


def step2_convert_comma_to_point_in_text_via_regexp(input_text):
  """
  Step 2: replace all comma decimal points to point ones in numbers
          notice that in Step 1 thousands points were removed (above)
  """
  output_text = comma_decimal_place_compiled_re.sub('.', input_text)
  return output_text


def convert_comma_to_point_in_numbers_via_regexp_for(input_text):
  """
    Calls the two functions as the 2-step process to convert comma to point in numbers in text
  """
  # Step 1
  midtext = step1_convert_thousands_points_to_empty_in_text_via_regexp(input_text)
  # Step 2
  return step2_convert_comma_to_point_in_text_via_regexp(midtext)


def adhoctests():
  pass


def process():
  pass


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
