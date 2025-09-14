#!/usr/bin/env python3
""""
BeansCounterPy_PrdPrj:
  lib/datesetc/datefs.py
Module with date & time (helper) functions
"""
import datetime

import art.prices.priceitem_cm as prit  # prit.PurchaseItem |


class ObramaxPurchase:

  def __init__(self, purchasedate):
    self.today = datetime.date.today()
    self.purchasedate = purchasedate or self.today
    self.purchaseitem = None
    self.purchaseitems = {}
    self.seq = 0

  def add(self, itemwprice, qty):
    self.seq += 1
    self.purchaseitem = prit.PurchaseItem(itemwprice, self.purchasedate, qty, seq=self.seq)
    self.purchaseitems[self.purchaseitem.itemwprice.sku] = self.purchaseitem

  def listitems(self):
    text = ''
    for sku in self.purchaseitems:
      purchaseitem = self.purchaseitems[sku]
      line = str(purchaseitem)
      text += line + '\n'
    return text

  def __str__(self):
    return self.listitems()


class TxtFromWksExtractor:

  def __init__(self, rofo_abspath=None):
    self.rofo_abspath = rofo_abspath


  def process(self):
    pass


def adhoctest():
  pass


def process():
  """
  """
  extractor = TxtFromWksExtractor()
  extractor.process()


if __name__ == '__main__':
  """
  adhoctest()
  pass
  """
  process()
