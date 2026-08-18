"""
art/immeub/rent/billmodels/monthly_pay_creditor_class.py
  Contains functions that pay a debt directly or by "quinhões"
    (i.e., peacemealwise when monthly mora is partitioned, i.e., it happens across more than one month)
"""
import calendar
from decimal import Decimal, Context, ROUND_HALF_UP
import datetime
from dateutil import relativedelta
import pydantic
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as fncach  # fncach.IpcaAPICacherRetriever
# for fncfs.calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate
import lib.fncfs.credeb_pkg.payment_processor as paybyquin  # paybyquin.process_payments_in_month
import lib.fncfs.credeb_pkg.samemonthmora_classes as mmora # mmora.SameMonthMora
import lib.fncfs.credeb_pkg.pay_dt_val_interface as intrfc  # intrfc.PaymentInterfaceDateNValue
DECIMAL_ZERO = Decimal('0')
DECIMAL_ONE = Decimal('1')
M_MINUS_N = 2


class PaymentCrediter(pydantic.BaseModel):
  refmonth: datetime.date
  monthspayvalue: Decimal
  dueday: int
  fix_ir: Decimal
  has_ipca: bool = True
  _ipca_dec: Decimal
  payments: list[intrfc.PaymentInterfaceDateNValue] = pydantic.dataclasses.Field(default_factory=lambda: [])
  mora_objs: list[intrfc.PaymentInterfaceDateNValue] = pydantic.dataclasses.Field(default_factory=lambda: [])
  credito_no_fecho: Decimal = pydantic.dataclasses.Field(default_factory=lambda: None)
  debito_no_fecho: Decimal = pydantic.dataclasses.Field(default_factory=lambda: None)
  ndays_n_increase_tuplelist: list[tuple[int, Decimal]] = pydantic.dataclasses.Field(default_factory=lambda: [])

  def add_payment(self, payment):
    self.payments.append(payment)

  @property
  def cur_refmonth(self):
    """
    This is the month when payment is due in an 'open window date range'
    """
    return self.refmonth + relativedelta.relativedelta(months=1)

  @property
  def duedate(self):
    year, month = self.cur_refmonth.year, self.cur_refmonth.month
    day = self.dueday
    return datetime.date(year=year, month=month, day=day)

  @property
  def open_pay_days_fr_to(self) -> tuple[int, int]:
    dayfrom = 1
    dayto = self.dueday
    return dayfrom, dayto

  @property
  def open_pay_daterange(self) -> tuple[datetime.date, datetime.date]:
    firstdate = self.curmonthsfirstdate
    duedate = self.duedate
    return firstdate, duedate

  @property
  def curmonthslastday(self):
    _, ndaysinmonth = calendar.monthrange(self.cur_refmonth)
    return ndaysinmonth

  @property
  def curmonthslastdate(self):
    year, month = self.cur_refmonth.year, self.cur_refmonth.month
    day = self.cur_refmonth.day
    year, month = self.cur_refmonth.year, self.cur_refmonth.month
    return datetime.date(year=year, month=month, day=day)

  @property
  def curmonthsfirstdate(self):
    year, month = self.cur_refmonth.year, self.cur_refmonth.month
    day = 1
    year, month = self.cur_refmonth.year, self.cur_refmonth.month
    return datetime.date(year=year, month=month, day=day)

  @property
  def ir_idx(self):
    fix_plus_var_ir_dec = self.fix_ir + self.ipca_dec
    return fix_plus_var_ir_dec

  @property
  def ipca_dec(self) -> Decimal:
    if not self.has_ipca:
      return DECIMAL_ZERO
    if self._var_ir is not None:
      return self._var_ir
    cacher = fncach.IpcaAPICacherRetriever()
    ipca_refmonth = rmfs.make_refmonth_it_minus_n_or_raise(self.refmonth, M_MINUS_N)
    ipca_dec = cacher.fetch_ipca_dec_for_refmonth(ipca_refmonth)
    self._var_ir = ipca_dec if ipca_dec is not None else DECIMAL_ZERO
    return self._var_ir

  def make_mora_objs(self):
    monthslastday = self.curmonthslastday
    for ndays_base_increase in self.ndays_n_increase_tuplelist:
      ndays, base, increase = ndays_n_increase
      todate = self.curmonthslastdate
      if ndays != monthslastday:
        todate = self.curmonthsfirstdate
      mora_o = SameMonthMora(
        fromdate=self.curmonthsfirstdate,
        todate=todate,
        prevalue=base,
        has_ipca=True,
      )


  def process_payments_in_month(self):
    self.credito_no_fecho, self.debito_no_fecho, self.ndays_n_increase_tuplelist = paybyquin.process_payments_in_month(
      valor_a_pagar_como_debito = self.monthspayvalue,
      payments = self.payments,
      duedate = self.duedate,
      retrodate_ifinmora = self.curmonthsfirstdate,
      postdate_ifinmora = self.curmonthslastdate,
      fix_plus_var_ir_dec = self.ir_idx,  # the variable parcel, if mora happens, is fetched 'downstream'
    )
    self.make_mora_objs()


