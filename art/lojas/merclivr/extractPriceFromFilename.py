#!/usr/bin/env python3
"""
art/lojas/merclivr/extractPriceFromFilename.py
  Extracts ML price from its filenames.

Explanation:
  Every MercadoLilvre purchases leave a spreedsheet file
  having in its name the total price.
  This script walks up ML folders and extracts these prices.

  TO INVESTIGATE:
    a) with the algo version, total price results in 26447.76
    b) with the re version, total price results in 26031.22
"""
import datetime
import os
from pathlib import Path
import sys
import re
import lib.texts.extractors as extr  # extr.extract_number_after_its_prefixing_chars
restrdate = r"^(?P<date>\d{4}\-\d{2}\-\d{2})"
recmpdate = re.compile(restrdate)
# restrprice = r"(?<=\s)\d+(?:\.\d+)?(?=\s)"
# restrprice = r"\s{1}ML(?P<price>\d+?\,d{2}){1}\s{1}"
restrprice = r" [ML](?P<price>\d+\,\d{2}) "
recmpprice = re.compile(restrprice)


class ExtractMethod:
  regex = 1
  stralgo = 2
  method_names = ['regex', 'stralgo']
  method_names_dict = {
    1: 'regex',
    2: 'stralgo',
  }

  def __init__(self, method_number):
    self.method_number = method_number

  @property
  def method_name(self):
    return self.method_names_dict[self.method_number]

  @classmethod
  def valid_method_numbers(cls):
    return [cls.regex, cls.stralgo]

  @classmethod
  def valid_method_objs(cls):
    objs = []
    for method_number in cls.valid_method_numbers():
      o = ExtractMethod(method_number)
      objs.append(o)
    return objs


class Extractor:

  def __init__(self, basefolderpath=None, extract_method_name=None):
    self.basefolderpath = basefolderpath or Path(os.getcwd())
    self.curr_dirpath = None
    self.dates_n_prices_list = []
    self.total_price = 0.0
    self.extract_method_name = extract_method_name

  @property
  def middlepath(self):
    """
    self.curr_dirpath, _, filenames in os.walk(self.basefolderpath):
    """
    strpath = f"{self.basefolderpath}"
    _middlepath = self.curr_dirpath[len(strpath):]
    _middlepath = _middlepath.lstrip(os.sep)
    return _middlepath

  def extract_prices_in_files(self, filenames):
    for fn in filenames:
      _, dotext = os.path.splitext(fn)
      if dotext not in ['.ods', '.xlsx']:
        continue
      # [same as alg-version] price = extr.extract_number_after_its_prefixing_chars(fn)
      if self.extract_method_name == 'regex':
        price = extr.extract_price_wi_str_re_version(fn)
      elif self.extract_method_name == 'stralgo':
        price = extr.extract_price_wi_str_alg_version(fn)
      else:
        errmsg = (
          f"There are only two extraction methods: 'regex' and 'stralgo'."
          f" The one given was {self.extract_method_name}"
        )
        raise ValueError(errmsg)
      try:  # if isinstance(price, [int, float]):
        price = round(price, 2)
        self.total_price += price
      except TypeError:
        pass
      pdate = extr.extract_date_at_the_beginning_of_str(fn)
      if not isinstance(pdate, datetime.date) or price is None:
        continue
      date_n_price = (pdate, price)
      print(pdate, price, self.total_price)
      self.dates_n_prices_list.append(date_n_price)

  def traverse_dirs(self):
    for self.curr_dirpath, _, filenames in os.walk(self.basefolderpath):
      print('@', self.middlepath)
      self.extract_prices_in_files(filenames)

  def process(self):
    self.traverse_dirs()
    self.report()

  def report(self):
    seq = 0
    n_prices = len(self.dates_n_prices_list)
    for tupl in self.dates_n_prices_list:
      pdate, price = tupl
      if not price:
        continue
      seq += 1
      print(seq, pdate, price)
    scrmsg = f"Total price: {self.total_price:7.2f}"
    print(scrmsg)
    avrg = 0.0
    if seq > 0:
      avrg = self.total_price / seq
    scrmsg = f"Average: {avrg:7.2f}"
    print(scrmsg)
    scrmsg = (
      f"'Method: {self.extract_method_name} | N_prices: {n_prices} |"
      f" Average: {avrg:7.2f} On folder: [{self.basefolderpath}]"
    )
    print(scrmsg)


def process():
  basefolderpath = None
  try:
    basefolderpath = sys.argv[1]
  except IndexError:
    pass
  scrmsg = f"Parameter entered: {basefolderpath}"
  print(scrmsg)
  extractor = Extractor(basefolderpath=basefolderpath)
  extractor.process()


if __name__ == '__main__':
  process()
