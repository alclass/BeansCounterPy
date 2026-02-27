#!/usr/bin/env python3
"""
art/lojas/merclivr/extractPriceFromFilename.py
  Extracts ML price from its filenames.

Explanation:
  Every MercadoLilvre purchases leave a spreedsheet file
  having in its name the total price.
  This script walks up ML folders and extracts these prices.
"""
import os
from pathlib import Path
import sys
import re
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

  def extract_prices_in_files(self, filenames):
    for fn in filenames:
      print(fn)
      match_o_date = recmpdate.match(fn)
      match_o_price = recmpprice.match(fn)
      if match_o_date:
        strdate = match_o_date.group('date')
        price = None
        if match_o_price:
          price = match_o_price.group('price')
        print('-'*40)
        print(strdate, price, '->', fn)

  def traverse_dirs(self):
    for self.curr_dirpath, _, filenames in os.walk(self.basefolderpath):
      print(self.curr_dirpath)
      self.extract_prices_in_files(filenames)

  def process(self):
    self.traverse_dirs()


def process():
  basefolderpath = None
  try:
    basefolderpath = sys.argv[1]
  except IndexError:
    pass
  extractor = Extractor(basefolderpath=basefolderpath)
  extractor.process()


if __name__ == '__main__':
  process()
