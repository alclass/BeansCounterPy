"""
lib/finfs/indices/indices_fetch_n_fs.py

import lib.finfs.indices.indices_fetch_n_fs as ipfs  # ipfs.ipca_for_refmonth
"""
import decimal
import datetime
import lib.finfs.indices.ipca.ipca_api_fetcher_n_updater as fet  # fet.read_n_get_json_ipca_monthlyindices_via_file_for_year()
import lib.datesetc.refmonth_fs as rmfs
import lib.finfs.indices.ipca.ipca_data as ipca
import lib.finfs.indices as init
IPCA = init.IPCA


class JsonFileIpcaRetriever:
  """
  Stores (for the object's scope) and retrieves IPCA data

  If a month's index is asked, the whole 12 months in its year are 'cached',
    this is because the data jsonfiles are yearly.

  Another important point is that the indices in the JSON files are 'percent',
    so to form a decimal ipca it must be divided by 100.
  """

  def __init__(self):
    self.month_n_ipcapct_dict = {}

  def fetch_ipca_percent_for_refmonth(self, refmonth):
    if refmonth not in self.month_n_ipcapct_dict:
      pdict = get_ipcas_via_jsonfile_for_year(refmonth.year)
      self.month_n_ipcapct_dict.update(pdict)
    return self.month_n_ipcapct_dict[refmonth]

  def fetch_ipcadec_for_refmonth(self, refmonth):
    """
    The ipca indices stores in the JSON files are expressed as percent numbers.
    Because of that, they must be divided by 100 to 'form' ipca_dec (its decimal number).
    """
    ipca_pct = self.fetch_ipca_percent_for_refmonth(refmonth)
    return ipca_pct / 100.0

  def get_all_monthly_ipcapct_between_refmonths(self, inirefmonth, finrefmonth):
    for refmonth in rmfs.generate_monthrange(inirefmonth, finrefmonth):
      ipca_idx = self.fetch_ipca_percent_for_refmonth(refmonth)
      scrmsg = f"refmonth={refmonth.strftime('%Y-%m')} | ipca_idx={ipca_idx}%"
      print(scrmsg)

  def process(self):
    inirefmonth, finrefmonth = '2020-01', '2024-12'
    self.get_all_monthly_ipcapct_between_refmonths(inirefmonth, finrefmonth)
    return


def get_ir_incrfactor_for_mora_w_iridx_n_expo(ir_idx, exponent):
  """
  Returns the multiplier for the (mora) Interest Rate (ir) calculation
    based on an index (ir_idx) and an exponent
    (this is independent on the duration time or cycle, which might be anyone in the caller)

  Acronyms:
    ir -> interest rate
    ir idx -> interest rate index
    incrfactor -> interest rate multiplier for finding the 'incr' (increment factor)
  """
  intermediate = (1 + ir_idx) ** exponent
  multiplier = intermediate - 1
  return multiplier


def find_ipca_corrmonet_for_month_via_pyfile(refmonth, idxname):
  if idxname == IPCA:
    return get_ipca_for_refmonth_via_pyfile(refmonth)
  return None


def get_ipca_for_refmonth_via_pyfile(refmonth):
  """
  A série histórico pode ser baixada xls-zipada de:
    https://ftp.ibge.gov.br/Precos_Indices_de_Precos_ao_Consumidor/IPCA/Serie_Historica/ipca_SerieHist.zip
  """
  year = refmonth.year
  month = refmonth.month
  monthly_indices = ipca.data_2019_2026[year]
  idx = monthly_indices[month-1]
  # idx is represented as %, so it's needed to divide it by 100
  idx = idx / 100
  return idx


def fetch_ipcadec_via_jsonfile_for_refmonth(refmonth: datetime.date) -> decimal.Decimal | None:
  year = refmonth.year
  yeardict = fet.read_n_get_json_ipca_monthlyindices_via_file_for_year(year)
  try:
    str_ipca = yeardict[refmonth]
    ipca_pct = float(str_ipca)
    ipca_pct_by_100 = ipca_pct / 100.0
    ipca_dec = decimal.Decimal(ipca_pct_by_100)
    return ipca_dec
  except KeyError:
    pass
  return None


def get_ipcas_via_jsonfile_for_year(year):
  return fet.read_n_get_json_ipca_monthlyindices_via_file_for_year(year)


def adhoctest1():
  """
  """
  refmonth = '2025-03'
  refmonth = rmfs.make_refmonth_or_raise(refmonth)
  monthly_ipca = fetch_ipcadec_via_jsonfile_for_refmonth(refmonth)
  scrmsg = f"refmonth={refmonth} | monthly_ipca = {monthly_ipca}"
  print(scrmsg)
  refmonth = '2026-05'
  refmonth = rmfs.make_refmonth_or_raise(refmonth)
  monthly_ipca = fetch_ipcadec_via_jsonfile_for_refmonth(refmonth)
  scrmsg = f"refmonth={refmonth.strftime('%Y-%m')} | ipca = {monthly_ipca}"
  print(scrmsg)
  retr = JsonFileIpcaRetriever()
  retr.process()


def adhoctest2():
  pass


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
