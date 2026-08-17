"""
lib/fncfs/credeb_pkg/pay_by_quinhoes_etc.py
  Contains functions that pay a debt directly or by "quinhões"
    (i.e., peacemealwise when monthly mora is partitioned, i.e., it happens across more than one month)
"""
import calendar
from decimal import Decimal, Context, ROUND_HALF_UP
import decimal
import datetime
from dataclasses import dataclass, field
from typing import Optional
from dateutil import relativedelta
import pydantic
import lib.datesetc.datefs as dtfs
import lib.fncfs.credeb_pkg.credit_debit_fs as cdfs  # cdfs.debit_value_to_accounts
# for fncfs.calc_finalmontant_w_1inimontant_2fixir_fetchipca_3inidate_4findate
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fncfs
DECIMAL_ZERO = Decimal('0')
DECIMAL_ONE = Decimal('1')


class SameMonthMora(pydantic.BaseModel):
  fromdate: datetime.date
  todate: datetime.date  # todate is also incidencedate
  prevalue: Decimal
  fix_ir: Decimal
  has_ipca: bool = True
  _var_ir: Optional[Decimal] = None
  _postvalue: Optional[Decimal] = None

  def explains(self) -> str:
    ir_pct = self.ir_idx * 100
    ir_pct = f"{ir_pct:.2f}%"
    line = f"em {self.todate} houve incidência de mora sobre {self.prevalue:.2f} por {self.moradays} dias à taxa {ir_pct} gerando incremento de {self.increase:.2f} (subtotal  {self.postvalue:.2f})"
    return line

  @property
  def moradays(self):
    deltadays = self.todate - self.fromdate
    _moradays = deltadays.days + 1
    return _moradays

  @property
  def increase(self) -> Decimal:
    return self.postvalue - self.prevalue

  @property
  def ipca_dec(self) -> Decimal:
    return DECIMAL_ZERO

  @property
  def var_ir(self) -> Decimal:
    if not self.has_ipca:
      return DECIMAL_ZERO
    return self.ipca_dec

  @property
  def ir_idx(self) -> Decimal:
    return self.fix_ir + self.var_ir

  @property
  def postvalue(self) -> Decimal:
    if self._postvalue is None:
      self._postvalue, increase = fncfs.calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
        inimontant=self.prevalue,
        ir_idx=self.ir_idx,
        inidate=self.fromdate,
        findate=self.todate,
      )
    return self._postvalue

  def __str__(self):
    fr, to = self.fromdate, self.todate
    ostr = f"SameMonthMora: fr={fr} to={to} ndays={self.moradays}"
    preval, posval = self.prevalue, self.postvalue
    ostr += f"\n\t preval={preval:.2f} | posval={posval:.2f} | incr={self.increase:.2f}"
    return ostr




@dataclass
class PaymentInterfaceDateNValue:
  """
  This class is just to contain payment's date and value
  Clients will use it with obj.date and obj.value

  It aims to simplify the two fields for objects
    coming from a Pydantic class with more attributes.
  """
  date: datetime.date
  value: Decimal

  def __str__(self):
    ostr = f"payvalue={self.value} on {self.date}"
    return ostr


class PaymentCrediter(pydantic.BaseModel):
  refmonth: datetime.date
  monthspayvalue: Decimal
  dueday: int
  fix_ir: Decimal
  has_ipca: bool = True
  _ipca_dec: Decimal
  payments: list[PaymentInterfaceDateNValue] = pydantic.dataclasses.Field(default_factory=lambda: [])
  mora_objs: list[PaymentInterfaceDateNValue] = pydantic.dataclasses.Field(default_factory=lambda: [])

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
  def ipca_dec(self):
    if self._ipca_dec is None:
      ipcacacher = 1

  def process_payments_in_month(self):
    process_payments_in_month(
      valor_a_pagar_como_debito = self.monthspayvalue,
      payments = self.payments,
      duedate = self.duedate,
      retrodate_ifinmora = self.curmonthsfirstdate,
      postdate_ifinmora = self.curmonthslastdate,
      fix_plus_var_ir_dec = self.ir_idx,  # the variable parcel, if mora happens, is fetched 'downstream'
    )


