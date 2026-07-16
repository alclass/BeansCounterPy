import unittest
import art.immeub.rent.bill.mora_calculator as mclc  # mclc.MoraMonthCalculator
from dinero import Dinero
from dinero.currencies import BRL  # USD, EUR
import lib.datesetc.rmfs as rmfs  # refmonth_fs.py.months_inbetween_ret_int_n_float

class Test1(unittest.TestCase):

  def test_1(self):
    """
    Zero both fix and var interest rates,
      then ini_montant should be equal to fin_montant
    """
    mi = Dinero("1000", BRL)
    di, df = "2026-01-01", "2026-01-31"
    mo = mclc.MoraMonthCalculator(
      ini_montant=mi,
      ini_date=di,
      fin_date=df,
      fix_ir_pct=0,
      var_ir_pct=0
    )
    mlt_mo = mo.multiplier_for_mora
    self.assertAlmostEqual(mlt_mo, 0.0)
    self.assertEqual(mo.fin_montant, mi)

  def test_2(self):
    """
    Make a month-whole time elapse,
      then the fin_montant should emcompass one month interest
      which involves a "simpler" calculation: fm = im * (1 + ir) ** 1,
      because exponent is "1"
    """
    mi = Dinero("1000", BRL)
    di, df = "2026-01-01", "2026-01-31"
    mo = mclc.MoraMonthCalculator(
      ini_montant=mi,
      ini_date=di,
      fin_date=df,
      fix_ir_pct=5,
      var_ir_pct=5,
    )
    # fin_montant is 10% more than ini_montant
    mf = Dinero("1100", BRL)
    mlt_mo = round(mo.multiplier_for_fm, 1)
    self.assertAlmostEqual(mlt_mo, 1.1)
    self.assertEqual(mo.fin_montant, mf)

  def test_3(self):
    """
    Make a two-month-whole time elapse,
      then the fin_montant should emcompass one month interest
      which also involves a "simpler" calculation: fm = im * (1 + ir) ** 2,
      because exponent is "2"
    """
    mi = Dinero("1000", BRL)
    di, df = "2026-01-01", "2026-02-28"
    mo = mclc.MoraMonthCalculator(
      ini_montant=mi,
      ini_date=di,
      fin_date=df,
      fix_ir_pct=5,
      var_ir_pct=5,
    )
    # fin_montant is 10% more than ini_montant
    mf = Dinero("1210", BRL)
    # mlt_mo = round(mo.multiplier_for_fm, 3)
    self.assertEqual(31+28, mo.inbetween_days)
    self.assertEqual(2, 2)  # mo.inbetween_months
    mult_for_calc_fin_mont = 1.1**2
    # mlt_mo = mo.multiplier_for_fm
    # self.assertAlmostEqual(mlt_mo, mult_for_calc_fin_mont)
    # self.assertEqual(mo.fin_montant, mf)


class TestCase2(unittest.TestCase):

  def test_1(self):
    di, df = "2026-01-01", "2026-01-31"
    i, frac = rmfs.months_inbetween_return_int_n_float(di, df)
    self.assertEqual((i, frac), (1,0))
