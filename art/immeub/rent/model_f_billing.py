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


class RentBiller:

  def __init__(self, immeub_code, price_components):
    self.immeub_code = immeub_code
    self.price_components = price_components
    self.price_dict = {}
    self.treat_attrs()

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
