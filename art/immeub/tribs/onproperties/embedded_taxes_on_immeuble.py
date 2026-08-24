import datetime
import pydantic
from decimal import Decimal
import lib.datesetc.refmonth_fs as rmfs
FUNESBOM_SIGLA_UPPER = 'FUNESBOM'


class EmbeddedImmeubleTax(pydantic.BaseModel):
  """
  In this app, a tax(imposto) resides, in MongoDB (and in the equivalent class)
    inside immmeuble ( or location). That is, the location itself contains
    the information about taxes (either imposto, taxa or contributions).

  The (dict) object models the way the IPTU may be charged, that is, either one pays a whole year amount
  or pays a parceled monthly amount in months selected.

  The description below is for an 'embedded' object to the main Location instance.

  imm_nickname is not necessary because it's embedded in Immeuble
  (the embedded object is kept for 5 years in the corresponding Mongo doc)
  """
  sigla: str
  descr: str
  govlevel: str  # municipal | estadual | federal
  payment_year: int
  yearvalue: Decimal
  refmonth_beginning: datetime.date
  opted_monthly: bool = True
  n_parcels_if_opt_mon: int = 1
  monthvalue: Decimal = pydantic.Field(default_factory=lambda: None)

  @property
  def refyear(self) -> int:
    """
    The refyear for IPTU is its payment year.
    The refyear for Funesbom is the year before its payment year.
    """
    _refyear = self.payment_year
    if self.sigla.upper() == FUNESBOM_SIGLA_UPPER:
      _refyear = _refyear - 1
    return _refyear

  @property
  def descr_ente_ano(self):
    _descr=f'{self.descr} {self.govlevel} ref {self.refyear}'
    return _descr

  @property
  def n_parcels(self) -> int:
    return self.n_parcels_if_opt_mon if self.opted_monthly else 1

  @property
  def parcelvalue(self) -> Decimal:
    return self.monthvalue if self.opted_monthly else self.yearvalue

  @property
  def meses_a_pagar(self) -> list[datetime.date]:
    if not self.opted_monthly:
      return [self.refmonth_beginning]
    refmonths = rmfs.make_refmonth_list_fr_refmonth_plus_n_or_raise(self.refmonth_beginning, self.n_parcels)
    return refmonths

  def mk_line_meses_a_pagar(self) -> str:
    ostr = ""
    pt_mmmbaryyyy_refmonths = []
    for refmonth in self.meses_a_pagar:
      m3letter = rmfs.get_pt_3lettermonth_fr_date(refmonth)
      m3_n_year = f"{m3letter}/{refmonth.year}"
      pt_mmmbaryyyy_refmonths.append(m3_n_year)
    line_meses_a_pagar = ', '.join(pt_mmmbaryyyy_refmonths)
    return line_meses_a_pagar

  @property
  def yeartotal(self) -> Decimal:
    """
    As opted or available. For example, in IPTU yeartotal depends on opting monthly or year-once.
    """
    total = self.parcelvalue * self.n_parcels
    return total

  def mk_line_pay_option(self) -> str:
    return 'mensal' if self.opted_monthly else 'anual'

  def __str__(self):
    ostr = f"""
    Tributo: {self.sigla} | {self.descr_ente_ano} | total no ano: {self.yeartotal:.2f}
    opção pagt: {self.mk_line_pay_option()} | n parcelas = {self.n_parcels} | valor parcela = {self.parcelvalue:.2f}
    pagamento(s) no(s) mes(es): {self.mk_line_meses_a_pagar()}"""
    return ostr


def make_example_iptu_1():
  mkrm = rmfs.make_refmonth_or_raise
  emb_o = EmbeddedImmeubleTax(
    sigla='IPTU',
    descr='Imposto predial',
    govlevel='municipal',
    payment_year=2026,
    yearvalue=Decimal(1500),
    opted_monthly=True,
    n_parcels_if_opt_mon=10,
    refmonth_beginning=mkrm('2026-2'),
    monthvalue=Decimal(160),
  )
  # emb_o.opted_monthly = False
  return emb_o


def make_example_funesbom_1():
  mkrm = rmfs.make_refmonth_or_raise
  emb_o = EmbeddedImmeubleTax(
    sigla='Funesbom',
    descr='Taxa de incêndio',
    govlevel='estadual',
    payment_year=2026,
    yearvalue=Decimal(300),
    opted_monthly=False,
    n_parcels_if_opt_mon=1,
    refmonth_beginning=mkrm('2026-3'),
    # monthvalue=Decimal(300),
  )
  # emb_o.opted_monthly = False
  return emb_o


def adhoctest1():
  """
  """
  # emb_o = make_example_iptu_1()
  # print(emb_o)
  emb_o = make_example_funesbom_1()
  print(emb_o)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()