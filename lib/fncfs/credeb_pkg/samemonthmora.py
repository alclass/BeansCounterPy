"""
lib/fncfs/credeb_pkg/samemonthmora.py
  Contains class SameMonthMora which calculates mora within a month.

from dateutil.relativedelta import relativedelta
"""
from decimal import Decimal, Context, ROUND_HALF_UP
import datetime
from typing import Optional
import pydantic
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fncfs
DECIMAL_ZERO = Decimal('0')
DECIMAL_ONE = Decimal('1')
M_MINUS_N_POSTPAYCASE = 1


class SameMonthMora(pydantic.BaseModel):
  fromdate: datetime.date
  todate: datetime.date  # find out, in Pydantic, how to criticize todate so that is not smaller than fromdate
  prevalue: Decimal  # the client-caller has to control whether prevalue is positive (credit) or negative (debt)
  fix_ir_dec: Decimal
  var_ir_dec: Decimal
  var_ir_sigla: str = "IPCA"
  _postvalue: Optional[Decimal] = None
  _increase: Optional[Decimal] = None

  @pydantic.model_validator(mode='after')
  def check_date_order(self) -> 'SameMonthMora':
    # Self contains fully validated date objects at this point
    if self.todate < self.fromdate:
      errmsg = f'todate {self.todate} cannot be earlier than fromdate {self.fromdate}'
      raise ValueError(errmsg)
    return self

  def explains(self) -> str:
    ir_pct = self.ir_idx * 100
    ir_pct = f"{ir_pct:.2f}%"
    line = f"\t=> Em {self.todate} houve incidência de mora sobre R${self.prevalue:.2f} por {self.moradays} dias à taxa {ir_pct} ao mês gerando incremento de R${self.increase:.2f} (subtotal R${self.postvalue:.2f})"
    return line

  @property
  def refmonth(self) -> datetime.date:
    """
    refmonth is the previous month related to the month when payment happens.
    It may be said the refmonth is M-1 (that is, the previous month).
    Notice that the IPCA refmonth is M-1 from the billing refmonth (this) or M-2 from payment refmonth.
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
    # the IDE complains self._increase can be None, but self.calc_increase() does not have a return None type-hint
    # noinspection bad-return
    return self._increase

  @property
  def ir_idx(self) -> Decimal:
    """The sum of the fix part and the variable part of the return rate (or ir = interest rate)."""
    return self.fix_ir_dec + self.var_ir_dec

  @property
  def postvalue(self) -> Decimal:
    """
    Is the final montant (*) of prevalue with ir_idx and the exponent as the month's fraction.

    (*) The 'final montant' in the 'canonical' financial equation is:
      fm = im * (1 + r) ** d
    WHERE:
      fm = final montant
      r = the return rate (or interest rate)
      d = the duration in the operation's time measure unit
    """
    if self._postvalue is None:
      self._postvalue, _ = fncfs.calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
        inimontant=self.prevalue,
        ir_idx=self.ir_idx,
        inidate=self.fromdate,
        findate=self.todate,
      )
    # noinspection bad-return
    return self._postvalue

  def calc_increase(self) -> Decimal:
    """
    Calculates the increase, i.e. the increment that is added to inimontant to give finmontant.
    @see also docstr for postvalue above.
    It calls an 'underlying' financial function for that purpose.
    """
    _increase = fncfs.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=self.prevalue,
      ir_idx=self.ir_idx,
      inidate=self.fromdate,
      findate=self.todate,
    )
    return _increase

  def __repr__(self) -> str:
    frdt = self.fromdate.strftime('%Y%m%d')
    todt = self.todate.strftime('%Y%m%d')
    prev = f"{self.prevalue:.2f}"
    posv = f"{self.postvalue:.2f}"
    inc = f"{self.increase:.2f}"
    retidx = f"{self.ir_idx:.4f}"
    ostr = f"SMM(fr={frdt}, to={todt}, preval={prev}, r={retidx}, inc={inc}, postval={posv})"
    return ostr

  def __str__(self) -> str:
    fr, to = self.fromdate, self.todate
    ostr = f"SameMonthMora: fr={fr} to={to} ndays={self.moradays} fix={self.fix_ir_dec:.2f} var={self.var_ir_dec:.4f}"
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
    var_ir_dec=Decimal(0.0033),
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
