"""
lib/fncfs/payments/payments_fs.py

To import this:
  import lib.fncfs.payments_fs as payfs  # payfs.fn...
"""
import datetime
from decimal import Decimal
import pydantic
import lib.datesetc.datefs as dtfs


class InterfPayment(pydantic.BaseModel):
  datetime: datetime.datetime
  value: Decimal

  @property
  def date(self):
    return self.datetime.date()

  @property
  def daytime(self):
    """
    Here we also call 'daytime' as 'hour'
      (generically including minutes etc.)
    """
    return self.datetime.date()

  def set_daytime(self, pdaytime):
    pdate = self.datetime.date()
    self.datetime = datetime.datetime.combine(pdate, pdaytime)

  @property
  def triple_y_m_d(self):
    dt = self.datetime
    year, month, day = dt.year, dt.month, dt.day
    return year, month, day

  @property
  def triple_h_m_s(self):
    dt = self.datetime
    hour, minute, second = dt.hour, dt.minute, dt.second
    return hour, minute, second

  def __repr__(self):
    hour = self.datetime.time()
    ostr = f"d={self.date}|h={hour}|v={self.value}"
    return ostr

  def __str__(self):
    dt = self.datetime
    dt_str = dt.strftime("%Y-%m-%d")  # e.g., "2026-08-27"
    ho_str = dt.strftime("%H:%M:%S")  # e.g., "10:48:00"
    value = f"{self.value:.02f}"
    ostr = "Payment: {"
    ostr += f"value={value} on dt={dt_str} @ ho={ho_str}"
    ostr += "}"
    return ostr


def split_nonrepeats_n_repeats_date_value_sameday_fr_payments(p_payments):
  """
  This function treats case where the hour-time of payment is not recorded
    and a payment may have been repeated.
  TODO This function should be upgraded to treat the full datetime
    of payment so that two payments with the same datetime from the same source are considered mistaken.
  """
  payments = p_payments[:]
  payments_wo_repeats, repeats = [], []
  while len(payments) > 0:
    payment = payments.pop(0)
    if len(payments) == 0:
      payments_wo_repeats.append(payment)
    else:  # if len(payments) > 0:
      boolarr = map(lambda o: o.datahora == payment.datahora and o.value == payment.value, payments)
      boolarr = list(boolarr)
      if True in boolarr:
        repeats.append(payment)
      else:
        payments_wo_repeats.append(payment)
  return payments_wo_repeats, repeats


def remove_if_sameday_repeat_date_n_value_fr_payments(p_payments):
  payments_wo_repeats, _ = split_nonrepeats_n_repeats_date_value_sameday_fr_payments(p_payments)
  return payments_wo_repeats


def verify_if_paydate_n_payvalue_repeat_sameday_in_payments(p_payments):
  payments_wo_repeats = remove_if_sameday_repeat_date_n_value_fr_payments(p_payments)
  if len(p_payments) != len(payments_wo_repeats):
    return True
  return False


def raise_if_paydate_n_payvalue_repeat_sameday_in_payments(p_payments):
  if verify_if_paydate_n_payvalue_repeat_sameday_in_payments(p_payments):
    wo_repeats, w_repeats = split_nonrepeats_n_repeats_date_value_sameday_fr_payments(p_payments)
    errmsg = f"Error: there is/are repeated date and value payment(s)."
    errmsg += f"\n\t if two payments are equal on the same day, they should be consolidated."
    errmsg += f"\n\t all payments are: {p_payments}."
    errmsg += f"\n\t repeated payments are: {w_repeats}."
    errmsg += f"\n\t non-repeated payments are: {wo_repeats}."
    raise ValueError(errmsg)


def split_daydate_n_hourtime_fr_datetime():
  # 1. Create or get a sample datetime object
  dt_now = datetime.datetime.now()
  # 2. Extract the individual components
  just_date = dt_now.date()  # Returns a datetime.date object
  just_time = dt_now.time()  # Returns a datetime.time object
  print("Original Datetime:", dt_now)
  print("Extracted Date:   ", just_date)
  print("Extracted Time:   ", just_time, type(just_time))


def adhoctest1():
  payments = []
  paydate = dtfs.make_date_or_raise('2026-04-10')
  payhour = datetime.time(hour=10, minute=10)
  paydatetime = datetime.datetime.combine(paydate, payhour)
  payvalue = Decimal('2000')
  payment = InterfPayment(datetime=paydatetime, value=payvalue)
  # 1
  payments.append(payment)
  # 2
  payments.append(payment)
  paydate = dtfs.make_date_or_raise('2026-04-21')
  payhour = datetime.time(hour=10, minute=10)
  paydatetime = datetime.datetime.combine(paydate, payhour)
  payvalue = Decimal('1500')
  payment = InterfPayment(datetime=paydatetime, value=payvalue)
  # 3
  payments.append(payment)
  wo, w = split_nonrepeats_n_repeats_date_value_sameday_fr_payments(payments)
  print('payments:')
  for i, payment in enumerate(payments):
    seq = i + 1
    print(seq, payment)
  print('without repeats:', wo)
  print('with repeats:', w)


def adhoctest2():
  split_daydate_n_hourtime_fr_datetime()


def adhoctest3():
  """
  Adhoctesting with datetime.datetime.combine()
  Timetuple unpackingQuick unpacking shortcut
    datetime(*my_date.timetuple()[:3])
  Pandas to_datetimeDataFrames and Series arrays
    import pandas as pdpd.to_datetime(my_date)
  """
  print('Adhoctesting with datetime.datetime.combine()')
  dt = datetime.datetime.now()
  pdate = dt.date()
  print('Setting 11:11:00 to', dt, 'and date is', pdate)
  h = datetime.time(hour=11, minute=11)
  newdt = datetime.datetime.combine(pdate, h)
  print('newdt', newdt)


def process():
  pass


if __name__ == '__main__':
  """
  """
  process()
  adhoctest1()
  adhoctest2()
  adhoctest3()