def pay_monthsbill_by_quinhao_considering_mora(
    debito_em_mora: Decimal,
    p_payments: list[PaymentInterfaceDateNValue],  # we'll only need date and value from a payment object
    retrodate_ifinmora: datetime.date,
    postdate_ifinmora: datetime.date,
    fix_plus_var_ir_dec: Decimal  # the variable parcel, if mora happens, is fetched 'downstream'
  ) -> tuple[decimal.Decimal, decimal.Decimal, list[tuple[int, Decimal]]]:
  """

  All input dates for this function must be in the same month.

  Explanation of retrodate_ifinmora and postdate_ifinmora:
  ==============
    retrodate_ifinmora applies only when in mora.
    The same with postdate_ifinmora.

    When in mora, a payment window (date range) opens.
    However, if duedate is overtaken, the payment window
      becomes a 'mora' moment together with the days after
      dueday (the whole month in fact for refmonth is M-1).
    The general case is the following:
      a) if dueday is the 10th
      b) if that day is 'overtaken'
      c) then retroday goes to the 1st
      d) and postday goes to the last day of the month
  """
  if debito_em_mora > DECIMAL_ZERO:
    errmsg = f"Error: debito_em_mora (={debito_em_mora}) cannot be greater than zero"
    raise ValueError(errmsg)
  elif debito_em_mora == DECIMAL_ZERO:
    return DECIMAL_ZERO, DECIMAL_ZERO, []
  # at this point: debito_em_mora < DECIMAL_ZERO
  debito, credito = debito_em_mora, DECIMAL_ZERO
  payments = p_payments[:]  # copy it
  quinhoes_days_vals = []
  while len(payments) > 0:
    payment = payments.pop(0)
    payvalue = payment.value
    paydate = payment.date
    inimontant = -debito
    if inimontant > DECIMAL_ZERO:
      mora_incr = fncfs.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
        inimontant, fix_plus_var_ir_dec, retrodate_ifinmora, paydate
      )
      debito = debito - mora_incr
      ndays = paydate.day - retrodate_ifinmora.day + 1
      days_n_vals = (ndays, mora_incr)
      quinhoes_days_vals.append(days_n_vals)
      debito = debito + payvalue  # notice pay is positive, debito is negative
      if debito > DECIMAL_ZERO:
        # debito has been paid
        credito += debito
        debito = DECIMAL_ZERO
        break
    else:  # debito has been paid
      credito += payvalue
    # loop on if while condition is still true (more payments in queue)
  # loop is over, payments all considered
  # at this point, if debito may or may not yet exist
  # however, if it does, it must mora-increase from retrodate_ifinmora to postdate_ifinmora
  if debito < DECIMAL_ZERO:
    inimontant = -debito
    mora_incr = fncfs.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant, fix_plus_var_ir_dec, retrodate_ifinmora, postdate_ifinmora
    )
    debito = debito - mora_incr
    ndays = postdate_ifinmora.day - retrodate_ifinmora.day + 1
    days_n_vals = (ndays, mora_incr)
    quinhoes_days_vals.append(days_n_vals)
  return credito, debito, quinhoes_days_vals


