"""
lib/fncfs/indices/ipca/ipca_fetcher_cacher.py
  Contains the main class that API-fetches monthly IPCA indices and caches them in local JSON files.

To import this:
  import lib.fncfs.indices.ipca.ipca_fetcher_cacher as fncach  # fncach.IpcaAPICacherRetriever


"""
import datetime
import decimal
import random
from decimal import Decimal
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.indices.ipca.ipca_api_fetcher_n_updater as fet  # fet.write_jsonresponse_within_dates_to()
INT_IPCA_YEARS_IN_CACHE = 10
NUMBER_OF_FETCH_TRIES = 3


def fetch_iridx_n_ipca_m_plus_i_w_refmonth_n_fix(
    refmonth: datetime.date, p_fix_ir_dec: Decimal | None = None, i: int = 1,
  ) -> tuple[Decimal, Decimal]:
  fix_ir_dec = p_fix_ir_dec or DEFAULT_FIX_IR_DEC
  ipcacacher = IpcaAPICacherRetriever()
  ipca_dec = ipcacacher.fetch_ipca_dec_for_refmonth_minus_n(refmonth, i)
  if ipca_dec is None:
    ipca_dec = DECIMAL_ZERO
  ir_idx = fix_ir_dec + ipca_dec
  return ir_idx, ipca_dec


def trnsp_refmonth_n_ipcadec_fr_dict_to_tuplelist(pdict):
  """
  Transposes a {refmonth: ipcadec} dictlist into a tuplelist (refmonth, ipcadec).
  It also completes missing months (in-between gaps) if there are any.
  The missing months will receive 'None' in its corresponding ipca_dec 'dimension'.

  Example:
  ========
    Suppose input is:
     pdict = {
       '2025-1': 0.0069,
       '2025-3': 0.0059,
       '2025-5': 0.0096,
     }
    Then, output should be:
     tuplelist = [
       ('2025-1', 0.0069),
       ('2025-2', None),
       ('2025-3', 0.0059),
       ('2025-4', None),
       ('2025-5', 0.0096),
     ]
  """
  # 1 transform dictlist to tuplelist
  month_n_ipcadec_tuplelist = [(refmonth, pdict[refmonth]) for refmonth in pdict if pdict[refmonth] is not None]
  # 2 sort tuplelist by refmonth
  month_n_ipcadec_tuplelist.sort(key=lambda tpl: tpl[0])
  # 3 extract (just) refmonths from tuplelist
  refmonths = [tpl[0] for tpl in month_n_ipcadec_tuplelist]
  # 4 find, if any, missing refmonths within refmonths (a list)
  missing_refmonths = rmfs.pickup_refmonth_gaps_throughout_list(refmonths)
  if len(missing_refmonths) == 0:
    # 5 no gaps in-between, return
    return month_n_ipcadec_tuplelist
  # 5 there were gaps, create new tuples with ipca_dec None for the missing refmonths
  tuplist = []
  for missingrefmonth in missing_refmonths:
    tupl = (missingrefmonth, None)
    tuplist.append(tupl)
  # 6 join them together
  month_n_ipcadec_tuplelist += tuplist
  # 7 sort it again and return
  month_n_ipcadec_tuplelist.sort(key=lambda tpl: tpl[0])
  return month_n_ipcadec_tuplelist


