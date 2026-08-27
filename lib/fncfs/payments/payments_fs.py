"""

"""


def raise_if_a_payment_repeats_with_date_n_value_within(p_payments):
  payments = p_payments[:]
  while len(payments) > 0:
    payment = payments.pop(0)
    if len(payments) > 0:
      boolarr = map(lambda o: o.date == payment.date and o.value == payment.value, payments)
      boolarr = list(boolarr)
      if True in boolarr:
        errmsg = f"Error: payment [{payment}] date and value has already been entered.."
        errmsg += f"\n\t if two payments are equal on the same day, they should be consolidated."
        errmsg += f"\n\t all payments are: {p_payments}."
        raise ValueError(errmsg)
