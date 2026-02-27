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


class Extractor:

  def __init__(self, basefolderpath=None):
    self.basefolderpath = basefolderpath or Path(os.getcwd())
    self.curr_dirpath = None
    self.dates_n_prices_list = []
    self.total_price = 0.0

  @property
  def middlepath(self):
    """
    self.curr_dirpath, _, filenames in os.walk(self.basefolderpath):
    """
    _middlepath = self.curr_dirpath[len(self.basefolderpath):]
    _middlepath = _middlepath.lstrip(os.sep)
    return _middlepath

  def extract_prices_in_files(self, filenames):
    for fn in filenames:
      _, dotext = os.path.splitext(fn)
      if dotext not in ['.ods', '.xlsx']:
        continue
      # [same as alg-version] price = extr.extract_number_after_its_prefixing_chars(fn)
      # price = extr.extract_price_wi_str_re_version(fn)
      price = extr.extract_price_wi_str_alg_version(fn)
      try:  # if isinstance(price, [int, float]):
        self.total_price += price
      except TypeError:
        pass
      pdate = extr.extract_date_at_the_beginning_of_str(fn)
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
    for tupl in self.dates_n_prices_list:
      pdate, price = tupl
      if not price:
        continue
      seq += 1
      print(seq, pdate, price)
    scrmsg = f"Total price: {self.total_price:7.2f}"
    print(scrmsg)
    avrg =  self.total_price / seq
    scrmsg = f"Average: {avrg:7.2f}"
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
