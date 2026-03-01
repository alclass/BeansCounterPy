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
import string
from pathlib import Path
import sys
import re
import lib.texts.extractors as extr  # extr.extract_number_after_its_prefixing_chars
import collections as coll
datepricent = coll.namedtuple('dateprice', ['date', 'seq', 'price'])
restrdate = r"^(?P<date>\d{4}\-\d{2}\-\d{2})"
recmpdate = re.compile(restrdate)
# restrprice = r"(?<=\s)\d+(?:\.\d+)?(?=\s)"
# restrprice = r"\s{1}ML(?P<price>\d+?\,d{2}){1}\s{1}"
restrprice = r" [ML](?P<price>\d+\,\d{2}) "
recmpprice = re.compile(restrprice)
default_basefolder = (
  "/media/friend/OurD SSD 1Tb D1/OurDocs/Biz OD/Compras OD/Lojas Virtuais CmprOD/"
  "MercLivr CmprOD/ano a ano compras MercLivr OD"
)


def get_dates_payment_seqorder_or_1(phrase):
  """
  The order of payment is organized by a letter after the beginning date.

  Examples:
    a) an example with only one payment on date:
      "2026-02-28 bla foo bar.ods"

    b) an example with more than one payment on date:
      "2026-03-01a bla foo bar.ods"
      "2026-03-01b bla foo bar.ods"
      "2026-03-01c bla foo bar.ods"
  """
  try:
    c = phrase[10]
    if c == ' ':
      return 1
    idx = string.ascii_lowercase.index(c)
    return idx+1
  except (IndexError, TypeError, ValueError):
    pass
  return 1


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

  default_extract_method_name = 'regex'

  def __init__(self, basefolderpath=None, extract_method_name=None):
    self.basefolderpath = basefolderpath or Path(os.getcwd())
    self.curr_dirpath = None
    self.nt_dateprice_list = []
    self.total_price = 0.0
    self.extract_method_name = extract_method_name or self.default_extract_method_name

  @property
  def middlepath(self):
    """
    self.curr_dirpath, _, filenames in os.walk(self.basefolderpath):
    """
    strpath = f"{self.basefolderpath}"
    _middlepath = self.curr_dirpath[len(strpath):]
    _middlepath = _middlepath.lstrip(os.sep)
    return _middlepath

  def extract_dateprice_nt_fr_filenames(self, filenames):
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
      seq = get_dates_payment_seqorder_or_1(fn)
      date_seq_n_price = datepricent(pdate, seq, price)
      print(date_seq_n_price)
      self.nt_dateprice_list.append(date_seq_n_price)

  def traverse_dirs(self):
    for self.curr_dirpath, _, filenames in os.walk(self.basefolderpath):
      print('@', self.middlepath)
      self.extract_dateprice_nt_fr_filenames(filenames)

  def process(self):
    self.traverse_dirs()
    self.report()

  def report(self):
    seq = 0
    n_prices = len(self.nt_dateprice_list)
    for nt in self.nt_dateprice_list:
      if not nt.price:
        continue
      seq += 1
      print(nt.date, nt.seq, nt.price)
      # print(nt)
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
  if basefolderpath is None:
    basefolderpath = default_basefolder
  scrmsg = f"Parameter entered: {basefolderpath}"
  print(scrmsg)
  extractor = Extractor(basefolderpath=basefolderpath)
  extractor.process()


if __name__ == '__main__':
  process()
