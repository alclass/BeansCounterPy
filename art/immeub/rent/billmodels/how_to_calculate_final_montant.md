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
