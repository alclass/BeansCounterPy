#!/usr/bin/env python3
"""
art/immeub/cdutra/rent/model_f_billing.py

"""
import lib.datesetc.datefs as dtfs
from collections import namedtuple
import datetime
import art.immeub.rent.iptu_mdl as iptu_m
DEFAULT_MUNICIPIONAME = 'Rio de Janeiro - RJ'
reais_baserent = 'reais_baserent'
cond_tariff = 'cond_tariff'
iptu_obj = 'iptu_obj'
fire_comb_obj = 'fire_comb_obj'
monthlyprice_maincomponents_namedtuple = namedtuple(
  'nt_monthlyprice_maincomponents_namedtuple',
  ['reais_baserent', 'cond_tariff', 'iptu_obj', 'fire_comb_obj']
)


class PriceItem:

  def __init__(self,
     coditem=None,
     seqitem=None,
     refyear=None,
     refmonth=None,
     refdate=None,
     price=None,
     cotas=None,
     b_inrefcycle=None,
     n_cota=None,
     totalcotas=None,
     ptype=None,
     descr_line1=None,
     descr_line2=None,
  ):
    self.coditem = coditem
    self.seqitem = seqitem
    # either refyear, refmonth or refdate
    self.refyear = refyear
    self.refmonth = refmonth
    self.refdate = refdate
    self.price = price
    self.b_inrefcycle = b_inrefcycle or False,
    self.n_cota = n_cota,
    self.totalcotas = totalcotas,
    self.type = ptype or 'mensal',
    self.descr_line1 = descr_line1,
    self.descr_line2 = descr_line2

  def __str__(self):
    outstr = f"""
    {self.coditem}
    {self.seqitem}
    {self.refyear} 
    {self.refmonth}
    {self.refdate}
    {self.price}
    {self.b_inrefcycle}
    {self.n_cota}
    {self.totalcotas}
    {self.type}
    {self.descr_line1}
    {self.descr_line2}
    """
    return outstr


class RentBiller:

  def __init__(
      self, immeub_code, price_components,
      refmonth, refyear, refdate,
    ):
    self.immeub_code = immeub_code
    self.price_components = price_components
    self.price_dict = {}
    # either refyear, refmonth or refdate
    self.refyear = refyear
    self.refmonth = refmonth
    self.refdate = refdate
    self.treat_attrs()

  @property
  def recycle(self):
    if self.refmonth:
      return self.refmonth
    if self.refdate:
      return self.refdate
    return self.refyear

  def treat_attrs(self):
    """
      self.price_components[reais_baserent]
    """
    if isinstance(self.price_components, type(namedtuple)):
      errmsg = f"Error: price components {self.price_components} should be the namedtuple configurad, it's not."
      raise AttributeError(errmsg)

  def as_dict(self):
    """
    reais_baserent', 'cond_tariff', 'iptu_obj', 'fire_comb_obj'
    """
    pdict = {}
    try:
      pdict['reais_baserent'] = self.price_components.reais_baserent
      pdict['cond_tariff'] = self.price_components.cond_tariff
      pdict['iptu_obj'] = self.price_components.iptu_obj
    except AttributeError:
      pass
    return pdict

  def generate_refmonth_billing(self):
    outstr = f"""
    Cobrança Aluguel | Mês {self.refcycle}
    --------------------------------------------
    """
    return outstr


  def __str__(self):
    outstr = f"""RentBiller object
    {self.as_dict()}
    """
    return outstr


def adhoctest1():
  iptu_o = iptu_m.get_adhoc_iptu_obj()
  price_cmp = monthlyprice_maincomponents_namedtuple(
    reais_baserent=1000, cond_tariff=1200, fire_comb_obj=100, iptu_obj=iptu_o
  )
  biller = RentBiller(
    immeub_code=10,
    price_components=price_cmp,
  )
  print(biller)

  priceitem = PriceItem(
        coditem=None,
        seqitem=None,
        refyear=None,
        refmonth='2025-05',
        refdate=None,
        price=2000.0,
        b_inrefcycle=None,
        n_cota=None,
        totalcotas=None,
        ptype=None,
        descr_line1=None,
        descr_line2=None,
    )
  print(priceitem)



def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  adhoctest()
  pass
  """
  adhoctest1()
  # adhoctest2()
  process()
