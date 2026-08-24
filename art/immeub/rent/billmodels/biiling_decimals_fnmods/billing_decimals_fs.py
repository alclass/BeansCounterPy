#!/usr/bin/env python3
"""
  Contains functions related to decimals (decimal.Decimal) to billing item and payment numbers.

"""
from decimal import Decimal, ROUND_HALF_UP
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fm_mnts  # fm_mnts.sigfig()
CNV_N_DECIMAL_PLACES = 6  # Decimal's number of decimal places
CNV_N_SIGFIG = 18  # Decimal's number of digits both integers and fractions


def get_default_ndecplaces_n_nsigfig():
  return CNV_N_DECIMAL_PLACES, CNV_N_SIGFIG


def get_cnv_ndecplace_decmold_for_quantize(n_decplaces=None) -> Decimal:
  default_decplaces, _ = get_default_ndecplaces_n_nsigfig()
  if n_decplaces is None:
    n_decplaces = default_decplaces
  decmold = '0.' + '0' * (n_decplaces - 1) + '1'
  decdecmold = Decimal(decmold)
  return decdecmold


def remake_decimal_w_ndecplaces_n_nsigfig(dec: Decimal, n_sigfig=None, n_decplaces=None) -> Decimal:
  """
  n_sigfigs is set firstly.
  Then n_decplaces is set secondly.
  """
  if n_sigfig is None:
    _, n_sigfig = get_default_ndecplaces_n_nsigfig()
  dec = fm_mnts.sigfig(dec, n_sigfig)
  decdecmold = get_cnv_ndecplace_decmold_for_quantize(n_decplaces)
  dec = dec.quantize(decdecmold, rounding=ROUND_HALF_UP)
  return dec


def adhoctest1():
  n_decplaces, n_sigfig = get_default_ndecplaces_n_nsigfig()
  scrmsg = f"ndecplaces = {n_decplaces} | n_sigfig = {n_sigfig}"
  print(scrmsg)
  dec = Decimal('1234.56789')
  newdec = remake_decimal_w_ndecplaces_n_nsigfig(dec)
  print('dec =', dec, 'newdec', newdec)



def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