class IpcaAPICacherRetriever:
  """
  Stores (for the object's scope) and retrieves IPCA (*) testdata.
    (*) IPCA is a Brazililan inflation index.

  Noting:

  1 - This class fetches the IPCA indices via its BCB web-API.
  2 - Every fetch also caches the IPCA testdata (month and index)
      in local JSON files.
  3 - Excepting when the year is still incomplete
      (that is, the currenty year), the whole 12 months
      in its year are 'cached' (that is, goes into a JSON file).
  4 - This class first looks up in the files,
      then it tries via the web-API.
  5 - (ATTENTION) the indices in the JSON files (as in the API)
      are 'percent', so to form a decimal ipca it must be divided by 100.
      (This class have methods with 'pct' (percent) and 'dec' (decimal) in their names.)

  Memory consumption:
  ===================

  Because IPCA testdata is memory 'light-weight',
    the object caches up to 10 years of IPCA in memory (it's a relatively small imprint).
    (It could be well more, 10 years testdata makes up a 'small footprint'.)

  import lib.fncfs.indices.ipca.ipca_fetcher_cacher as ipcachache  $ ipcachache.IpcaAPICacherRetriever
  """

  def __init__(self):
    self.month_n_ipcapct_dict = {}
    self.fifo_years = []
    self._ipca_oldest_refmonth_n_idx = None
    self._ipca_mostrecent_refmonth_n_idx = None

  @property
  def ipca_oldest_refmonth_n_idx(self):
    if self._ipca_oldest_refmonth_n_idx is None:
      self.find_n_set_ipca_oldest_n_newest_year_thru_json_cache()
    return self._ipca_oldest_refmonth_n_idx

  @property
  def ipca_mostrecent_refmonth_n_idx(self):
    if self._ipca_mostrecent_refmonth_n_idx is None:
      self.find_n_set_ipca_oldest_n_newest_year_thru_json_cache()
    return self._ipca_mostrecent_refmonth_n_idx

  def find_n_set_ipca_oldest_n_newest_year_thru_json_cache(self):
    oldest_n_newest_years = fet.find_ipca_oldest_n_newest_year_thru_json_cache()
    if oldest_n_newest_years is None:
      return
    iniyear = oldest_n_newest_years[0]
    finyear = oldest_n_newest_years[-1]
    iniyeartuplelist = self.retrieve_month_n_ipcadec_tuplelist_fo_year(iniyear)
    self._ipca_oldest_refmonth_n_idx = iniyeartuplelist[0]
    finyeartuplelist = self.retrieve_month_n_ipcadec_tuplelist_fo_year(finyear)
    self._ipca_mostrecent_refmonth_n_idx = finyeartuplelist[-1]

  def fetch_the_last_n_months_n_ipca(self, n):
    months_n_ipca_last_n = []
    refmonth, idx = self.ipca_mostrecent_refmonth_n_idx
    if refmonth is None or idx is None:
      return []
    months_n_ipca_last_n.append((refmonth, idx))
    previous_refmonth = refmonth
    while len(months_n_ipca_last_n) < n:
      refmonth = rmfs.make_refmonth_it_minus_n_or_none(previous_refmonth, 1)
      idx = self.fetch_ipca_dec_for_refmonth(refmonth)
      if idx is None:
        break
      months_n_ipca_last_n.append((refmonth, idx))
      previous_refmonth = refmonth
    return months_n_ipca_last_n

  def add_n_manage_years_cache_size(self, year: int):
    if year in self.month_n_ipcapct_dict:
      if year not in self.fifo_years:
        self.fifo_years.insert(0, year)
    if len(self.fifo_years) > INT_IPCA_YEARS_IN_CACHE:
      removed_year = self.fifo_years.pop()
      del self.month_n_ipcapct_dict[removed_year]
    dictsize = len(self.month_n_ipcapct_dict)
    fifosize = len(self.fifo_years)
    # scrmsg = f"""{__name__}
    # input year = {year} | fifo_years = {self.fifo_years} | fifosize = {fifosize} | dictsize = {dictsize}
    # """
    # print(scrmsg)

  def update_year_ipcas_pct_dict(self, year, year_ipcas_pct_dict):
    if year not in self.month_n_ipcapct_dict:
      self.month_n_ipcapct_dict.update({year: year_ipcas_pct_dict})
    self.add_n_manage_years_cache_size(year)

  def fetch_ipcas_pct_fr_jsonfile_for_year(
      self, year: int, nretries: int = 0
    ) -> dict[datetime.date, decimal.Decimal] | None:
    # scrmsg = f" {__name__} -> fetch_ipcas_pct_fr_jsonfile_for_year({year})"
    # print(scrmsg)
    jsonexists = fet.does_jsonfile_for_year_ipcas_exist(year)
    if not jsonexists:
      fet.fetch_n_store_monthly_ipcas_to_jsonfile_fo_year(year)
      if nretries <= 3:
        return self.fetch_ipcas_pct_fr_jsonfile_for_year(year, nretries=nretries+1)
      errmsg = (f"Error: system failed to fetch and store local jsonfile for {year}."
                f" Please, check network or filesystem. There were {nretries} retries.")
      raise OSError(errmsg)
    monthly_ipcas_pct_in_year = fet.get_year_monthly_ipcas_pct_via_jsonfile(year)
    self.update_year_ipcas_pct_dict(year, monthly_ipcas_pct_in_year)
    if year not in self.month_n_ipcapct_dict:
      self.add_n_manage_years_cache_size(year)
    return monthly_ipcas_pct_in_year

  def fetch_ipcas_dec_fr_jsonfile_for_year(self, year: int) -> dict[datetime.date, Decimal] | None:
    year_ipcas_pct = self.fetch_ipcas_pct_fr_jsonfile_for_year(year)
    if year_ipcas_pct is None:
      return None
    year_ipcas_dec = {month: year_ipcas_pct[month] / Decimal(100.0) for month in year_ipcas_pct}
    return year_ipcas_dec

  def retrieve_month_n_ipcadec_tuplelist_fo_year(
      self, year: int, ntries: int = 0
    ) -> list[tuple[datetime.date, Decimal | None]]:
    pdict = self.fetch_ipcas_dec_fr_jsonfile_for_year(year)
    if pdict is not None:
      # trnsp_refmonth_n_ipcadec_fr_dict_to_tuplelist()
      month_n_ipcadec_tuplelist = [(refmonth, pdict[refmonth]) for refmonth in pdict]
      month_n_ipcadec_tuplelist.sort(key=lambda tpl: tpl[0])
      return month_n_ipcadec_tuplelist
    # we have to web-API fetch it and retry reading from the cache
    fet.fetch_n_store_monthly_ipcas_to_jsonfile_fo_year(year)
    if ntries > NUMBER_OF_FETCH_TRIES:
      errmsg = f"Error: system failed to fetch and store local jsonfile for {year}."
      raise OSError(errmsg)
    return self.retrieve_month_n_ipcadec_tuplelist_fo_year(year, ntries=ntries+1)

  def fetch_ipca_pct_fr_jsonfile_for_refmonth(self, p_refmonth: datetime.date | str) -> decimal.Decimal | None:
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    year = refmonth.year
    # scrmsg = f" {__name__} -> fetch_ipca_pct_fr_jsonfile_for_refmonth({refmonth}) | {year}"
    # print(scrmsg)
    year_ipcas_pct = self.fetch_ipcas_pct_fr_jsonfile_for_year(year)
    if year_ipcas_pct is None:
      return None
    if refmonth in year_ipcas_pct:
      return year_ipcas_pct[refmonth]
    else:
      return None

  def fetch_ipca_dec_fr_jsonfile_for_refmonth(self, p_refmonth: datetime.date | str) -> decimal.Decimal | None:
    """
    The ipca indices stores in the JSON files are expressed as percent numbers.
    Because of that, they must be divided by 100 to 'form' ipca_dec (its decimal number).
    """
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    ipca_pct = self.fetch_ipca_pct_fr_jsonfile_for_refmonth(refmonth)
    if ipca_pct is None:
      return None
    ipca_dec = ipca_pct / 100
    scrmsg = f"refmonth = {refmonth} | ipca_dec = {ipca_dec}"
    print(scrmsg)
    return ipca_dec

  def fetch_ipca_pct_for_refmonth(self, p_refmonth, retry=False):
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    ipca_pct = self.fetch_ipca_pct_fr_jsonfile_for_refmonth(refmonth)
    if ipca_pct is None:
      if retry:
        return None
      # we have to web-API fetch it and retry reading from the cache
      fet.fetch_n_store_monthly_ipcas_to_jsonfile_fo_year(refmonth.year)
      return self.fetch_ipca_pct_for_refmonth(refmonth, retry=True)
    return ipca_pct

  def fetch_ipca_dec_for_refmonth(self, p_refmonth: datetime.date) -> decimal.Decimal | None:
    refmonth = rmfs.make_refmonth_or_raise(p_refmonth)
    ipca_pct = self.fetch_ipca_pct_for_refmonth(refmonth)
    if ipca_pct is None:
      return None
    ipca_dec = ipca_pct / 100
    ipca_dec = Decimal(ipca_dec)
    return ipca_dec

  def fetch_ipca_dec_for_refmonth_minus_n(self, p_refmonth: datetime.date, n: int) -> decimal.Decimal | None:
    refmonth = rmfs.make_refmonth_it_minus_n_or_none(p_refmonth, n)
    if refmonth is None:
      return None
    ipca_dec = self.fetch_ipca_dec_for_refmonth(refmonth)
    return ipca_dec

  def retrieve_all_monthly_ipcapct_between_refmonths(self, inirefmonth, finrefmonth):
    for refmonth in rmfs.generate_refmonths_from_2datemonthrange(inirefmonth, finrefmonth):
      ipca_idx = self.fetch_ipca_pct_for_refmonth(refmonth)
      scrmsg = f"refmonth={refmonth.strftime('%Y-%m')} | ipca_idx={ipca_idx}%"
      print(scrmsg)

  def process(self):
    inirefmonth, finrefmonth = '2020-01', '2024-12'
    self.retrieve_all_monthly_ipcapct_between_refmonths(inirefmonth, finrefmonth)
    return

  def __str__(self):
    ostr = f"""{self.__class__.__name__}
    ipca_oldest_refmonth_n_idx = {self.ipca_oldest_refmonth_n_idx}
    ipca_mostrecent_refmonth_n_idx = {self.ipca_mostrecent_refmonth_n_idx}
    """
    return ostr


