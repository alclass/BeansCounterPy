"""
art/immeub/rent/billmodels/monthsmora_simulator.py
"""
import datetime
from decimal import Decimal
import pydantic
import typing
from dateutil.relativedelta import relativedelta
import art.immeub.rent.billmodels.billingcard_pydantic as bcmod  # bcmod.PydtcBillingCard
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.credeb_pkg.samemonthmora as moram  # moram.SameMonthMora
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as fncach  # fncach.IpcaAPICacherRetriever
import lib.fncfs.credeb_pkg.payment_processor as pproc
mkrm = rmfs.make_refmonth_or_raise
DEFAULT_FIX_IR_DEC = Decimal('0.02')
DECIMAL_ZERO = Decimal('0.00')
MORA_M_MINUS_N = 2  # notice it's 2 months prior from refmonth and 3 from paymonth


def mk_n_get_monthmora_w_1pproc_n_2todate(
      pprocessor: pproc.PaymentProcessor, todate: datetime.date,
  ) -> moram.SameMonthMora | None:
  if pprocessor.ongoing_date is None:
    # retrodate_ifinmora, if contract does not say differently, is the first day of the month
    pprocessor.ongoing_date = pprocessor.retrodate_ifinmora
  if pprocessor.ongoing_date >= todate:
    # the '=' means mora has already been counted
    # the '>' means mora has been counted and also that a payment happened on the last day of month
    # because at the method's end: self.ongoing_date = todate + relativedelta(days=1)
    # and if a payment happened on month's last dat, self.ongoing_date will be position on next month's first day
    # out of the 2 callers to this method, the second, add_closing_mora(), considers this
    # the first one throws an exception upon receiving None
    return None
  if pprocessor.ongoing_debt >= DECIMAL_ZERO:
    # case which an ongoing_credit might have occurred
    # notice this method is called by '2 clients'
    # one of them will throw an exception if it gets None
    # because this method should not be called under that condition
    # the second caller, add_closing_mora(), considers this
    return None
  ipca_cacher = fncach.IpcaAPICacherRetriever()
  # this is just to make refmonth (paymonth's previous month)
  refmonth = rmfs.make_refmonth_it_minus_n_or_raise(todate, 1)
  rm_minus_2 = rmfs.make_refmonth_it_minus_n_or_raise(refmonth, MORA_M_MINUS_N)
  ipca_dec = ipca_cacher.fetch_ipca_dec_for_refmonth(rm_minus_2)
  # noinspection bad-argument-type
  monthmora = moram.SameMonthMora(
    fromdate=pprocessor.ongoing_date,
    todate=todate,
    prevalue=pprocessor.ongoing_debt,  # this is negative
    fix_ir_dec=pprocessor.fix_ir_dec,
    var_ir_dec=ipca_dec,
    var_ir_sigla="IPCA",
  )
  pprocessor.ongoing_date = todate + relativedelta(days=1)
  return monthmora


class MonthsMoraSimulator(bcmod.PydtcBillingCard):
  """
  """
  billingcard: bcmod.PydtcBillingCard = pydantic.Field(exclude=True)
  projected_date: datetime.date = pydantic.Field(exclude=True, default_factory=lambda: datetime.date.today())
  pprocessor: typing.Optional[pproc.PaymentProcessor] = pydantic.Field(exclude=True, default_factory=lambda: None)
  monthmora: typing.Optional[moram.SameMonthMora] = None
  fix_ir_dec: Decimal = pydantic.Field(default_factory=lambda: DEFAULT_FIX_IR_DEC)

  def get_monthmora(self) -> moram.SameMonthMora:
    if self.monthmora is None:
      self.calc_projected_mora()
    if self.monthmora is None:
      errmsg = "Error: monthmora could not be created in mora-simulator."
      raise ValueError(errmsg)
    return self.monthmora

  @property
  def paymonth(self) -> datetime.date:
    _payrefmonth = rmfs.make_refmonth_or_raise(self.projected_date)
    return _payrefmonth

  def instantiate_n_get_payment_processor(self) -> pproc.PaymentProcessor:
    if self.pprocessor is not None:
      return self.pprocessor
    ongoing_debt = - self.billingcard.mesreftotal
    self.pprocessor = pproc.PaymentProcessor(
      ongoing_debt=ongoing_debt,
      duedate=self.paymonth,
      fix_ir_dec=self.fix_ir_dec,
    )
    if self.pprocessor is None:
      errmsg = f"Error: payment_processor is None"
      raise ValueError(errmsg)
    return self.pprocessor

  def calc_projected_mora(self):
    if self.billingcard.fech_pagts_n_mora is not None:
      cre, deb, _ = self.billingcard.fech_pagts_n_mora.cre_deb_moras_after_process
      # noinspection string-format
      errmsg = (f"Error: fechamento exists in billingcard: BC is closed (cre={cre:.2f}, deb={deb:.2f}),"
                f" cannot simulate month's mora.")
      raise ValueError(errmsg)
    _ = self.instantiate_n_get_payment_processor()
    # noinspection bad-argument-type
    self.monthmora = mk_n_get_monthmora_w_1pproc_n_2todate(pprocessor=self.pprocessor, todate=self.projected_date)

  def process(self):
    self.calc_projected_mora()

  def __str__(self):
    mm = self.get_monthmora()
    ostr = f"""{self.billingcard.contrnumber} | {self.billingcard.refmonth}
    monthmora = {mm}"""
    return ostr



def adhoctest1():
  """

  """
  contrnumber = 'CDouto202401'
  refmonth = mkrm('2026-4')
  print('contrnumber:', contrnumber, 'refmonth:', refmonth)
  billingcard = bcmod.dbfetch_billingcard_dictdoc_w_refmonth_n_contrnumber(
    contrnumber=contrnumber, refmonth=refmonth
  )
  print(billingcard)
  projected_date = refmonth + relativedelta(months=1, days=15)
  # noinspection argument-list
  msim = MonthsMoraSimulator(projected_date=projected_date, billingcard=billingcard)
  print(msim)
  print(msim.monthmora.explains())



def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
