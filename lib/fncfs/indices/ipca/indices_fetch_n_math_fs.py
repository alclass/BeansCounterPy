"""
lib/fncfs/indices/indices_fetch_n_math_fs.py
  Contains monetary correction functions.
  At this time, particularly functions for fetching (db-cached or via web-API) monthly IPCA's.

"""
from decimal import Decimal
import datetime
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fmath  # fmath.get_ir_incrfact_f_mora_w_idx_n_expo
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as fncach  # fncach.IpcaAPICacherRetriever


def fetch_ipcadec_v_cacher_f_refmonth(refmonth: datetime.date) -> Decimal | None:
  """
  Fetches a monthly ipca (as a decimal number, not percentual)
    via the 'cacher' object.

  The 'cacher' (@see its module) looks up first the monthly ipca in local JSON files.
  If not found in these lcoal files,
    it tries a web-API fetch, if successful, both retrieves it
    and saves it (caches) to its correspond local JSON file.
  """
  refmonth = rmfs.make_refmonth_or_raise(refmonth)
  ipcacacher = fncach.IpcaAPICacherRetriever()
  ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth(refmonth)
  return ipca_dec


def calc_morafact_n_ipca_w_1refm_2ir_3monthduration(
    refmonth: datetime.date | str, ir_dec: float | None = None, mduration: float | None = None
  ) -> tuple[Decimal | None, Decimal | None]:
  """
  Parameters:
  Input:
      refmonth (required): is the month-reference, it's a datetime.date with day=1,
        it may come in as a string
      ir_dec (optional): if any, is the 'interest rate' part (aliquota)
        to be added to ipca
        default: 0.0
      mduration: is the time elapsed in 'months'
        default: 1.0
    Output:
      multiplier: the multiplier factor the one that is applied to 'initial montant'
      ipca_dec: if ipca index for refmonth
  """
  refmonth = rmfs.make_refmonth_or_raise(refmonth)
  ir_dec = 0.0 if ir_dec is None else ir_dec
  ir_dec = Decimal(ir_dec)
  ir_dec = Decimal(ir_dec)
  mduration = 1.0 if mduration is None else mduration
  mduration = Decimal(mduration)
  ipca_dec = fetch_ipcadec_v_cacher_f_refmonth(refmonth)
  if ipca_dec is None:
    return None, None
  ipca_dec = Decimal(ipca_dec)
  ipca_plus_ir = ipca_dec + ir_dec
  multiplier = fmath.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(ipca_plus_ir, mduration)
  return multiplier, ipca_plus_ir


def adhoctest1():
  """
  """
  refmonth = '2025-07'
  multiplier, ipca_dec = calc_morafact_n_ipca_w_1refm_2ir_3monthduration(refmonth)
  scrmsg = f"refmonth={refmonth} | duration default to 1 month"
  print(scrmsg)
  scrmsg = f"Calc IPCA multiplier for refmonth={refmonth} | ipca mult = {multiplier}, ipca_dec = {ipca_dec}"
  print(scrmsg)


def adhoctest2():
  refmonth = '2025-03'
  refmonth = rmfs.make_refmonth_or_raise(refmonth)
  monthly_ipca = fetch_ipcadec_v_cacher_f_refmonth(refmonth)
  scrmsg = f"refmonth={refmonth} | monthly_ipca = {monthly_ipca}"
  print(scrmsg)
  refmonth = '2026-05'
  refmonth = rmfs.make_refmonth_or_raise(refmonth)
  monthly_ipca = fetch_ipcadec_v_cacher_f_refmonth(refmonth)
  scrmsg = f"refmonth={refmonth.strftime('%Y-%m')} | ipca = {monthly_ipca}"
  print(scrmsg)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  adhoctest2()
  """
  adhoctest1()