def adhoctest1():
  """
  In the adhoctests below, ipca is not used, only the fix_ir_dec (=0.02).
  """
  mkdt = dtfs.make_date_or_raise
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  totaldebt = valor_a_pagar_como_debito
  payments = []
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(1200))
  payments.append(payment)
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-20'), value=Decimal(900))
  payments.append(payment)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  retrodate = mkdt('2026-4-1')
  postdate = mkdt('2026-4-30')
  monthly_fix_ir_dec = Decimal(0.02)
  credito, debito, quinhoes = process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    retrodate_ifinmora=retrodate,
    postdate_ifinmora=postdate,
    fix_plus_var_ir_dec=monthly_fix_ir_dec,
  )
  scrmsg = f"""Example:
    Input: debt = {totaldebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {quinhoes} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)
  # 2
  mkdt = dtfs.make_date_or_raise
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  totaldebt = valor_a_pagar_como_debito
  payments = []
  payment = intrfc.PaymentInterfaceDateNValue(
    date=mkdt('2026-4-08'), value=Decimal(1000)
  )
  payments.append(payment)
  payment = intrfc.PaymentInterfaceDateNValue(
    date=mkdt('2026-4-10'), value=Decimal(1000)
  )
  payments.append(payment)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  monthly_fix_ir_dec = Decimal(0.02)
  credito, debito, quinhoes = process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    retrodate_ifinmora=retrodate,
    postdate_ifinmora=postdate,
    fix_plus_var_ir_dec=monthly_fix_ir_dec
  )
  scrmsg = f"""Example:
    Input: debt = {totaldebt} | payments = {payments}
      duedate = {duedate} | pays issued: {billstotal} | quinhoes = {quinhoes} 
      monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f}
    Output: credito, debito = {credito:.2f}, {debito:.2f} 
  """
  print(scrmsg)
  # 3
  mkdt = dtfs.make_date_or_raise
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  totaldebt = valor_a_pagar_como_debito
  payments = []
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-08'), value=Decimal(1000))
  payments.append(payment)
  payment = intrfc.PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(900))
  payments.append(payment)
  payvalues = [p.value for p in payments]
  billstotal = sum(payvalues)
  duedate = mkdt('2026-4-10')
  monthly_fix_ir_dec = Decimal(0.02)
  credito, debito, quinhoes = process_payments_in_month(
    valor_a_pagar_como_debito=valor_a_pagar_como_debito,
    payments=payments,
    duedate=duedate,
    retrodate_ifinmora=retrodate,
    postdate_ifinmora=postdate,
    fix_plus_var_ir_dec=monthly_fix_ir_dec
  )
  scrmsg = f"""Example:
  Input: debt = {totaldebt} | payments = {payments} 
    duedate = {duedate} | pays issued: {billstotal} | quinhoes = {quinhoes} 
    monthly_fix_ir_dec = {monthly_fix_ir_dec:.2f} ipca = 0.00
  Output: credito, debito = {credito:.2f}, {debito:.2f} 
"""
  print(scrmsg)


def adhoctest2():
  fromdate = datetime.date(2026, 4, 1)
  todate = datetime.date(2026, 4, 13)
  d1 = DECIMAL_ONE
  mora = mmora.SameMonthMora(
    fromdate=fromdate,
    todate=todate,
    fix_ir_dec=Decimal(0.02),
    prevalue= 100 * d1,
  )
  print(mora)
  print(mora.explains())


def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest2()
