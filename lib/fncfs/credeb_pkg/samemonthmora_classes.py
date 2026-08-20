"""
art/immeub/rent/billmodels/samemonthmora_class.py
  Contains functions that pay a debt directly or by "quinhões"
    (i.e., peacemealwise when monthly mora is partitioned, i.e., it happens across more than one month)
"""
from decimal import Decimal, Context, ROUND_HALF_UP
import datetime
from typing import Optional
import pydantic
from dateutil.relativedelta import relativedelta

import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.indices.ipca.ipca_fetcher_cacher as fncach  # fncach.IpcaAPICacherRetriever
# for fncfs.calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fncfs
DECIMAL_ZERO = Decimal('0')
DECIMAL_ONE = Decimal('1')
M_MINUS_N = 2


class SameMonthMora(pydantic.BaseModel):
  fromdate: datetime.date
  todate: datetime.date  # todate is also incidencedate
  prevalue: Decimal
  fix_ir_dec: Decimal
  has_ipca: bool = True
  _var_ir: Optional[Decimal] = None
  _postvalue: Optional[Decimal] = None
  _increase: Optional[Decimal] = None

  def explains(self) -> str:
    ir_pct = self.ir_idx * 100
    ir_pct = f"{ir_pct:.2f}%"
    line = f"em {self.todate} houve incidência de mora sobre {self.prevalue:.2f} por {self.moradays} dias à taxa {ir_pct} gerando incremento de {self.increase:.2f} (subtotal  {self.postvalue:.2f})"
    return line

  @property
  def refmonth(self) -> datetime.date:
    """
    refmonth is the previous month related to the month when payment happens
    It may be said the refmonth is M-1
    """
    _refmonth = rmfs.make_refmonth_it_minus_n_or_raise(self.fromdate, 1)
    return _refmonth

  @property
  def moradays(self):
    deltadays = self.todate - self.fromdate
    _moradays = deltadays.days + 1 # because mora rolls along the month, it cannot add '+ 1'
    return _moradays

  @property
  def increase(self) -> Decimal:
    if self._increase is None:
      self._increase = self.calc_increase()
      return self._increase
    else:
      return self._increase

  @property
  def ipca_dec(self) -> Decimal | None:
    if not self.has_ipca:
      return DECIMAL_ZERO
    if self._var_ir is not None:
      return self._var_ir
    cacher = fncach.IpcaAPICacherRetriever()
    ipca_refmonth = rmfs.make_refmonth_it_minus_n_or_raise(self.refmonth, M_MINUS_N)
    ipca_dec = cacher.fetch_ipca_dec_for_refmonth(ipca_refmonth)
    self._var_ir = ipca_dec if ipca_dec is not None else DECIMAL_ZERO
    return self._var_ir

  @property
  def var_ir(self) -> Decimal:
    if not self.has_ipca:
      return DECIMAL_ZERO
    return self.ipca_dec

  @property
  def ir_idx(self) -> Decimal:
    return self.fix_ir_dec + self.var_ir

  @property
  def postvalue(self) -> Decimal:
    if self.todate == self.fromdate:
      return self.prevalue
    if self._postvalue is None:
      # ajust days: either add 1 to the first or diminish 1 to the last
      # this is because monthmora 'slides' through the month according to the dates interacted with
      findate = self.todate - relativedelta(days=1)
      self._postvalue, increase = fncfs.calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
        inimontant=self.prevalue,
        ir_idx=self.ir_idx,
        inidate=self.fromdate,
        findate=findate,
      )
    return self._postvalue

  def calc_increase(self) -> Decimal:
    if self.todate == self.fromdate:
      return Decimal(0)
    # ajust days: either add 1 to the first or diminish 1 to the last
    # this is because monthmora 'slides' through the month according to the dates interacted with
    findate = self.todate - relativedelta(days=1)
    _increase = fncfs.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=self.prevalue,
      ir_idx=self.ir_idx,
      inidate=self.fromdate,
      findate=findate,
    )
    return _increase

  def __str__(self):
    fr, to = self.fromdate, self.todate
    ostr = f"SameMonthMora: fr={fr} to={to} ndays={self.moradays} ipca={self.ipca_dec:.4f} fix={self.fix_ir_dec:.2f}"
    preval, posval = self.prevalue, self.postvalue
    ostr += f"\n\t preval={preval:.2f} | posval={posval:.2f} | incr={self.increase:.2f} | ir={self.ir_idx:.4f} modays={self.moradays}"
    return ostr


def adhoctest1():
  """
  In the adhoctests below, ipca is not used, only the fix_ir_dec (=0.02).
  """
  mkdt = dtfs.make_date_or_raise
  ctx = Context(prec=32, rounding=ROUND_HALF_UP)
  valor_a_pagar_como_debito = Decimal(-2000, context=ctx)
  totaldebt = valor_a_pagar_como_debito
  payments = []
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(1200))
  payments.append(payment)
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-20'), value=Decimal(900))
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
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-08'), value=Decimal(1000))
  payments.append(payment)
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(1000))
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
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-08'), value=Decimal(1000))
  payments.append(payment)
  payment = PaymentInterfaceDateNValue(date=mkdt('2026-4-10'), value=Decimal(900))
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
  mora = SameMonthMora(
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
