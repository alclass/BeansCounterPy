#!/usr/bin/env python3
""""
BeansCounterPy_PrdPrj:
  art/prices/priceitem_cm.py
This module contains the following classes:
  1 - ItemWOPrice: models an item good without its price
  2 - PriceItem: inherits from ItemWOPrice, it models an item good with its price
  3 - PurchaseItem: composes with PriceItem, it models an item good in a "purchase set"

The "purchase set" class, which models a purchase with various items, is not in this module.
"""
import datetime


class ItemWOPrice:

  def __init__(self, sku, description, unit_type=None, url=None):
    self.sku = sku
    self.description = description
    self.unit_type = unit_type
    self.url = url

  def __str__(self):
    outstr = f"""{self.__class__.__name__}
    sku = {self.sku} 
    description = {self.description} 
    unit_type = {self.unit_type} 
    url = {self.url}
    """
    return outstr


class ItemWPrice(ItemWOPrice):

  def __init__(
      self,
      sku, description,
      unitprice, pricedate=None, whosal_uprice=None, amount_f_whosalpri=None,
      unit_type=None, url=None,
    ):
    super().__init__(sku, description, unit_type, url)
    self.unitprice = unitprice
    self.pricedate = pricedate
    self.whosal_uprice = whosal_uprice
    self.amount_f_whosalpri = amount_f_whosalpri

  def get_unitprice_given_qty(self, qty):
    if self.whosal_uprice is None or self.amount_f_whosalpri is None:
      return self.unitprice
    if qty >= self.amount_f_whosalpri:
      return self.whosal_uprice
    return self.unitprice

  @classmethod
  def create_instance_w_itemwoprice(
      cls, itemwoprice, unitprice,
      pricedate=None, whosal_uprice=None, amount_f_whosalpri=None,
    ):
    obj = cls(
      sku=itemwoprice.sku,
      description=itemwoprice.description,
      unit_type=itemwoprice.unit_type,
      url=itemwoprice.url,
      unitprice=unitprice,
      pricedate=pricedate,
      whosal_uprice=whosal_uprice,
      amount_f_whosalpri=amount_f_whosalpri
    )
    return obj

  def __str__(self):
    outstr1 = super().__str__()
    outstr2 = f"""unitprice = {self.unitprice}
    pricedate = {self.pricedate}
    whosal_uprice = {self.whosal_uprice}
    amount_f_whosalpri = {self.amount_f_whosalpri}"""
    outstr = outstr1 + outstr2
    return outstr


class PurchaseItem:

  def __init__(
      self, itemwprice, purchasedate, qty=1, seq=None
    ):
    self.itemwprice = itemwprice
    self.purchasedate = purchasedate
    self.qty = qty
    self.seq = seq

  @property
  def unitprice(self):
    return self.itemwprice.get_unitprice_given_qty(self.qty)

  @property
  def totalitem(self):
    return self.qty * self.unitprice

  def __str__(self):
    seq = self.seq
    sku = self.itemwprice.sku
    dsc = self.itemwprice.description
    qty = self.qty
    untyp = self.itemwprice.unit_type
    upri = self.unitprice
    totalitem = self.totalitem
    outstr = f"{seq} | {sku} | {dsc} | {qty} | {untyp} | {upri} | {totalitem}"
    return outstr


def adhoctest():
  today = datetime.date.today()
  itemwoprice = ItemWOPrice(sku='010', description='cimento cp2', unit_type='saco50kg')
  itemwprice = ItemWPrice.create_instance_w_itemwoprice(
    itemwoprice=itemwoprice,
    unitprice=12,
    pricedate=today,
    whosal_uprice=11,
    amount_f_whosalpri=8
  )
  purchaseitem = PurchaseItem(
    itemwprice=itemwprice, purchasedate=today, qty=5, seq=1
  )
  print(purchaseitem)
  print('='*40)
  print(itemwprice)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  adhoctest()
  pass
  """
  adhoctest()
  process()
