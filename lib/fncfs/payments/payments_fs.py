"""
lib/fncfs/payments/payments_fs.py
import lib.datesetc.datefs as dtfs

To import this:
  import lib.fncfs.payments_fs as payfs  # payfs.fn...
"""
import datetime
from decimal import Decimal


def verify_paydatahora_n_value_donotrepeat_in_payments_or_raise_va(p_payments):
  payments = p_payments[:]
  while len(payments) > 0:
    payment = payments.pop(0)
    for p in payments:
      if (p.datahora, p.value) == (payment.datahora, payment.value):
        errmsg = f"Error: there is a repeat in pair (datahora, value) in the payment list ({p_payments})."
        raise ValueError(errmsg)


def verify_paymentlist_contains_datahora_n_value_or_raise_va(p_payments):
  for p in p_payments:
    try:
      datahora, value = p.datahora, p.value
      if not isinstance(datahora, datetime.datetime):
        errmsg = f'Error: one payment datahora ({datahora}) is not a valid datetime.'
        raise ValueError(errmsg)
    except AttributeError as e:
      errmsg = str(e) + f'\nAttribute Error as VA: datahora is not a field in the object.'
      raise ValueError(errmsg)
    try:
      _ = Decimal(value)
    except (TypeError, ValueError) as e:
      errmsg = str(e) + f'\nError: one payment value ({value}) is not a valid Decimal.'
      raise ValueError(errmsg)


def verify_paymentlist_consistency_or_raise_va(p_payments):
  """
  verify_paymentlist_consistency_or_raise_va
    # 1st: verify date and value
    # 2nd: verify a repeat (or coincidence) in both datahora and value
  """
  if p_payments is None:
    errmsg = 'Error: payment list is None.'
    raise ValueError(errmsg)
  if len(p_payments) == 0:
    return
  verify_paymentlist_contains_datahora_n_value_or_raise_va(p_payments)
  verify_paydatahora_n_value_donotrepeat_in_payments_or_raise_va(p_payments)
  return


def split_nonrepeats_n_repeats_those_w_equal_datetime_n_value_in_payments(p_payments):
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


def remove_if_repeat_datetime_n_value_in_payments(p_payments):
  payments_wo_repeats, _ = split_nonrepeats_n_repeats_those_w_equal_datetime_n_value_in_payments(p_payments)
  return payments_wo_repeats


def do_datetime_n_value_repeat_in_payments(p_payments):
  payments_wo_repeats = remove_if_repeat_datetime_n_value_in_payments(p_payments)
  if len(p_payments) != len(payments_wo_repeats):
    return True
  return False


def raise_va_if_paydate_n_payvalue_repeat_in_payments(p_payments):
  if do_datetime_n_value_repeat_in_payments(p_payments):
    wo_repeats, w_repeats = split_nonrepeats_n_repeats_those_w_equal_datetime_n_value_in_payments(p_payments)
    if len(w_repeats) > 0:
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
  pass

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
