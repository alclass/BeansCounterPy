def report_quinhoes_days_vals(self) -> str:
  """
  quinhoes_days_vals is a tuple list whose tuples contain:
    (ndays, moravalue)
  WHERE:
    ndays is the number of numbers that received 'mora'
    moravalue is the increased value due to the 'mora'

  What else can be reported?
  The elements in quinhoes_days_vals are related to payments.

  Example:
    if a payment was late (post duedate), it will:
    a) create one item to quinhoes_days_vals if it's fully compensates debt
    b) create two items in quinhoes_days_vals if a residue debt was left
  """
  tardypaymentsdict = {o.date.day: o for o in self.payments}
  if len(tardypaymentsdict) == 0:
    return "No tardy payments"
  lines = []
  line = 'Report/report_quinhoes_days_vals():'
  lines.append(line)
  _, ndaysinmonth = calendar.monthrange(self.duedate.year, self.duedate.month)
  # report_tuple = None
  for tupl in self.quinhoes_days_vals:
    # report_tuple = tupl
    # payment = None
    try:
      ndays, moravalue = tupl
      payment = tardypaymentsdict[ndays]
      line = f"mora {moravalue:.2f} foi gerada por {ndays} dias em {payment.date} com o pagt {payment.value}"
      lines.append(line)
    except KeyError:
      pass
  report_text = '\n'.join(lines)
  return report_text
