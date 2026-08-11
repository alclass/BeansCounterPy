import unittest
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants as fm_mnts  # fm_cmnts.calc_incrfactor_intrstrt_w_1iridx_2expo
import datetime
from decimal import Decimal
from lib.fncfs.credeb_pkg.credit_debit_fs import debit_or_credit_value_to_accounts
decimal_zero = Decimal('0.0')
decimal_one = Decimal('1.0')


class TestCase1(unittest.TestCase):

  def test_1_1_multiplier_for_fm(self) -> None:
    # ======================
    # hypothesis 1-1-1
    # multiplier=(1+1)**1=2
    # ======================
    d0, d1, d2 = decimal_zero, decimal_one, 2 * decimal_one
    ir_idx, exponent = d1, d1
    byhand_incrfactor = (1 + ir_idx) ** exponent  # (1+1)**1=2
    exp_increase_factor = d2
    self.assertEqual(exp_increase_factor, byhand_incrfactor)
    ret_increase_factor = fm_mnts.calc_multiplier_for_increase_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_increase_factor, ret_increase_factor)
    # ======================
    # hypothesis 1-1-2
    # (1+3)**2=16
    # ======================
    dec3, dec16 = 3 * d1, 16 * d1
    ir_idx, exponent = dec3, d2
    byhand_incrfactor = (1 + ir_idx) ** exponent  # (1+3)**2=16
    exp_increase_factor = dec16
    self.assertEqual(exp_increase_factor, byhand_incrfactor)
    ret_increase_factor = fm_mnts.calc_multiplier_for_increase_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_increase_factor, ret_increase_factor)

  def test_1_2_multiplier_for_increase(self) -> None:
    # ======================
    # hypothesis 1-2-1
    # (1+0.1)**2=1.21
    # 1.21 - 1 = 0.21 (21%)
    # ======================
    d0, d1 = decimal_zero, decimal_one
    d2 = 2 * d1
    ir_idx, exponent = d1/10, d2
    byhand_mult_fo_incr = (1 + ir_idx) ** exponent - d1
    exp_increase_factor = Decimal('0.21')
    self.assertEqual(exp_increase_factor, byhand_mult_fo_incr)
    ret_increase_factor = fm_mnts.calc_multiplier_for_increase_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_increase_factor, ret_increase_factor)
    # ======================
    # hypothesis 1-2-2
    # mult_for_im = (1+3)**2=16
    # mult_for_im = (16-1)/16
    # 1.21 - 1 = 0.21 (21%)
    # ======================
    d0, d1 = decimal_zero, decimal_one
    d2 = 2 * d1
    ir_idx, exponent = d1/10, d2
    byhand_mult_fo_im = (1 + ir_idx) ** exponent
    byhand_mult_fo_incr = (byhand_mult_fo_im - 1) / byhand_mult_fo_im
    exp_increase_factor = 15*d1 / (16*d1)
    self.assertEqual(exp_increase_factor, byhand_mult_fo_incr)
    ret_increase_factor = fm_mnts.calc_multiplier_for_increase_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_increase_factor, ret_increase_factor)
    # ======================
    # hypothesis 1-2-2
    # mult_for_im = (1+3)**2=16
    # mult_for_im = (16-1)/16
    # 1.21 - 1 = 0.21 (21%)
    # ======================
    # ======================
    # (1+3)**2=16
    # ======================

  def atest_1_3_join_the_2_multipliers(self) -> None:
    """
    The final montant can be taken as a 2-step operation, i.e.,
      a) find the multiplier for increase
      b) then multiplies it by inimontant
    Or calculate it directly by its function
      (the direct calculation does a multiplying by multiplier for im)
    """
    # hypothesis 1-3
    # fm = 1*(1+1)**1=2
    inimontant, ir_idx, exponent = decone, decone, decone
    byhand_finalmontant = 1 * (1 + ir_idx) ** exponent
    exp_finalmontant = dectwo
    self.assertEqual(exp_finalmontant, byhand_finalmontant)
    ret_finalmontant = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_finalmontant, ret_finalmontant)
    # hypothesis 1-4
    # fm = 2*(1+1)**1=4
    d0, d1 = decimal_zero, decimal_one
    d2, d4 = 2 * d1, 4 * d1
    exp_finalmontant = d4
    inimontant, ir_idx, exponent = d2, d1, d1
    byhand_finalmontant = inimontant * (1 + ir_idx) ** exponent
    self.assertEqual(exp_finalmontant, byhand_finalmontant)
    ret_finalmontant = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_3expo(
      inimontant=inimontant,
      ir_idx=ir_idx,
      exponent=exponent
    )
    self.assertEqual(exp_finalmontant, ret_finalmontant)
    # hypothesis 1-5
    # using the 'monthsduration' version
    fixir = decimal_one/2
    varir = decimal_one/2
    monthduration = exponent
    r2_finalmontant = fm_mnts.calc_finalmontant_w_1inimontant_2fixir_3varir_4monthsduration(
      inimontant=inimontant,
      fixir=ir_idx,
      varir=d0,
      monthsduration=exponent,
    )
    self.assertEqual(exp_finalmontant, r2_finalmontant)

  def atest_2_finalmontant(self) -> None:
    # hypothesis 2-1
    # we unit-test 'produtory' doing it the two ways and comparing results
    decone = decimal_one
    dectwo = 2 * decimal_one
    tuplelist_iridx_n_expo = [(decone, dectwo), (dectwo, decone)]
    # step 1: calculate incr_factor for pair (1, 2) -> i_f=(1+1)**2=4
    ir_idx, exponent = decone, dectwo
    byhand = (1 + ir_idx) ** exponent
    incrfact1 = fm_mnts.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent,
    )
    # self.assertEqual(byhand, incrfact1)
    # step 2: calculate incr_factor for (2, 1) -> i_f=(1+2)**1=3
    ir_idx, exponent = dectwo, decone
    byhand = (1 + ir_idx) ** exponent
    incrfact2 = fm_mnts.calc_multiplier_for_fm_intrstrt_w_1iridx_2expo(
      ir_idx=ir_idx,
      exponent=exponent,
    )
    exp_compounded = incrfact1 * incrfact2
    ret_compounded = fm_mnts.calc_finalmontant_w_1inimontant_2iridx_n_expo_zippedtuplelist(
      inimontant=decone,
      tuplelist_iridx_n_expo=tuplelist_iridx_n_expo
    )
    self.assertEqual(exp_compounded, ret_compounded)