def process_payments_in_month(
    valor_a_pagar_como_debito: Decimal,
    payments: list[PaymentInterfaceDateNValue],  # we'll only need date and value from a payment object
    duedate: datetime.date,
    retrodate_ifinmora: datetime.date,
    postdate_ifinmora: datetime.date,
    fix_plus_var_ir_dec: Decimal  # the variable parcel, if mora happens, is fetched 'downstream'
  ) -> tuple[decimal.Decimal, decimal.Decimal, list[tuple[int, Decimal]]]:
  """
  This function receives a debt value and a list of payments.
  It outputs two values: credito_no_fecho, debito_no_fecho
    credito_no_fecho is an excedent out of the payments
    debito_no_fecho signals that the payment was not completed

  This function uses a 'subsystem' that does the credit/debit calculation.
  The 'process' respects duedate and outdated payments,
    on the latter 'mora' is incident.
  """
  debtvalue = valor_a_pagar_como_debito
  if debtvalue > DECIMAL_ZERO:
    errmsg = f"Error: debt (={debtvalue}) cannot be greater than DECIMAL_ZERO"
    raise ValueError(errmsg)
  if len(payments) == 0:
    # there is no payments
    return DECIMAL_ZERO, debtvalue, []
  payments_ondate = list(filter(lambda po: po.date <= duedate, payments))
  payvalues = [p.value for p in payments_ondate]
  cred_account = sum(payvalues)
  if not isinstance(cred_account, Decimal):
    cred_account = Decimal(cred_account)
  credito_no_fecho, debito_no_fecho = cdfs.debit_value_to_accounts(debtvalue, cred_account, DECIMAL_ZERO)
  credito_no_fecho = DECIMAL_ZERO if credito_no_fecho is None else credito_no_fecho
  debito_no_fecho = DECIMAL_ZERO if debito_no_fecho is None else debito_no_fecho
  payments_outdate = list(filter(lambda po: po.date > duedate, payments))
  if len(payments_outdate) == 0:
    # all payments were in duedate, but we still have to check debito_no_fecho
    quinhoes_days_vals = []
    if debito_no_fecho < DECIMAL_ZERO:
      # there should be a 'mora-projection' from retro to post date
      inimontant = -debito_no_fecho
      # mora_incr 'projects' this remaining debt to postdate
      mora_incr = fncfs.calc_increase_amount_w_1inimontant_2iridx_3inidate_4findate_samemonth(
        inimontant=inimontant,
        ir_idx=fix_plus_var_ir_dec,
        inidate=retrodate_ifinmora,
        findate=postdate_ifinmora,
      )
      # fill in 'quinhoes'
      ndays = postdate_ifinmora.day - retrodate_ifinmora.day + 1
      days_n_vals = (ndays, mora_incr)
      quinhoes_days_vals.append(days_n_vals)
      # udpates debito_no_fecho according to the 'projection' above
      debito_no_fecho = debito_no_fecho - mora_incr
    return credito_no_fecho, debito_no_fecho, quinhoes_days_vals
  if credito_no_fecho > DECIMAL_ZERO:
    # notice that credito is always positive, debito is always negative
    # if one of them has value, the other must be zeroed
    return credito_no_fecho, debito_no_fecho, []
  # now the following condition holds: there are payments done out of duedate
  laterpayvalues = [p.value for p in payments_outdate]
  later_cred_account = sum(laterpayvalues)
  # then let's check if debito == 0, if so, payments go to credit
  if debito_no_fecho == DECIMAL_ZERO:
    credito_no_fecho += later_cred_account
    return credito_no_fecho, debito_no_fecho, []
  # now it's the most 'difficult' part because it involves 'mora'
  if not debito_no_fecho < DECIMAL_ZERO:
    errmsg = f"debito_no_fecho ({debito_no_fecho}) is not < DECIMAL_ZERO"
    raise ValueError(errmsg)
  debito_ainda = debito_no_fecho
  return pay_monthsbill_by_quinhao_considering_mora(
    debito_em_mora=debito_ainda,
    p_payments=payments_outdate,
    retrodate_ifinmora=retrodate_ifinmora,
    postdate_ifinmora=postdate_ifinmora,
    fix_plus_var_ir_dec=fix_plus_var_ir_dec,
  )  # returns credito_no_fecho, debito_no_fecho, quinhoes_days_vals


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
    fix_ir=Decimal(0.02),
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
