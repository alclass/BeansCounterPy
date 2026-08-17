from decimal import Decimal
import functools
import operator
import unittest
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants as fm_mnts  # fm_cmnts.calc_incrfactor_intrstrt_w_1iridx_2expo
import lib.fncfs.fncmathfs.unittests.adhoctests_fncmaths as adhoc  # adhoc.make_random_inimontants
import lib.datesetc.refmonth_fs as rmfs
import lib.datesetc.datefs as dtfs
mkdt = dtfs.make_date_or_raise
mkrm = rmfs.make_refmonth_or_raise
DECIMAL_ONE = Decimal('1.0')
quant = fm_mnts.quant
q4 = fm_mnts.q4
q8 = fm_mnts.q8
make_random_inimontants = adhoc.make_random_inimontants
make_random_tuplelist_iridx_exponent = adhoc.make_random_tuplelist_iridx_exponent
# CRITICAL: This hides the helper's internal traceback frames from the error output
__unittest = True

class TestCase1(unittest.TestCase):


  def assertDecimalIsClose(self, dec1: Decimal, dec2: Decimal, msg="in assertDecimalIsClose"):
    """Custom assertion to check decimal is close."""
    boolval =  fm_mnts.dec_is_close(dec1, dec2)
    if not boolval:
      # Create a descriptive, standard error message
      err_standard_msg = f"{dec1} is not close to {dec2}"
      # Combine your standard message with the user's optional custom message
      full_msg = self._formatMessage(msg, err_standard_msg)
      # Trigger the official test failure
      self.fail(full_msg)

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
    d1, d2 = DECIMAL_ONE, 2 * DECIMAL_ONE
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
    byhand_mult_fo_fm = quant(byhand_mult_fo_fm)
    exp_mult_fo_fm = Decimal('6.131576709333357')
    exp_mult_fo_fm = quant(exp_mult_fo_fm)
    self.assertEqual(exp_mult_fo_fm, byhand_mult_fo_fm)
    ret_mult_fo_fm = fm_mnts.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    ret_mult_fo_fm = quant(ret_mult_fo_fm)
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
    # d0, d1 = decimal_zero, decimal_one
    d1 = DECIMAL_ONE
    d2 = 2 * d1
    ir_idx, exponent = d1/10, d2
    byhand_mult_fo_incr = (1 + ir_idx) ** exponent - d1
    exp_mult_fo_incr = Decimal('0.21')
    self.assertEqual(exp_mult_fo_incr, byhand_mult_fo_incr)
    ret_mult_fo_incr = fm_mnts.calc_multiplier_for_increase_w_1iridx_2expo(
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
    ret_mult_fo_incr = fm_mnts.calc_multiplier_for_increase_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_mult_fo_incr, ret_mult_fo_incr)

  def test_3_combine_the_2_multipliers(self) -> None:
    """
    The final montant can be taken either by adding 'increase' to inimontant
      or multiplying multiplier_for_fm by inimontant:
        a) find the 'increase' and then add it to inimontant giving finalmontant;
        b) find the 'multiplier_for_fm' and then multiplies it by inimontant giving finalmontant;
    And/or calculate it directly by its direct function.
    """
    # ======================
    # hypothesis 3-1 -> let's take: inimontant, ir_idx, exponent = 1, 0.1, 2
    # (here multiplier_for_increase is less than 1 -> (1 + 0.1) ** 2 - 1 = 0.21)
    # multiplier_for_fm = (1+0.1)**2=1.21 (because inimontant=1, finalmontant in this case is also 1.21)
    # multiplier_for_incr = 1.21 - 1 = 0.21 (the other approach [addition] -> 1 + 0.21 = 1.21)
    # Let's calculate fm (final montant) using the two approaches and compare the 2 results
    # ======================
    d1 = DECIMAL_ONE
    onetenth, d2 = d1/10, 2 * d1
    inimontant, ir_idx, exponent = d1, onetenth, d2
    exp_final_montant = Decimal(1.21)  # direct value
    exp_final_montant = quant(exp_final_montant)
    byhand_final_montant = (1 + ir_idx) ** exponent  # do the math expression
    byhand_final_montant = quant(byhand_final_montant)
    self.assertEqual(exp_final_montant, byhand_final_montant)  # compare "by hand" with expected
    increase_amount = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3expo(
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
    final_montant_direct = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3expo(
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
    exp_final_montant = quant(exp_final_montant)
    byhand_final_montant = inimontant * (1 + ir_idx) ** exponent  # do the math expression
    byhand_final_montant = quant(byhand_final_montant)
    self.assertEqual(exp_final_montant, byhand_final_montant)  # compare "by hand" with expected
    increase_amount = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent
    )
    final_montant_by_addition = inimontant + increase_amount
    final_montant_by_addition = quant(final_montant_by_addition)
    self.assertEqual(exp_final_montant, final_montant_by_addition)  # compare "by addition" with expected
    multiplier_for_fm = fm_mnts.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    final_montant_by_multiplication = inimontant * multiplier_for_fm
    final_montant_by_multiplication = quant(final_montant_by_multiplication)
    self.assertEqual(final_montant_by_multiplication, final_montant_by_addition)  # compare "by addition" with "by mult"
    final_montant_direct = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent
    )
    final_montant_direct = quant(final_montant_direct)
    self.assertEqual(final_montant_by_multiplication, final_montant_direct)  # compare "by mult" with direct-function


  def test_4_crossing_functions_back_n_forth(self) -> None:
    """
    Verifying 'crossing' related functions 'back and forth'.

    For one example:
      we can test calculations of finalmontant 'crossing' the 2 functions below:
        calc_increase_amount_w_1inimomtant_2iridx_3expo()
        calc_finalmontant_w_1inimontant_2iridx_3expo()
    """
    # ======================
    # hypothesis 4-1 -> let's take: inimontant, ir_idx, exponent = 1, 0.1, 2
    # and compare calculations of fm (final montant) with addition and the direct function
    # ======================
    d1 = DECIMAL_ONE
    onetenth, d2 = d1/10, 2 * d1
    inimontant, ir_idx, exponent = d1, onetenth, d2
    exp_final_montant = Decimal(1.21)  # direct value
    exp_final_montant = quant(exp_final_montant)
    byhand_final_montant = (1 + ir_idx) ** exponent  # do the math expression
    byhand_final_montant = quant(byhand_final_montant)
    self.assertEqual(exp_final_montant, byhand_final_montant)
    ret_increase_amount = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent,
    )
    ret_increase_amount = quant(ret_increase_amount)
    added_final_montant = ret_increase_amount + inimontant
    self.assertEqual(exp_final_montant, added_final_montant)
    ret_final_montant = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent,
    )
    ret_final_montant = quant(ret_final_montant)
    self.assertEqual(added_final_montant, ret_final_montant)

  def test_5_exponent_series(self) -> None:
    """
    Unit-test with 'produtory' i.e., with a list of exponents (the multipliers are multiplied up)
      (or a summing of the exponents before exponentiation)
      (multiplying to summed exponents is the same as multiplying the factors each raised to its own exponent):
        example:
          a) with literals
            (a ** b) * (a ** c) = a ** (b + c)
          b) with numbers
            (2 ** 3) * (2 ** 4) = 8 * 16 = 128
            2 ** (3 + 4) = 2 ** 7 = 128
    """
    # ======================
    # hypothesis 5-1 -> inimontant, ir_idx = 1, 1/10; exponent_series = [2,  4]
    # ======================
    d1 = DECIMAL_ONE
    onetenth, d2 = d1/10, 2 * d1
    inimontant, ir_idx = d1, onetenth
    exponent_series = [d2,  2 * d2]
    byhand_finalmontant = (1 + ir_idx) ** sum(exponent_series)
    byhand_finalmontant = inimontant * byhand_finalmontant
    increase_amount = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3exposeries(
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
    increase_amount = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3exposeries(
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
    d1 = DECIMAL_ONE
    tuplelist_iridx_n_expo = [
      (Decimal(.1), Decimal(.5)),
      (Decimal(0.075), Decimal(.75)),
      (Decimal(0.11), Decimal(.6667)),
    ]
    t = tuplelist_iridx_n_expo
    byhandret_incrfactor = (1+t[0][0])**t[0][1]
    byhandret_incrfactor *= (1+t[1][0])**t[1][1]
    byhandret_incrfactor *= (1+t[2][0])**t[2][1]
    ret_incrfactor, multfactors = fm_mnts.calc_multiplicationfactor_for_fm_w_1tuplelist_iridx_n_exponent(
      tuplelist_iridx_n_expo
    )
    ret_incrfactor, byhandret_incrfactor = q8(ret_incrfactor), q8(byhandret_incrfactor)
    self.assertEqual(ret_incrfactor, byhandret_incrfactor)
    multfactors_multipliedup = functools.reduce(operator.mul, multfactors, 1)
    # noinspection bad-argument-type
    multfactors_multipliedup = Decimal(multfactors_multipliedup)
    self.assertEqual(ret_incrfactor, q8(multfactors_multipliedup))
    inimontant = 500 * d1
    ret_incr_amount, quinhoes = fm_mnts.calc_increase_amount_w_1inimontant_2tuplelist_iridx_n_exponent(
      inimontant, tuplelist_iridx_n_expo
    )
    # ======================
    # hypothesis 6-2 -> compare final_montant both by sum and by multiplication
    # ======================
    finalmontant_by_sum = inimontant + ret_incr_amount
    finalmontant_by_mul = inimontant * byhandret_incrfactor
    self.assertEqual(q4(finalmontant_by_sum), q4(finalmontant_by_mul))
    total_quinhoes = sum(quinhoes)
    self.assertEqual(ret_incr_amount, total_quinhoes)

  def test_7_with_monthpartition(self):
    """

    The first explanation here has to do with decimal places (and their problems with asserting equality)
    =====================
    This unit-test had problems with decimal places, some assertions had 2 or 3 decimal places to pass,
      and this precision-setting was done with dec.quantize().
      This solution failed to be proper for numbers on different scales (too big or too small).

    After this, one solution has been found (the is_close()) and one test (at the time of writing)
      is already asserting with custom-method assertDecimalIsClose().
    In time, the idea is to update all assertions that got 'quantized' with the assertDecimalIsClose(),
      and avoid using the quantize() approach.
    There is also one further initiative that uses sigfigs (significant figures).
    The function for this one (sigfigs) is available in the same module as is
      assertDecimalIsClose()'s underlying dec_is_close() function.

    What is a monthpartition?
    =========================
      A month partition is a list of tuples which
         contains the numbers of 'used days' and their corresponding months (represented by 'refmonths' (*))

    (*) A refmonth is a date with day=1 and is useful for representing months.

    The tuple contains 'days used' and 'total days' which gives the exponent in the IR expression.

    Examples:
      a) if tuple is (15, '2026-04'), then exponent will be 15 (days) by 30 (total days in April) = 0.5
      b) if tuple is (3, '2026-01'), then exponent will be 3 (days) by 31 (total days in April) = 3/31
        3/31 = 0.0967741935483871

    partitionmonths: list[tuple[int, datetime.date]]
    """
    # ======================
    # hypothesis 7-1 -> with a monthpartition, compare multfactor_for_fm 'by hand' and by function
    # ======================
    monthpartition = [
      (15,  mkrm('2026-04')),
      (3, mkrm('2026-01')),
    ]
    copied_monthpartition = monthpartition[:]
    d1 = DECIMAL_ONE
    inimontant, ir_idx = 3 * d1, d1 / 10
    copied_inimontant = 3 * d1
    exponents = [15 * d1 / 30, 3 * d1 / 31]
    byhand_multfactor_for_fm = (1 + ir_idx)**exponents[0]
    byhand_multfactor_for_fm *= (1 + ir_idx)**exponents[1]
    ret_multfactor_for_fm, quinhoes2 = fm_mnts.calc_multiplicationfactor_for_fm_w_1iridx_2monthpartition(
      ir_idx=ir_idx,
      monthpartition=monthpartition,
    )
    byhand_multfactor_for_fm, ret_multfactor_for_fm = \
      quant(byhand_multfactor_for_fm), quant(ret_multfactor_for_fm)
    # the 'two sides' got quantized for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(byhand_multfactor_for_fm, ret_multfactor_for_fm)
    # ======================
    # hypothesis 7-2 -> compare ... self.assertEqual(byhand_multfactor_for_incr, ret_multfactor_for_incr)
    # ======================
    ret_multfactor_for_incr, quinhoes1 = fm_mnts.calc_multiplicationfactor_for_increase_w_1iridx_2monthpartition(
      ir_idx=ir_idx,
      monthpartition=monthpartition,
    )
    byhand_multfactor_for_incr = byhand_multfactor_for_fm - 1
    byhand_amount_increased = inimontant * byhand_multfactor_for_incr
    byhand_multfactor_for_fm = quant(byhand_multfactor_for_fm)
    ret_multfactor_for_incr = quant(ret_multfactor_for_incr)
    # the 'two sides' got quantized for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(byhand_multfactor_for_incr, ret_multfactor_for_incr)
    # ======================
    # hypothesis 7-3 -> compare ... self.assertEqual(ret_amount_increased_by_mul, byhand_amount_increased)
    # ======================
    ret_amount_increased_by_mul = inimontant * ret_multfactor_for_incr
    ret_increase_amount, quinhoes1 = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3monthpartition(
      inimontant=inimontant,
      ir_idx=ir_idx,
      monthpartition=monthpartition,
    )
    ret_amount_increased_by_mul = quant(ret_amount_increased_by_mul, 2)
    ret_increase_amount = quant(ret_increase_amount, 2)
    # the 'two sides' got quantized for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(ret_amount_increased_by_mul, ret_increase_amount)
    self.assertEqual(ret_increase_amount, quant(byhand_amount_increased, 2))
    # ======================
    # hypothesis 7-4 -> compare ... self.assertEqual(byhand_finalmontant, ret_finalmontant_direct)
    # ======================
    byhand_finalmontant = inimontant * byhand_multfactor_for_fm
    _, quinhoes1 = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3monthpartition(
      inimontant=inimontant,
      ir_idx=ir_idx,
      monthpartition=monthpartition,
    )
    self.assertEqual(copied_monthpartition, monthpartition)
    self.assertEqual(copied_inimontant, inimontant)
    self.assertEqual(ir_idx, d1/10)
    byhand_finalmontant = quant(byhand_finalmontant, 2)
    ret_finalmontant = ret_increase_amount + inimontant
    ret_finalmontant = quant(ret_finalmontant, 2)
    # the 'two sides' got quantized for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(byhand_finalmontant, ret_finalmontant)
    ret_finalmontant_by_sum = inimontant + ret_increase_amount
    ret_multfactor_for_fm, quinhoes1 = fm_mnts.calc_multiplicationfactor_for_fm_w_1iridx_2monthpartition(
      ir_idx=ir_idx,
      monthpartition=monthpartition,
    )
    ret_finalmontant_by_mul = inimontant * ret_multfactor_for_fm
    # one of them was set with 2 decimal places above, so the other will have too
    ret_finalmontant_by_mul = quant(ret_finalmontant_by_mul, 2)
    ret_finalmontant_by_sum = quant(ret_finalmontant_by_sum, 2)
    # the 'two sides' got quantized for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(q4(ret_finalmontant_by_sum), q4(ret_finalmontant_by_mul))
    # ======================
    # hypothesis 7-5 -> compare ... quinhões
    # quinhoes have some differences: study them better so that we can unit-test them
    # ======================
    inimontant, ir_idx = 3 * d1, d1 / 10
    iridxlist = [ir_idx, ir_idx]
    # byhand_finalmontant = inimontant * byhand_multfactor_for_fm
    ret_finalmontant_direct, quinhoes = fm_mnts.calc_finmontant_w_1inimontant_2iridxlist_3monthpartition(
      inimontant=inimontant, iridxlist=iridxlist, monthpartition=monthpartition,
    )
    self.assertEqual(quant(ret_finalmontant_direct, 2), quant(byhand_finalmontant, 2))
    # ======================
    # hypothesis 7-6 -> compare the 'simple' case of calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth()
    # because the quinhoes returned, for only one period, contains also its corresponding increase_amount
    # ======================
    d1 = DECIMAL_ONE
    inimontant, ir_idx = 3 * d1, d1 / 10
    inidate, findate = mkdt('2026-1-15'), mkdt('2026-1-31')
    finmontant_by_samemonth_fn, quinhoes = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3inidate_4findate_samemonth(
      inimontant=inimontant, ir_idx=ir_idx, inidate=inidate, findate=findate,
    )
    monthsfraction = (31-15+1) * d1 / 31  # (31-15+1) (used) days in the 31-day month
    finmontant_by_direct_fn = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant, ir_idx=ir_idx, exponent=monthsfraction,
    )
    increase_amount = finmontant_by_direct_fn - inimontant
    self.assertDecimalIsClose(increase_amount, quinhoes[0], msg="testing via exponent from samemonth")
    self.assertDecimalIsClose(finmontant_by_direct_fn, finmontant_by_samemonth_fn, msg="testing via exponent from samemonth")


  def test_8_with_quinhoes(self):
    """
    Contains general tests with quinhões (additive) or multiplier factors (multiplicative).
    """
    # ======================
    # hypothesis 8-1 -> verify that each quinhão in quinhões adds up to increase_amount
    # ======================
    monthpartition = [
      (15,  mkrm('2026-04')),
      (3, mkrm('2026-01')),
    ]
    d1  = DECIMAL_ONE
    inimontant, ir_idx = 3 * d1, d1 / 10
    iridxlist = [ir_idx, ir_idx]
    ret_finalmontant_direct, quinhoes = fm_mnts.calc_finmontant_w_1inimontant_2iridxlist_3monthpartition(
      inimontant=inimontant, iridxlist=iridxlist, monthpartition=monthpartition,
    )
    increase_amounts_by_quinhoes = Decimal(sum(quinhoes))
    increase_amount_by_subtraction = ret_finalmontant_direct - inimontant
    # only 'one side' got quantized for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(increase_amount_by_subtraction, q4(increase_amounts_by_quinhoes))
    # ======================
    # hypothesis 8-2 -> compare ret_multfactor_for_incr from the function above and the one below
    # ======================
    ret_multfactor_for_fm, multifactors_for_fm = fm_mnts.calc_multiplicationfactor_for_fm_w_1iridx_2monthpartition(
      ir_idx=ir_idx, monthpartition=monthpartition,
    )
    comp_multfactgor_for_fm = ret_finalmontant_direct / inimontant
    self.assertEqual(q4(comp_multfactgor_for_fm), q4(ret_multfactor_for_fm))
    # ======================
    # hypothesis 8-3 -> compare and verify that quinhões is consistent with multiplicationfactors
    # ======================
    increase_amount_via_quin = quinhoes[0]
    increase_amount_via_mfact = inimontant * (multifactors_for_fm[0] - 1)
    # set decimal places to 4 for the two
    increase_amount_via_quin, increase_amount_via_mfact = q4(increase_amount_via_quin), q4(increase_amount_via_mfact)
    self.assertEqual(increase_amount_via_quin, increase_amount_via_mfact)
    # ======================
    # hypothesis 8-4 -> simulate various (single) calculations and compare them with quinhões
    # ======================
    inimontant_1, ir_idx = 100 * d1, d1/10
    exponents = [Decimal(15)/ Decimal(30), Decimal(3) / Decimal(31)]
    exponent = exponents[0]  # Decimal(15)/ Decimal(30)
    increase_parcel_1 = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3expo(
      inimontant=inimontant_1, ir_idx=ir_idx, exponent=exponent,
    )
    inimontant_2 = inimontant_1 + increase_parcel_1
    exponent = exponents[1]  # Decimal(3) / Decimal(31)
    increase_parcel_2 = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3expo(
      inimontant=inimontant_2, ir_idx=ir_idx, exponent=exponent,
    )
    iridxlist = [ir_idx, ir_idx]
    monthpartition = [(15,  mkrm('2026-04')), (3, mkrm('2026-01')),]
    ret_finalmontant_direct, quinhoes = fm_mnts.calc_finmontant_w_1inimontant_2iridxlist_3monthpartition(
      inimontant=inimontant_1, iridxlist=iridxlist, monthpartition=monthpartition,
    )
    increase_amounts_by_quinhoes = Decimal(sum(quinhoes))
    increase_parcel = increase_parcel_1 + increase_parcel_2
    self.assertEqual(q4(increase_parcel), q4(increase_amounts_by_quinhoes))
    self.assertEqual(q4(increase_parcel_1), q4(quinhoes[0]))
    self.assertEqual(q4(increase_parcel_2), q4(quinhoes[1]))
    # ======================
    # hypothesis 8-5 -> continuing from the latter, verify final_montant on the 2 sides (piecemeal and monthpartition)
    # ======================
    piecemeal_finalmontant = inimontant_2 + increase_parcel_2
    self.assertEqual(ret_finalmontant_direct, q4(piecemeal_finalmontant))
    # ======================
    # hypothesis 8-5 -> for a longer/larger and random quinhoes, compare it to function results
    #   self.assertEqual(aggregate_incr_amount, quinhoes)
    # ======================
    n, param_hi, param_lo = 10, 100, 10
    inimontants = make_random_inimontants(n=n, param_hi=param_hi, param_lo=param_lo)
    ir_range, exp_range = (0.005, 1.345), (0.45, 15.468)
    for inimontant in inimontants:
      tuplelist_iridx_exponent = make_random_tuplelist_iridx_exponent(n=n, ir_range=ir_range, exp_range=exp_range)
      ongoingmontant, byhand_quinhoes = inimontant, []
      for tupl in tuplelist_iridx_exponent:
        ir_idx, exponent = tupl
        incr_amt = fm_mnts.calc_increase_amount_w_1inimontant_2iridx_3expo(
          inimontant=ongoingmontant, ir_idx=ir_idx, exponent=exponent,
        )
        byhand_quinhoes.append(incr_amt)
        ongoingmontant = ongoingmontant + incr_amt
      ret_incr_amt, ret_quinhoes = fm_mnts.calc_increase_amount_w_1inimontant_2tuplelist_iridx_n_exponent(
        inimontant=inimontant,
        tuplelist_iridx_n_expo=tuplelist_iridx_exponent
      )
      exp_incr_amt = Decimal(sum(byhand_quinhoes))
      self.assertDecimalIsClose(exp_incr_amt, ret_incr_amt)


  def test_9_invert_exponent_etal(self):
    """
    Contains tests on the 'idea' that
      applying an inverse function go a function returns its argument,
      i.e., f_inv ( f(x) ) = x or f( f_inv(x) ) = x.
    """
    # ======================
    # hypothesis 9-1 -> doing f(f_inv(x))=x with exponent | backexponent (calculating 'back' exponent)
    # ======================
    d1 = DECIMAL_ONE
    ir_idx, exponent = d1/20, 3 * d1 / 2
    byhand_mult_for_fm = (1 + ir_idx) ** exponent
    byhand_mult_for_incr = byhand_mult_for_fm - 1
    multiplier_for_increase = fm_mnts.calc_multiplier_for_increase_w_1iridx_2expo(
      ir_idx=ir_idx, exponent=exponent,
    )
    self.assertEqual(quant(multiplier_for_increase), quant(byhand_mult_for_incr))
    backexponent = fm_mnts.calc_inv_exponent_w_1iridx_2multiplierforincrease(
      ir_idx=ir_idx, mult_for_incr=multiplier_for_increase
    )
    self.assertEqual(quant(backexponent), exponent)
    inimontant = 77 * d1
    finmontant = inimontant * (multiplier_for_increase + 1)
    backexponent = fm_mnts.calc_inv_exponent_w_1finmontant_2inimontant_3iridx(
      finmontant=finmontant, inimontant=inimontant, ir_idx=ir_idx)
    # only 'back' gets quantized for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(quant(backexponent), exponent)
    # ======================
    # hypothesis 9-2 -> doing f(f_inv(x))=x with ir_idx (calculating 'back' ir_idx)
    # ======================
    back_ir_idx = fm_mnts.calc_inv_iridx_w_1exponent_2multiplierforincrease(
      exponent=exponent, mult_for_incr=multiplier_for_increase
    )
    # idem: only 'back' gets quantized for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(quant(back_ir_idx), ir_idx)
    inimontant = 3257 * d1 / 7
    finmontant = inimontant * (multiplier_for_increase + 1)
    back_ir_idx = fm_mnts.calc_inv_irdix_w_1finmontant_2inimontant_3exponent(
      finmontant=finmontant, inimontant=inimontant, exponent=exponent)
    # idem: only 'back' gets quantized for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(quant(back_ir_idx), ir_idx)
    # ======================
    # hypothesis 9-3 -> doing f(f_inv(x))=x with inimontant -> f_inv(f(inimontant))=inimontant
    # ======================
    inimontant = 100 * d1
    finmontant = fm_mnts.calc_finmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant, ir_idx=ir_idx, exponent=exponent
    )
    backinimontant = fm_mnts.calc_inv_inimontant_w_1finmontant_2iridx_3exponent(
      finmontant=finmontant, ir_idx=ir_idx, exponent=exponent
    )
    # no quantizing was needed here for the assertEqual(), @see also assertions with assertDecimalIsClose()
    self.assertEqual(inimontant, backinimontant)
