How to Calculate "Final Montant"
================================

A monthly compound interest "final montant" calculation is as follows:
  fm = im * (1 + ir) ** em
    where:
      fm = final montant
      im = initial montant
      ir = interest rate (may have a fix fraction [the ir itself] and a variable one [the mone_corr])
      em = number of months in-between
           (time in months elapsed from dates: initial and final)

Obs:
  o1 - the '**' operator means 'exponentiation'
  o2 - the measure-unit for the exponent is 'months' as mone_corr is calculated based on 'months' elapsed

Here is an example for an n_months exponent:
==================
  Suppose elapsed 'mora' duration is from '2026-01-01' to '2026-03-01', then n_months = 2.03226;
    the fractional part is due to the inclusive character of date range,
    in this case, March 1st 2026 ('2026-03-01') is included (this one day adds 1/31 to 2),
    the first day, January 1st 2026 ('2026-01-01') is also included.

    

  Mora, if any, explained
  =======================
  This can be explained with a simple example.
  Let's consider this context/situation:
    a) duedate is on month's day 10
    b) payment happened lately incomplete on month's day 20
  How 'mora' is calculated?
    1 first, a 20 day (after day 1) mora will increase the whole month's pay;
    2 then the pay on the 20th will credit the updated month's bill;
    3 then the remaining balance will increase to the rest of month
      (day 31, in this case, it increases another 10 days);
    4 this remaining is then closed (frozen),
       and is passed on to a new billing entry on the subsequent month's bill
    5 if another payment happens in between day 21 to month's end,
      payment_process() must be rerun and calculates again either credit or debit.

  When the month transitions (i.e., the next month comes),
    the 'mora' becomes a new 'billing item' itself and
    does not correct for the 10-day payment window.
    However, it goes into the same treatment as the other items
    in case a new mora becomes incident after duedate.

  billingcard: BillingCard = pydantic.dataclasses.Field(default_factory=lambda: None)
  refmonth: Optional[datetime.date] = pydantic.Field(default=lambda: rmfs.make_current_refmonth())

  In between, keep contrnumber and rentcontract,
    the following is the option not chosen (i.e., keeping contrnunber):

  @pydantic.computed_field
  @property
  def rentcontract(self) -> rentpydtc.PydtcRentContract:
    _rentcontract = rentpydtc.find_rentcontract_by_contrnumber(self.contrnumber)
    if _rentcontract is None:
      errmsg = f"Not Found Error: rent contract not found for contrnumber: {self.contrnumber}"
      raise ValueError(errmsg)
    return _rentcontract

