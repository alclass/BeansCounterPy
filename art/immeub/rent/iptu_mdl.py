#!/usr/bin/env python3
"""
art/immeub/cdutra/rent/model_f_billing.py

"""
import lib.datesetc.datefs as dtfs
from collections import namedtuple
import datetime
DEFAULT_MUNICIPIONAME = 'Rio de Janeiro - RJ'
reais_baserent = 'reais_baserent'
cond_tariff = 'cond_tariff'
iptu_obj = 'iptu_obj'
fire_comb_obj = 'fire_comb_obj'
monthlyprice_maincomponents_namedtuple = namedtuple(
  'nt_monthlyprice_maincomponents_namedtuple',
  ['reais_baserent', 'cond_tariff', 'iptu_obj', 'fire_comb_obj']
)


class IPTU:

  def __init__(
      self, discounted_price_yearonce, ref_year=None, duedate_for_yearoncepay=None,
      parcelprice_ifmonthly=None, totalparcels_ifmonthly=None,
      b_is_yearonce_choosen=True, refmonth=None, duedate_for_monthpay=None,
      b_yearonce_payment_done=False, intsmonths_alreadypaid=None,
      municipioname=None
  ):
    self.discounted_price_yearonce = discounted_price_yearonce
    self.ref_year = ref_year
    self.duedate_for_yearoncepay = duedate_for_yearoncepay
    self.parcelprice_ifmonthly = parcelprice_ifmonthly
    self.totalparcels_ifmonthly = totalparcels_ifmonthly
    self.b_is_yearonce_choosen = b_is_yearonce_choosen or False
    self.refmonth = refmonth
    self.duedate_for_monthpay = duedate_for_monthpay
    self.intsmonths_alreadypaid = intsmonths_alreadypaid
    self.b_yearonce_payment_done = b_yearonce_payment_done
    self.municipioname = municipioname
    self.today = datetime.date.today()
    self.treat_attrs()

  def treat_attrs(self):
    try:
      self.ref_year = int(self.ref_year)
    except ValueError:
      self.ref_year = self.today.year
    self.duedate_for_yearoncepay = dtfs.make_refmonthdate_or_none(self.duedate_for_yearoncepay)
    if self.duedate_for_yearoncepay is None:
      self.duedate_for_yearoncepay = self.today
    self.refmonth = dtfs.make_refmonthdate_or_none(self.refmonth)
    if self.refmonth is None:
      self.refmonth = dtfs.make_refmonthdate_or_current(self.refmonth)
    self.duedate_for_monthpay = dtfs.make_duedate_or_thismonth_on_the_10th(self.duedate_for_monthpay)
    self.totalparcels_ifmonthly = self.totalparcels_ifmonthly or 10
    self.treat_intsmonths()
    self.municipioname = self.municipioname or DEFAULT_MUNICIPIONAME

  def treat_intsmonths(self):
    if not isinstance(self.intsmonths_alreadypaid, list):
      self.intsmonths_alreadypaid = []
      return
    self.intsmonths_alreadypaid = list(map(lambda i: int(i), self.intsmonths_alreadypaid))

  @property
  def is_refyear_iptu_paid(self):
    """
    Returns boolean True if iptu has been paid, otherwise returns False
      This property works with both modes: yearly or monthly
    """
    # the yearly mode is "seen" by flag b_yearonce_payment_done
    if self.b_is_yearonce_choosen:
      if self.b_yearonce_payment_done:
        return True
    # the monthly mode is "seen" when length of the months-paid list is equal to total months to pay
    if len(self.intsmonths_alreadypaid) == self.totalparcels_ifmonthly:
      return True
    return False

  @property
  def total_yearprice_ifmonthly(self):
    total_ifmonthly = None
    try:
      total_ifmonthly = self.parcelprice_ifmonthly * self.totalparcels_ifmonthly
    except ValueError:
      pass
    return total_ifmonthly

  @property
  def intsmonths_yet_topay(self):
    parcels_list = list(range(2, self.totalparcels_ifmonthly + 2))
    for n_month in self.intsmonths_alreadypaid:
      if n_month in parcels_list:
        parcels_list.remove(n_month)
    return parcels_list

  def mount_scrmsg_pagt_anual_efetuado(self):
    scrmsg_pagt_anual_efetuado = f'pagamentos mensais escolhidos em {self.totalparcels_ifmonthly} cotas'
    if self.b_is_yearonce_choosen:
      scrmsg_pagt_anual_efetuado = f"pagamento anual escolhido e a efetuar"
      if self.b_yearonce_payment_done:
        scrmsg_pagt_anual_efetuado = f"pagamento anual escolhido e efetuado"
    return scrmsg_pagt_anual_efetuado

  def __repr__(self):
    return str(self)

  def __str__(self):
    scrmsg_pagt_anual_efetuado = self.mount_scrmsg_pagt_anual_efetuado()
    outstr = f"""{self.__class__.__name__} object
    discounted_price_yearonce = {self.discounted_price_yearonce}
    ref_year = {self.ref_year}
    duedate_for_yearoncepay = {self.duedate_for_yearoncepay}
    parcelprice_ifmonthly = {self.parcelprice_ifmonthly}
    totalparcels_ifmonthly = {self.totalparcels_ifmonthly}
    b_is_yearonce_choosen = {self.b_is_yearonce_choosen}
    refmonth = {self.refmonth}
    duedate_for_monthpay = {self.duedate_for_monthpay}
    intsmonths_yet_topay = {self.intsmonths_yet_topay}
    intsmonths_alreadypaid = {self.intsmonths_alreadypaid} | {scrmsg_pagt_anual_efetuado}
    municipio = {self.municipioname}
    today = {self.today}
    is_refyear_iptu_paid = {self.is_refyear_iptu_paid}
    """
    return outstr


def get_adhoc_iptu_obj():
  in_iptu_obj = IPTU(
    ref_year=2025,
    discounted_price_yearonce=1000,
    duedate_for_yearoncepay='2025-02-10',
    b_yearonce_payment_done=True,
  )
  return in_iptu_obj


def adhoctest1():
  in_iptu_obj = get_adhoc_iptu_obj()
  print(in_iptu_obj)


def adhoctest2():
  price_cmp = monthlyprice_maincomponents_namedtuple(
    reais_baserent=1000, cond_tariff=1200, fire_comb_obj=100, iptu_obj=get_adhoc_iptu_obj()
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
