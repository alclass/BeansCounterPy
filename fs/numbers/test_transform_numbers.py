#!/usr/bin/env python3
""""
transform_numbers.py module
Mainly it transform the European number representation (dots for thousands and comma for decimal places)
  into Python's American-like format (just the dot for decimal place)
"""
import unittest
import fs.numbers.transform_numbers as trans  # .transform_european_stringnumber_to_pythonfloat


class TestTransformNumber(unittest.TestCase):

  def test_invert_strchars(self):
    pass

  def test_place_thousand_dots_in_number_as_strnumber(self):
    comma_str = '1,000,432.34'
    returned_point_str = trans.place_thousand_dots_in_number_as_strnumber(comma_str)
    expected_point_str = '1.000.432,34'
    self.assertEqual(expected_point_str, returned_point_str)

  def swap_thousandcommas_n_decplacecomma_to_europeanformat(self):
    pass

  def test_transform_european_stringnumber_to_pythonfloat(self):
    str_or_number = '1000432,34'
    returned_float = trans.transform_european_stringnumber_to_pythonfloat(str_or_number)
    expected_float = 1000432.34
    self.assertEqual(expected_float, returned_float)
