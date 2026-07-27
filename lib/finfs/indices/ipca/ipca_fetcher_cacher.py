"""
lib/finfs/indices/ipca/ipca_fetcher_cacher.py
  Contains the main class that API-fetches monthly IPCA indices and caches them in local JSON files.

"""
import datetime
import decimal
from decimal import Decimal
import lib.datesetc.refmonth_fs as rmfs
import lib.finfs.indices.ipca.ipca_api_fetcher_n_updater as fet  # fet.write_jsonresponse_within_dates_to()
INT_IPCA_YEARS_IN_CACHE = 10


class IpcaAPICacherRetriever:
  """
  Stores (for the object's scope) and retrieves IPCA data

  import lib.finfs.indices.ipca.ipca_fetcher_cacher as ipcachache  $ ipcachache.IpcaAPICacherRetriever

  If a month's index is asked, the whole 12 months in its year are 'cached',
    this is because the data jsonfiles are yearly.

  Another important point is that the indices in the JSON files are 'percent',
    so to form a decimal ipca it must be divided by 100.

  Memory consumption:
  ===================

  Because IPCA data is memory 'light-weight',
    the object caches up to 10 years of IPCA in memory (it's a relatively small imprint).

  """

  def __init__(self):
    self.month_n_ipcapct_dict = {}
    self.fifo_years = []

  def add_n_manage_years_cache_size(self, year: int):
    if year in self.month_n_ipcapct_dict:
      if year not in self.fifo_years:
        self.fifo_years.insert(0, year)
    if len(self.fifo_years) > INT_IPCA_YEARS_IN_CACHE:
      removed_year = self.fifo_years.pop()
      del self.month_n_ipcapct_dict[removed_year]
    dictsize = len(self.month_n_ipcapct_dict)
    fifosize = len(self.fifo_years)
    scrmsg = f"""{__name__}
    input year = {year} | fifo_years = {self.fifo_years} | fifosize = {fifosize} | dictsize = {dictsize}
    """
    print(scrmsg)

  def update_year_ipcas_pct_dict(self, year, year_ipcas_pct_dict):
    if year not in self.month_n_ipcapct_dict:
      self.month_n_ipcapct_dict.update({year: year_ipcas_pct_dict})
    self.add_n_manage_years_cache_size(year)


  def fetch_ipcas_pct_fr_jsonfile_for_year(self, year: int, retrying: bool = False)\
      -> dict[datetime.date, decimal.Decimal] | None:
    scrmsg = f" {__name__} -> fetch_ipcas_pct_fr_jsonfile_for_year({year})"
    print(scrmsg)
    jsonexists = fet.does_jsonfile_for_year_ipcas_exist(year)
    if not jsonexists:
      fet.store_monthly_ipcas_to_jsonfile_for_year(year)
      if not retrying:
        return self.fetch_ipcas_pct_fr_jsonfile_for_year(year, retrying=True)
      errmsg = (f"Error: system failed to fetch and store local jsonfile for {year}."
                f" Please, check network or filesystem.")
      raise OSError(errmsg)
    monthly_ipcas_pct_in_year = fet.get_year_monthly_ipcas_pct_via_jsonfile(year)
    self.update_year_ipcas_pct_dict(year, monthly_ipcas_pct_in_year)
    if year not in self.month_n_ipcapct_dict:
      self.add_n_manage_years_cache_size(year)
    return monthly_ipcas_pct_in_year

  def fetch_ipcas_dec_fr_jsonfile_for_year(self, year: int) -> dict[datetime.date, decimal.Decimal] | None:
    year_ipcas_pct = self.fetch_ipcas_pct_fr_jsonfile_for_year(year)
    if year_ipcas_pct is None:
      return None
    year_ipcas_dec = {month: year_ipcas_pct[month] / Decimal(100.0) for month in year_ipcas_pct}
    return year_ipcas_dec

  def fetch_ipca_pct_fr_jsonfile_for_refmonth(self, p_refmonth: datetime.date | str) -> decimal.Decimal | None:
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    year = refmonth.year
    scrmsg = f" {__name__} -> fetch_ipca_pct_fr_jsonfile_for_refmonth({refmonth}) | {year}"
    print(scrmsg)
    year_ipcas_pct = self.fetch_ipcas_pct_fr_jsonfile_for_year(year)
    if year_ipcas_pct is None:
      return None
    return year_ipcas_pct[refmonth]

  def fetch_ipca_dec_fr_jsonfile_for_refmonth(self, p_refmonth: datetime.date | str) -> decimal.Decimal | None:
    """
    The ipca indices stores in the JSON files are expressed as percent numbers.
    Because of that, they must be divided by 100 to 'form' ipca_dec (its decimal number).
    """
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    ipca_pct = self.fetch_ipca_pct_fr_jsonfile_for_refmonth(refmonth)
    if ipca_pct is None:
      return None
    ipca_dec = ipca_pct / Decimal(100.0)
    scrmsg = f"refmonth = {refmonth} | ipca_dec = {ipca_dec}"
    print(scrmsg)
    return ipca_dec

  def fetch_ipca_pct_for_refmonth(self, p_refmonth):
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    return self.fetch_ipca_pct_fr_jsonfile_for_refmonth(refmonth)

  def fetch_ipca_dec_for_refmonth(self, p_refmonth):
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    return self.fetch_ipca_dec_fr_jsonfile_for_refmonth(refmonth)

  def get_all_monthly_ipcapct_between_refmonths(self, inirefmonth, finrefmonth):
    for refmonth in rmfs.generate_monthrange(inirefmonth, finrefmonth):
      ipca_idx = self.fetch_ipca_pct_for_refmonth(refmonth)
      scrmsg = f"refmonth={refmonth.strftime('%Y-%m')} | ipca_idx={ipca_idx}%"
      print(scrmsg)

  def process(self):
    inirefmonth, finrefmonth = '2020-01', '2024-12'
    self.get_all_monthly_ipcapct_between_refmonths(inirefmonth, finrefmonth)
    return


def adhoctest1():
  """
  """
  retr = IpcaAPICacherRetriever()
  for year in range(2002, 2026):
    refmonth = f'{year}-2'
    ipca_dec = retr.fetch_ipca_dec_for_refmonth(refmonth)
    scrmsg = f"refmonth={refmonth} | ipca_dec={ipca_dec}"
    print(scrmsg)


def process():
  """
  Calls the function that updates the monthly IPCA's for the current year.
    The user should accept/confer/confirm the screen-display
      to check that the year's JSON content may be file-written or not.
    It's an easy check because when an error returns,
      it's easily identified and the user should not confirm it if it either contains an error or is empty.

  TODO this checking might be automated in the future.
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
