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
# import os
# import sys
import art.lojas.merclivr.extractPriceFromFilename as extrM  # extrm.Extractor
default_basefolder = (
  "/media/friend/OurD SSD 1Tb D1/OurDocs/Biz OD/Compras OD/Lojas Virtuais CmprOD/"
  "MercLivr CmprOD/ano a ano compras MercLivr OD"
)


class ExtractorComparator:

  def __init__(self, basefolderpath=None):
    self.store_dict = {}
    self.dates_n_prices_list = []
    self.missing_dates_n_prices_list = []
    self.basefolderpath = basefolderpath or default_basefolder
    self.methodnames = extrM.ExtractMethod.method_names

  def fetch_by_extract_method(self):
    for method_o in extrM.ExtractMethod.valid_method_objs():
      extractor = extrM.Extractor(basefolderpath=self.basefolderpath, extract_method_name=method_o.method_name)
      extractor.process()
      dates_n_prices_list = extractor.nt_dateprice_list
      dates_n_prices_list.sort(key=lambda x: x[0])  # , reverse=True)
      self.store_dict[method_o.method_name] = dates_n_prices_list
      pass

  def remove_equals(self):
    """
    for tupl in regex_tuple_list:
      if tupl in stralgo_tuple_list:
        print('removing', tupl)
        regex_tuple_list.remove(tupl)
        stralgo_tuple_list.remove(tupl)

    """
    regex_tuple_list = self.store_dict['regex']
    stralgo_tuple_list = self.store_dict['stralgo']
    seq = 0
    for tupl in regex_tuple_list:
      if tupl not in stralgo_tuple_list:
        self.missing_dates_n_prices_list.append(tupl)
        seq += 1
        print(seq, 'missing', tupl)

  def show_size(self):
    """
      for tupl in dates_n_prices_list:
        print(tupl)
    """
    for i, method_name in enumerate(self.store_dict):
      seq = i + 1
      dates_n_prices_list = self.store_dict[method_name]
      scrmsg = f"{seq} n of dates-prices {len(dates_n_prices_list)}"
      print(scrmsg)

  def process(self):
    self.fetch_by_extract_method()
    self.remove_equals()
    self.report()

  def report(self):
    self.show_size()


def process():
  comparator = ExtractorComparator()
  comparator.process()


if __name__ == '__main__':
  process()
