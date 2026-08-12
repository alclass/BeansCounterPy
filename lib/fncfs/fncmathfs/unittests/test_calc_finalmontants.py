import unittest
from math import exp
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants as fm_mnts  # fm_cmnts.calc_incrfactor_intrstrt_w_1iridx_2expo
import datetime
from decimal import Decimal, ROUND_HALF_UP
from lib.fncfs.credeb_pkg.credit_debit_fs import debit_or_credit_value_to_accounts
import lib.datesetc.refmonth_fs as rmfs
decimal_zero = Decimal('0.0')
decimal_one = Decimal('1.0')


def quantize6decplaces(decvalue):
  """
  Quantizes "decimal" to 6 decimal places and set rounding as ROUND_HALF_UP.
  Useful to compare values in the context here with assertEqual
  """
  return decvalue.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)


class TestCase1(unittest.TestCase):

  def test_1_multiplier_for_fm(self) -> None:
    """
    Unit-testing multiplier for (fm) final montant
    This means the number that multiplied by initial montant gives final montant
      => fm = im * multiplier_for_fm
    """
    # ======================
    # hypothesis 1-1 -> ir_idx, exponent = 1, 1
    # multiplier_for_fm=(1+1)**1=2
    # ======================
    d1, d2 = decimal_one, 2 * decimal_one
    ir_idx, exponent = d1, d1
    byhand_mult_fo_fm = (1 + ir_idx) ** exponent  # (1+1)**1=2
    exp_mult_fo_fm = d2
    self.assertEqual(exp_mult_fo_fm, byhand_mult_fo_fm)
    ret_mult_fo_fm = fm_mnts.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_mult_fo_fm, ret_mult_fo_fm)
    # ======================
    # hypothesis 1-2 -> ir_idx, exponent = 3, 2
    # multiplier_for_fm = (1+3)**2=16
    # ======================
    d3, d16 = 3 * d1, 16 * d1
    ir_idx, exponent = d3, d2
    byhand_mult_fo_fm = (1 + ir_idx) ** exponent  # (1+3)**2=16
    exp_mult_fo_fm = d16
    self.assertEqual(exp_mult_fo_fm, byhand_mult_fo_fm)
    ret_mult_fo_fm = fm_mnts.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_mult_fo_fm, ret_mult_fo_fm)
    # ======================
    # hypothesis 1-3 -> ir_idx, exponent = 1.2, 2.3
    # multiplier_for_fm = (1+1.2)**2.3 - 1 = 6.131576
    # ======================
    ir_idx, exponent = Decimal(1.2), Decimal(2.3)
    byhand_mult_fo_fm = (1 + ir_idx) ** exponent
    byhand_mult_fo_fm = quantize6decplaces(byhand_mult_fo_fm)
    exp_mult_fo_fm = Decimal('6.131576709333357')
    exp_mult_fo_fm = quantize6decplaces(exp_mult_fo_fm)
    self.assertEqual(exp_mult_fo_fm, byhand_mult_fo_fm)
    ret_mult_fo_fm = fm_mnts.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    ret_mult_fo_fm = quantize6decplaces(ret_mult_fo_fm)
    self.assertEqual(exp_mult_fo_fm, ret_mult_fo_fm)

  def test_2_multiplier_for_increase(self) -> None:
    """
    Unit-testing multiplier for (fm) increase
    This means the number that multiplied by initial montant gives the increase
      => increase = im * multiplier_for_incr
      and => fm = im + increase
    """
    # ======================
    # hypothesis 2-1
    # (1+0.1)**2=1.21
    # 1.21 - 1 = 0.21 (21%)
    # ======================
    d0, d1 = decimal_zero, decimal_one
    d2 = 2 * d1
    ir_idx, exponent = d1/10, d2
    byhand_mult_fo_incr = (1 + ir_idx) ** exponent - d1
    exp_mult_fo_incr = Decimal('0.21')
    self.assertEqual(exp_mult_fo_incr, byhand_mult_fo_incr)
    ret_mult_fo_incr = fm_mnts.calc_multiplier_for_increase_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_mult_fo_incr, ret_mult_fo_incr)
    # ======================
    # hypothesis 2-2
    # mult_for_im = (1+3)**2=16
    # mult_for_increase = 16-1 = 15
    # 16 - 1 = 15 (1500%)
    # ======================
    d3, d16 = 3 * d1, 16 * d1
    ir_idx, exponent = d3, d2
    byhand_mult_fo_im = (1 + ir_idx) ** exponent
    byhand_mult_fo_incr = byhand_mult_fo_im - 1
    exp_mult_fo_incr = 15 * d1
    self.assertEqual(exp_mult_fo_incr, byhand_mult_fo_incr)
    ret_mult_fo_incr = fm_mnts.calc_multiplier_for_increase_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_mult_fo_incr, ret_mult_fo_incr)

  def test_3_combine_the_2_multipliers(self) -> None:
    """
    The final montant can be taken either by adding 'increase' to inimontant or multiplying multiplier_for_fm:
      a) find the 'increase' and then add it to inimontant giving finalmontant;
      b) find the 'multiplier_for_fm' and then multiplies it by inimontant giving finalmontant;
    And/Or calculate it directly by its function direct function.
    """
    # ======================
    # hypothesis 3-1 -> let's take: inimontant, ir_idx, exponent = 1, 0.1, 2
    # (here multiplier_for_increase is less than 1 [0.21])
    # multiplier_for_fm = (1+0.1)**2=1.21 (because inimontant=1, finalmontant in this case is also 1.21)
    # multiplier_for_incr = 1.21 - 1 = 0.21 (the other approach [addition] -> 1 + 0.21 = 1.21)
    # Let's calculate fm (final montant) using the two approaches and compare the 2 results
    # ======================
    d1 = decimal_one
    onetenth, d2 = d1/10, 2 * d1
    inimontant, ir_idx, exponent = d1, onetenth, d2
    exp_final_montant = Decimal(1.21)  # direct value
    exp_final_montant = quantize6decplaces(exp_final_montant)
    byhand_final_montant = (1 + ir_idx) ** exponent  # do the math expression
    byhand_final_montant = quantize6decplaces(byhand_final_montant)
    self.assertEqual(exp_final_montant, byhand_final_montant)  # compare "by hand" with expected
    increase_amount = fm_mnts.calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent
    )
    final_montant_by_addition = inimontant + increase_amount
    self.assertEqual(exp_final_montant, final_montant_by_addition)  # compare "by addition" with expected
    multiplier_for_fm = fm_mnts.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    final_montant_by_multiplication = inimontant * multiplier_for_fm
    self.assertEqual(final_montant_by_multiplication, final_montant_by_addition)  # compare "by addition" with "by mult"
    final_montant_direct = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(final_montant_by_multiplication, final_montant_direct)  # compare "by mult" with direct-function
    # ======================
    # hypothesis 3-2 -> let's take: inimontant, ir_idx, exponent = 75, 3.75, 2.5
    # (here multiplier_for_increase is greater than 1 [49.173828])
    # multiplier_for_fm = (1+3)**2.5=49.17382870681822
    # multiplier_for_incr = 49.17382870681822 - 1 = 48.17382870681822
    # Let's calculate fm (final montant) using the two approaches and compare the 2 results
    # ======================
    inimontant, ir_idx, exponent = 75 * d1, Decimal(3.75), Decimal(2.5)
    exp_final_montant = Decimal(3688.0371530113666)  # direct value 75 * 49.17382870681822
    exp_final_montant = quantize6decplaces(exp_final_montant)
    byhand_final_montant = inimontant * (1 + ir_idx) ** exponent  # do the math expression
    byhand_final_montant = quantize6decplaces(byhand_final_montant)
    self.assertEqual(exp_final_montant, byhand_final_montant)  # compare "by hand" with expected
    increase_amount = fm_mnts.calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent
    )
    final_montant_by_addition = inimontant + increase_amount
    final_montant_by_addition = quantize6decplaces(final_montant_by_addition)
    self.assertEqual(exp_final_montant, final_montant_by_addition)  # compare "by addition" with expected
    multiplier_for_fm = fm_mnts.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    final_montant_by_multiplication = inimontant * multiplier_for_fm
    final_montant_by_multiplication = quantize6decplaces(final_montant_by_multiplication)
    self.assertEqual(final_montant_by_multiplication, final_montant_by_addition)  # compare "by addition" with "by mult"
    final_montant_direct = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent
    )
    final_montant_direct = quantize6decplaces(final_montant_direct)
    self.assertEqual(final_montant_by_multiplication, final_montant_direct)  # compare "by mult" with direct-function


  def test_4_crossing_functions_back_n_forth(self) -> None:
    """
    Crossing related functions back and forth.

    For one example:
      we can test calculations of finalmontant 'crossing' the 2 functions below:
        calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo()
        calc_finalmontant_w_1inimontant_2iridx_3expo()
    """
    # ======================
    # hypothesis 4-1 -> let's take: inimontant, ir_idx, exponent = 1, 0.1, 2
    # and compare calculations of fm (final montant) with addition and the direct function
    # ======================
    d1 = decimal_one
    onetenth, d2 = d1/10, 2 * d1
    inimontant, ir_idx, exponent = d1, onetenth, d2
    exp_final_montant = Decimal(1.21)  # direct value
    exp_final_montant = quantize6decplaces(exp_final_montant)
    byhand_final_montant = (1 + ir_idx) ** exponent  # do the math expression
    byhand_final_montant = quantize6decplaces(byhand_final_montant)
    self.assertEqual(exp_final_montant, byhand_final_montant)
    ret_increase_amount = fm_mnts.calc_incr_amt_intrstrt_w_1inimomtant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent,
    )
    ret_increase_amount = quantize6decplaces(ret_increase_amount)
    added_final_montant = ret_increase_amount + inimontant
    self.assertEqual(exp_final_montant, added_final_montant)
    ret_final_montant = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent,
    )
    ret_final_montant = quantize6decplaces(ret_final_montant)
    self.assertEqual(added_final_montant, ret_final_montant)

  def test_5_exponent_series(self) -> None:
    """
    Unit-test with 'produtory' i.e., with a list of exponents (the multipliers are multiplied)
      or a summing of the exponents
      (multiplying to summed exponents is the same as multiplying the factors each raised to its own exponent):
        example:
          (a ** b) * (a ** c) = a ** (b + c)
          (2 ** 3) * (2 ** 4) = 8 * 16 = 128
          2 ** (3 + 4) = 2 ** 7 = 128
    """
    # ======================
    # hypothesis 5-1 -> inimontant, ir_idx = 1, 1/10; exponent_series = [2,  4]
    # ======================
    d1 = decimal_one
    onetenth, d2 = d1/10, 2 * d1
    inimontant, ir_idx = d1, onetenth
    exponent_series = [d2,  2 * d2]
    byhand_finalmontant = (1 + ir_idx) ** sum(exponent_series)
    byhand_finalmontant = inimontant * byhand_finalmontant
    increase_amount = fm_mnts.calc_incr_amt_w_1inimontant_2iridx_3exposeries(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exposeries=exponent_series,
    )
    added_finalmontant = inimontant + increase_amount
    self.assertEqual(byhand_finalmontant, added_finalmontant)
    ret_finalmontant = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_3exposeries(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exposeries=exponent_series,
    )
    self.assertEqual(ret_finalmontant, added_finalmontant)
    # ======================
    # hypothesis 5-2 -> sane as above with greater numbers
    # inimontant, ir_idx = 5, 3.25; exponent_series = [2.3,  1.75]
    # ======================
    inimontant, ir_idx = 500 * d1, Decimal(3.25)
    exponent_series = [Decimal(2.3), Decimal(1.75), Decimal(3.21)]
    byhand_finalmontant = (1 + ir_idx) ** sum(exponent_series)
    byhand_finalmontant = inimontant * byhand_finalmontant
    increase_amount = fm_mnts.calc_incr_amt_w_1inimontant_2iridx_3exposeries(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exposeries=exponent_series,
    )
    added_finalmontant = inimontant + increase_amount
    self.assertEqual(byhand_finalmontant, added_finalmontant)
    ret_finalmontant = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_3exposeries(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exposeries=exponent_series,
    )
    self.assertEqual(ret_finalmontant, added_finalmontant)

  def test_6_series_indices_n_exponents(self):
    # ======================
    # hypothesis 6-1 -> tuplelist_iridx_n_expo = [(0.1, 0.5), (0.075, 0.75), (0.11, 0.6667)]
    # ======================
    d1 = decimal_one
    tuplelist_iridx_n_expo = [
      (Decimal(.1), Decimal(.5)),
      (Decimal(0.075), Decimal(.75)),
      (Decimal(0.11), Decimal(.6667)),
    ]
    t = tuplelist_iridx_n_expo
    byhandret_incrfactor = (1+t[0][0])**t[0][1]
    byhandret_incrfactor *= (1+t[1][0])**t[1][1]
    byhandret_incrfactor *= (1+t[2][0])**t[2][1]
    ret_incrfactor = fm_mnts.calc_multiplicationfactor_fo_fm_w_1param_iridx_n_exponent_tuplelist(
      tuplelist_iridx_n_expo
    )
    self.assertEqual(ret_incrfactor, byhandret_incrfactor)
    inimontant = 500 * d1
    ret_incr_amount = fm_mnts.calc_increase_amount_w_1param_iridx_n_exponent_tuplelist(
      inimontant, tuplelist_iridx_n_expo
    )
    # ======================
    # hypothesis 6-2 -> compare final_montant both by sum and by multiplication
    # ======================
    finalmontant_by_sum = inimontant + ret_incr_amount
    finalmontant_by_mul = inimontant * byhandret_incrfactor
    self.assertEqual(finalmontant_by_sum, finalmontant_by_mul)

  def test_7_with_monthpartition(self):
    """
    A month partition is a list of tuples where the latter
       contains the numbers of 'used days' and the month itself (represented by a 'refmonth' (*))

    (*) A refmonth is a date with day=1 and is useful for representing months.

    This information gives the exponent in the IR expression.
    Examples:
      a) if tuple is (15, '2026-04'), then exponent will be 15 (days) by 30 (total days in April) = 0.5
      b) if tuple is (3, '2026-01'), then exponent will be 3 (days) by 31 (total days in April) = 3/31

    partitionmonths: list[tuple[int, datetime.date]]
    """
    # ======================
    # hypothesis 7-1 -> with a monthpartition, compare multfactor_for_fm 'by hand' and by function
    # ======================
    mkdt = rmfs.make_refmonth_or_raise
    monthpartition = [
      (15,  mkdt('2026-04')),
      (3, mkdt('2026-01')),
    ]
    copied_monthpartition = monthpartition[:]
    d1 = decimal_one
    inimontant, ir_idx = 3 * d1, d1 / 10
    copied_inimontant = 3 * d1
    exponents = [Decimal(15/30), Decimal(3/31)]
    byhand_multfactor_for_fm = (1 + ir_idx)**exponents[0]
    byhand_multfactor_for_fm *= (1 + ir_idx)**exponents[1]
    ret_multfactor_for_fm, quinhoes2 = fm_mnts.calc_multiplicationfactor_fo_fm_w_1inimontant_2iridx_3partitionmonths(
      ir_idx=ir_idx,
      partitionmonths=monthpartition,
    )
    self.assertEqual(byhand_multfactor_for_fm, ret_multfactor_for_fm)
    # ======================
    # hypothesis 7-2 -> compare ... self.assertEqual(byhand_multfactor_for_incr, ret_multfactor_for_incr)
    # ======================
    ret_multfactor_for_incr, quinhoes1 = fm_mnts.calc_multiplicationfactor_fo_incr_w_1inimontant_2iridx_3partitionmonths(
      ir_idx=ir_idx,
      partitionmonths=monthpartition,
    )
    byhand_multfactor_for_incr = byhand_multfactor_for_fm - 1
    byhand_amount_increased = inimontant * byhand_multfactor_for_incr
    self.assertEqual(byhand_multfactor_for_incr, ret_multfactor_for_incr)
    # ======================
    # hypothesis 7-3 -> compare ... self.assertEqual(ret_amount_increased_by_mul, byhand_amount_increased)
    # ======================
    ret_amount_increased_by_mul = inimontant * ret_multfactor_for_incr
    ret_increase_amount, quinhoes1 = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3partitionmonths(
      inimontant=inimontant,
      ir_idx=ir_idx,
      partitionmonths=monthpartition,
    )
    self.assertEqual(ret_amount_increased_by_mul, ret_increase_amount)
    self.assertEqual(ret_amount_increased_by_mul, byhand_amount_increased)
    # ======================
    # hypothesis 7-4 -> compare ... self.assertEqual(byhand_finalmontant, ret_finalmontant_direct)
    # ======================
    byhand_finalmontant = inimontant * byhand_multfactor_for_fm
    ret_finalmontant_direct, quinhoes1 = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_3partitionmonths(
      inimontant=inimontant,
      ir_idx=ir_idx,
      partitionmonths=monthpartition,
    )
    self.assertEqual(copied_monthpartition, monthpartition)
    self.assertEqual(copied_inimontant, inimontant)
    self.assertEqual(ir_idx, d1/10)
    self.assertEqual(byhand_finalmontant, ret_finalmontant_direct)
    ret_finalmontant_by_sum = inimontant + ret_increase_amount
    ret_multfactor_for_fm, quinhoes1 = fm_mnts.calc_multiplicationfactor_fo_fm_w_1inimontant_2iridx_3partitionmonths(
      ir_idx=ir_idx,
      partitionmonths=monthpartition,
    )
    ret_finalmontant_by_mul = inimontant * ret_multfactor_for_fm
    self.assertEqual(ret_finalmontant_by_sum, ret_finalmontant_by_mul)
    # ======================
    # hypothesis 7-4 -> compare ... quinhões
    # quinhões have some differences: study them better so that we can unit-test them
    # ======================
"""
    self.assertEqual(quinhoes1, quinhoes2)
    # self.assertEqual(quinhoes1, quinhoes2)
"""
