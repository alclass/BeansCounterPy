#!/usr/bin/env python3
"""
BeansCounter:
  lib/re/refunctions.py
    Contains text tranforming functions using regular expressions

In particular, the functions:

  1  step1_remove_thousands_point_sep_in_numbers_via_re(input_text):
  2  step2_convert_commasep_to_pointsep_in_numbers_via_re(input_text):

are used to convert texts with decimal place comma marker to those with the point marker instead.
"""
import re
point_decimal_place_compiled_re = re.compile(r'(?<=\d)\.(?=\d)')
comma_decimal_place_compiled_re = re.compile(r'(?<=\d),(?=\d)')
commanumber_regex = re.compile(r'(\d+,*\d*)')


def is_str_a_comma_sep_decimalplace_number(strnumber):
  match = commanumber_regex.match(strnumber)
  if not match:
    return False
  captured = match.group(1)
  if len(captured) == len(strnumber):
    return True
  return False


class AutoFindCommaPointNumberTransformer:
  """
  This class automatically finds whether a number is:
    a) a decimal-place-comma-separated
    b) or a decimal-place-point-separated
  Upon finding it, it transforms one into another.

  One use hypothesis for this class is when dealing with data text that
    contains numbers 'located' with comma separated decimal places
    and these must be transformed to its point separated decimal places format
    to, then, be 'cast' into 'native' numbers (basically int's, float's or double's)

  Noticing:
    Output:
      a) a transform to a point-sep number will also make it a float (instead of str)
      b) a transform to a comma-sep number will leave it as str
    Input:
      a) a comma-sep number input is 'naturally' a string (str)
        (a number in the computer, if it has decimal places, is always represented with point)
      b) a point-sep number may enter either as a string or a float
         (or something that is 'stringable',
          though number_fr (number from), if str, will be 'cast' to float internally in the class)
  """

  def __init__(self, number_fr):
    self.input_as_comma_decplace_number = None
    self.number_fr = number_fr
    self.number_to = None
    self.find_out_comma_or_point_convert_or_raise()
    self.process()

  def find_out_comma_or_point_convert_or_raise(self):
    # step 1: if it's float-convertable, deal done, if not, move on
    try:
      _ = float(self.number_fr)
      self.input_as_comma_decplace_number = False
      return
    except (TypeError, ValueError):
      pass
    self.find_out_it_is_a_commadecplacenumber_or_raise()

  def find_out_it_is_a_commadecplacenumber_or_raise(self):
    # now it should be a comma decplace number
    strnumber = self.number_fr
    if strnumber is None:
      errmsg = "Please, enter a valid comma number for comma-point transformation."
      raise ValueError(errmsg)
    strnumber = str(strnumber)
    if '.' in strnumber:
      # at this point in code, '.' (dot) can only be a thousand marker
      if ',' not in strnumber:
        # oh, oh, a comma, at least, should be there, it's not, raise ValueError
        if not isinstance(strnumber, float):
          errmsg = (f"Error: cannot transform '{strnumber}' to point number"
                    f" due to ambiguity in its dots or commas")
          raise ValueError(errmsg)
    # count dots
    dots = list(filter(lambda c: c == '.', strnumber))
    if len(dots) > 1:
      errmsg = (f"Error: cannot transform comma number {strnumber} to point number"
                f" due to having more than one dot")
      raise ValueError(errmsg)
    points = list(filter(lambda c: c == ',', strnumber))
    if len(points) > 1:
      errmsg = (f"Error: cannot transform comma number {strnumber} to point number"
                f" due to it having more than one point")
      raise ValueError(errmsg)
    bool_res = is_str_a_comma_sep_decimalplace_number(strnumber)
    if not bool_res:
      errmsg = (f"Error: cannot transform comma number {strnumber} to point number"
                f" due to it not being formed under the convention numbers comma plus optional numbers")
      raise ValueError(errmsg)
    # right-strip commas (to avoid numbers ending with comma and no more numbers following)
    strnumber = strnumber.rstrip(',')
    self.number_fr = strnumber
    self.input_as_comma_decplace_number = True

  def treat_dot_number_fr(self):
    try:
      _ = float(self.number_fr)
    except TypeError:
      errmsg = (f"Error: cannot transform point number {self.number_fr} to comma str number"
                f" due to it not passing through the float() function")
      raise ValueError(errmsg)

  def convert_pointdecimalplacenumber_to_strcommanumber(self):
    self.number_fr = float(self.number_fr)
    str_number_to = str(self.number_fr)
    self.number_to = str_number_to.replace('.', ',')

  def convert_commadecimalplacenumber_to_pointnumber_via_re_for(self):
    str_number_to = convert_decimalplace_comma_to_point_via_re_for(self.number_fr)
    self.number_to = float(str_number_to)

  def process(self):
    if self.input_as_comma_decplace_number:
      self.convert_commadecimalplacenumber_to_pointnumber_via_re_for()
    else:
      self.convert_pointdecimalplacenumber_to_strcommanumber()

  @property
  def marker_which_numbertype_from_to(self):
    point_number = 'point-number (.)'
    comma_number = 'comma-number (,)'
    marker = 'Transforming {_from} to {_to}'
    if self.input_as_comma_decplace_number:
      return marker.format(_from=comma_number, _to=point_number)
    return marker.format(_from=point_number, _to=comma_number)

  def __str__(self):
    outstr = f"""{self.__class__.__name__}
    {self.marker_which_numbertype_from_to}
    number from = {self.number_fr} ({type(self.number_fr)}) | number to = {self.number_to} ({type(self.number_to)})"""
    return outstr


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
    Calls the two functions via a 2-step process to convert
      a comma decplace strnumber (singular or plural)
      to a point decplace number (singular or plural)
    Obs: this can be done plurally (i.e., to more than one number separated by spaces)
      because it uses regex
  """
  # Step 1
  midtext = step1_remove_thousands_point_sep_in_numbers_via_re(input_text)
  # Step 2
  return step2_convert_commasep_to_pointsep_in_numbers_via_re(midtext)


def adhoctest1():
  input_text = '3,14 23.42 0,123 00,732 15 1'
  result = convert_decimalplace_comma_to_point_via_re_for(input_text)
  print('input_text', input_text)
  print('convert_commadecimalplacenumber_to_pointnumber_via_re_for() result', result)
  extracted_numbers = []
  for str_n in result.split(' '):
    try:
      n = float(str_n)
      extracted_numbers.append(n)
    except ValueError:
      continue
  print('extracted_numbers', str(extracted_numbers))


def adhoctest2():
  """
  number_fr = '3,14'
  trans = CommaPointNumberTransformer(number_fr)
  print(trans)
  boores = is_str_a_comma_sep_decimalplace_number(number_fr)
  print(number_fr, '|', boores)
  """
  number_fr = '3,'
  trans = AutoFindCommaPointNumberTransformer(number_fr)
  print(trans)
  number_fr = '3.14'
  trans = AutoFindCommaPointNumberTransformer(number_fr)
  print(trans)
  number_fr = '3'
  trans = AutoFindCommaPointNumberTransformer(number_fr)
  print(trans)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest2()
