
  The payment process applies a mora to the receivable 
    as pays happens after the month's duedate.

    The date from which mora duration starts.
    When in mora, its time-span (duration) goes before duedate
      down to the first day of the month.

    Example:
      a) suppose the 'window' of payment is from the 1st to the 10th of the month;
      b) if payment happens within this pay-window, it's on duetime and ;
      c) if it happens later/tardy, the 'mora' is counted from day 1

    The date to which mora duration ends.
    When in months mora, this ending duration may be two:
      a) it's either the pay date itself;
      b) or, if value remains unpaid, it's the last day of the month;

    Notes on the 'window of payment' and, if payment is tardy, 'mora'
    ========

    When not in mora, a payment window (date range) opens.
    However, if duedate is overtaken, for tardy payments the payment window
      'retrodates' and becomes itself a 'mora' period
      together with the days after dueday
      (the whole month in fact because refmonth is M-1, i.e., the previous month.).

    The general case is the following:
      a) if dueday is the 10th of the month
      b) if a payment 'overtook' duedate
      c) then retroday goes back to the 1st day of month
      d) and postday goes either to paydate or,
         if it is debt remaining, the last day of the month.
      In fact, postday dynamically moves, with payments if any, towards the end of month.

    treat_last_mora_after_all_payments_credited(self)
    add_closing_mora_ifany()

    At this point, there may still be debt after duedate and processed payments.
    This is the last 'mora' to be considered if debt is still < 0
      and no payment happened on the last day of the pay month.

    credit_payments_upto_duedate()

    This method contains a function that credits the total paid to two accounts:
      a) 'cre_acc' - beginning with zero;
      b) 'deb_acc' - beginning with the month's charge (ongoing_debt at the beginning);

    The result of crediting is:
      if it pays exact, both cre_acc and deb_acc will be = 0  (there's no beginning credit, only a beginning debt)
      if it pays below, deb will be < 0 (negative)
      if it pays above, cre will be > 0 (positive)


    Credits a payment to both the debt and credit accounts,
      and, as a second step, compensate, if needed, credit against debt.

    Credits a payment to debt in two steps:
      1 credit to ongoing_debt and, if any remains, to ongoing_credit;
      2 do the second pass that compensates the case when both credit and debt
        coexist after the above operation.  

    The processing ends with the formation of the triple:
      t1 credito_no_fecho, t2 debito_no_fecho, t3 monthmoras
    or
      t1 ongoing_credit, t2 ongoing_debt, t3 monthmoras

    This function uses a 'subsystem' (a functions module) that does the credit/debt calculation.
    The 'process' respects duedate and outdated payments,
      the latter on which 'mora' is incident.