def adhoctest1():
  """
  """
  retr = IpcaAPICacherRetriever()
  for year in range(2002, 2026):
    refmonth = f'{year}-2'
    ipca_dec = retr.fetch_ipca_dec_for_refmonth(refmonth)
    scrmsg = f"refmonth={refmonth} | ipca_dec={ipca_dec}"
    print(scrmsg)


def adhoctest2():
  refmonths = ['2025-1','2025-3','2025-5',]
  refmonths = map(lambda x: rmfs.make_refmonth_or_raise(x), refmonths)
  refmonths = list(refmonths)
  pdict = {}
  for refmonth in refmonths:
    rand_idx = random.randint(0, 100)
    idx = rand_idx / 100 / 100
    pdict[refmonth] = idx
  retlist = trnsp_refmonth_n_ipcadec_fr_dict_to_tuplelist(pdict)
  scrmsg = f"input {refmonths} | output {retlist}"
  print(scrmsg)


def adhoctest3():
  retriever = IpcaAPICacherRetriever()
  refmonths = ['2019-12','2015-3','2010-2',]
  inirefmonth, finrefmonth = refmonths[0], refmonths[-1]
  retriever.retrieve_all_monthly_ipcapct_between_refmonths(inirefmonth, finrefmonth)
  # scrmsg = f"input {inirefmonth} to {finrefmonth}| output {tuplelist}"
  # print(scrmsg)
  print(retriever)
  plist = retriever.fetch_the_last_n_months_n_ipca(3)
  print(plist)


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
  adhoctest1()
  process()
  """
  adhoctest3()
