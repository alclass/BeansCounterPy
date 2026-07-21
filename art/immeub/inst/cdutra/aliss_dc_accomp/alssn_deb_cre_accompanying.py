#!/usr/bin/env python3
"""
art/immeub/inst/cdutra/aliss_dc_accomp/alssn_deb_cre_accompanying.py

Strategy to treat 'fractions' (with repeating decimal)
=================

Choices might be:
  Fraction,
  decimal.Decimal,
  dinero.Dinero
  and round()
    every_float = round(every_float, 4)  # internal and DB
    then:  {every_float:0.2f}  # display

  Choosing Dinero
    remembering that the former choice was an 'int cents'  solution,
      which needs a duplication of attributes and a care in input and treatment.

from dataclasses import dataclass, field
from dinero import Dinero
@dataclass
class Transaction:
    amount: Dinero = field(default_factory=lambda: Dinero("10.50", "USD"))

import inspect
"""
import datetime
import decimal
from dinero import Dinero
from dataclasses import dataclass, field
import art.immeub.inst.cdutra.aliss_dc_accomp.accdata_deb_cre_alssn as accdt  # accdt.items
import lib.datesetc.refmonth_fs as rmfs
import lib.finfs.indices.indices_fetch_n_fs as ipfs  # ipfs.ipca_for_refmonth
VALOR_META_MENSAL_BRL = accdt.get_brl_dinero(500)
REFMONTH_INI_FOR_META = '2025-10'


def get_abs_dec_corrmone_n_intrst(inivalue, refmonth, fix=0.02):
  """
  The abs(inivalue) is taken so that the fraction returns as a positive number
  """
  inivalue = abs(inivalue.raw_amount)
  m_minus_2_rm = rmfs.make_refmonth_it_minus_n(refmonth, 2)
  ipca_dec = ipfs.ipca_for_refmonth(m_minus_2_rm)
  fix = decimal.Decimal(fix)
  ipca_dec = decimal.Decimal(ipca_dec)
  corrmone_n_intrst = inivalue * (fix + ipca_dec)
  return corrmone_n_intrst, ipca_dec


def get_as_dinero_dec_corrmone_n_intrst(inivalue, refmonth, fix=0.02):
  corrmone_n_intrst, ipca_dec = get_abs_dec_corrmone_n_intrst(inivalue, refmonth, fix)
  corrmone_n_intrst = accdt.get_brl_dinero(corrmone_n_intrst)
  return corrmone_n_intrst, ipca_dec


@dataclass
class DebCredAccompanier:
  """
  This class is conceptualized to make 'refmonths' run sequentially,
    i.e., one month feeds output into the subsequent next month input.

  Observation on 'putting the run-result into a DB'
  ==============
  One after-application of this run is to feed a database and 'close' (or freeze)
    the record by setting 'b-field 'is_closed' to True.
  If an edit is later necessary, the whole series should be run again
    because of the temporal dependency cited above
    (run at least for checking, though consistency is also possible in one to its former record).

  Observation on one field that was not 'calculate-automatized'
  ==============
  The two fields (attributes) not automatized in the class are:
    => the 'transport' value
    => and the 'fruit' quota
  These are dependent on 'task hours' but by design task_hours was left out of this implementation,
    then the two fields (transport & fruit) became input instead of autocalculated.
  However, it's possible to design a pre-processing that might find these two fields via another app.
  """
  refmonth: datetime.date
  inivalue_d1: Dinero
  cre_in_tasks: Dinero  # credit in tasks (done)
  cre_in_pay: Dinero   # credit in a payment
  cre_in_trnsp_n_frut: Dinero   # credit in quotas (@see also docstr above)
  deb_giro: Dinero  # giro is a kind of 'loan' that, if not fulfilled, goes into D2 (the debt account 2)
  _inivalue_res: Dinero  # every month carries on the previous' finvalue one; 'res' stands for 'the reserve account'
  _inivalue_d2: Dinero  # d2 is 'the debt account 2'
  _finvalue_res: Dinero = field(default_factory=lambda: None)
  _finvalue_d2: Dinero = field(default_factory=lambda: None)
  is_closed_n_in_db: bool = False
  REFMONTH_INI_FOR_META: datetime.date = rmfs.make_refmonth_or_raise(REFMONTH_INI_FOR_META)
  VALOR_META_MENSAL_BRL: Dinero = field(default_factory=lambda: VALOR_META_MENSAL_BRL)
  _corrmone_n_intrst_if_any: Dinero = None  # represents the amount increase due to fix interest and variable index
  _ipca_dec: Dinero = None  #  is the IPCA month's inflation fraction (another part of this app fetches it)
  updt_saldos_has_run: bool = False  # this Class models a run-once object

  def __post_init__(self):
    """
    Main rule here is that D2 (the debt 2 account) can only have a balance
      if 'res' (the reserve account) is empty (=0)
    But also:
      'res' cannot be negative
      'D1' cannot be positive
      'D2' cannot be positive

    But, important, some accounts may be both positive and negative,
      for example, transport_n_fruit are positive, but can receive an 'estorno' which is negative
    """
    if self.inivalue_res < accdt.dinero_zero:
      errmsg = f"Error: reserve {self.inivalue_res} cannot be negative."
      raise ValueError(errmsg)
    if self.inivalue_d1 > accdt.dinero_zero:
      errmsg = f"Error: balance D1 {self.inivalue_d1} cannot be positive."
      raise ValueError(errmsg)
    if self.inivalue_d2 > accdt.dinero_zero:
      errmsg = f"Error: balance D2 {self.inivalue_d2} cannot be positive."
      raise ValueError(errmsg)

  @property
  def str_refmonth(self) -> str:
    str_refmonth = rmfs.trnsf_refmonth_to_yyyydashmm(self.refmonth) or "n/a"
    return str_refmonth

  @property
  def seq_refmonth(self):
    n_months_inbetween = rmfs.calc_int_n_months_inbetween(self.REFMONTH_INI_FOR_META, self.refmonth)
    # month 1 is conventioned as the 'legacy' 2025-10 which has not a data-record,
    # leaving it to the subsequent month
    # so, add one to 1
    return n_months_inbetween + 1

  @property
  def finvalue_d1(self):
    """
    This is a characteristic of D1 (the debt account 1)
    It (its abs()) always diminishes by VALOR_META_MENSAL_BRL
    Differences go the D2
    """
    return self.inivalue_d1 + VALOR_META_MENSAL_BRL  # notice iniD1 is negative and metamensal positive

  @property
  def inivalue_res(self) -> Dinero:
    return self._inivalue_res

  @property
  def inivalue_d2(self):
    return self._inivalue_d2

  @property
  def finvalue_res(self):
    if self._finvalue_res is None:
      # provisionally, method 'updt' will 'correct' this inital value
      self._finvalue_res = self.inivalue_res
      self.process()
    return self._finvalue_res

  @property
  def finvalue_d2(self):
    if self._finvalue_d2 is None:
      # provisionally, method 'updt' will 'correct' this inital value
      self._finvalue_d2 = self.inivalue_d2 + self.corrmone_n_intrst_if_any
      self.process()
    return self._finvalue_d2

  @property
  def total_cred(self):
    """
    total_cred is always positive
    """
    _total_cred = self.cre_in_tasks + self.cre_in_pay + self.cre_in_trnsp_n_frut
    if _total_cred < accdt.dinero_zero:
      errmsg = f"Error: total_cred cannot be negative."
      raise ValueError(errmsg)
    return _total_cred

  @property
  def total_deb(self):
    """
    total_deb is always negative
    """
    _total_deb = self.deb_giro
    if _total_deb > 0:
      errmsg = f"Error: total_deb cannot be positive."
      raise ValueError(errmsg)
    return _total_deb

  @property
  def balanco_deb_cre(self):
    """
    total_cred is always positive
    deb_giro is always negative
    (so the arithmetic is '+')
    """
    balanco = self.total_cred + self.deb_giro  # if there is 'giro' is normally (if not 'estorno') negative
    return balanco

  @property
  def exc_or_deficit_to_meta(self):
    """
    VALOR_META_MENSAL_BRL is positive
    (so the arithmetic is '-')
    """
    exc_or_def = self.balanco_deb_cre - VALOR_META_MENSAL_BRL
    return exc_or_def

  def get_corrmone_n_intrst_parcel_if_any(self) -> Dinero:
    if self._inivalue_d2 == accdt.dinero_zero:
      return accdt.dinero_zero
    corrmone_n_intrst, self._ipca_dec = get_as_dinero_dec_corrmone_n_intrst(self.inivalue_d2, self.refmonth)
    # corrmone_n_intrst here is a negative number: check it and turn over sign if needed
    if corrmone_n_intrst > accdt.dinero_zero:
      corrmone_n_intrst = corrmone_n_intrst * -1
    corrmone_n_intrst = accdt.get_brl_dinero(corrmone_n_intrst)
    return corrmone_n_intrst

  @property
  def corrmone_n_intrst_if_any(self) -> Dinero:
    if self._corrmone_n_intrst_if_any is None:
      self._corrmone_n_intrst_if_any = self.get_corrmone_n_intrst_parcel_if_any()
    if self._corrmone_n_intrst_if_any is None:
      """
      IPCA is available from another part of this app,
        but if a particular month's index is not be available, ValueError will be raised.
      """
      errmsg = f"Error: corrmone_n_intrst_if_any is None"
      raise ValueError(errmsg)
    return self._corrmone_n_intrst_if_any

  def print_msg_w_finvalues_res_n_d2(self, fname, detail="") -> None:
    """
    This is an adhoc-debugging print method
    (used when developing and to be removed later on)

      fname = __name__
      detail = "d2 < excedente"
      self.print_msg_w_finvalues_res_n_d2(fname, detail)
    """
    msg = f"f@{fname}"
    msg += f" | [{detail}]"
    msg += f" | fin_d2 = {self.fmt_finvalue_d2}"
    msg += f" | fin_res = {self.fmt_finvalue_res}"
    msg += f" | refmonth = {self.str_refmonth}"
    print(msg)

  def treat_surplus_for_reserve_n_d2(self, excedente):
    """
      # case 1: surplus diminishes 'D2' and leaves nothing remaining to 'reserve'
      # case 2: surplus diminishes 'D2' and leaves something remaining to 'reserve'
    """
    if excedente < accdt.dinero_zero:
      errmsg = f"Error: excedente(={excedente}) is negative in treat_surplus_for_reserve_n_d2()"
      raise ValueError(errmsg)
    inid2_plus_cm_n_intrst: Dinero = self.inivalue_d2 + self.corrmone_n_intrst_if_any
    if inid2_plus_cm_n_intrst > accdt.dinero_zero:
      errmsg = f"Error: inid2_plus_cm_n_intrst(={inid2_plus_cm_n_intrst}) is positive, should be negative"
      raise ValueError(errmsg)
    if abs(inid2_plus_cm_n_intrst.raw_amount) >= excedente.raw_amount:
      # case 1: surplus diminishes 'D2' and leaves nothing remaining to 'reserve'
      self._finvalue_d2 = inid2_plus_cm_n_intrst
      self._finvalue_d2 = self._finvalue_d2 + excedente  # this 'diminishes' abs(D2)
      self._finvalue_res = self._inivalue_res  # just copying res ini to fin, it doesn't receive any remaining
      return True
    else:  # inid2_plus_cm_n_intrst < excedente:
      # case 2: surplus diminishes 'D2' and leaves something remaining to 'reserve'
      ainda_excedendo = inid2_plus_cm_n_intrst + excedente  # attention with signs (+/-): excedente is positive
      self._finvalue_d2 = accdt.dinero_zero
      # remains for the 'reserve'
      self._finvalue_res = self.inivalue_res + ainda_excedendo
      return True

  def treat_faltante_when_reserve_is_empty(self, faltante):
    """
    if there is missing value and reserve is empty, then this value is all placed on D2

    # at this point self.inivalue_res is 0 i.e., reserve is empty
    """
    self._finvalue_d2 = self.inivalue_d2 + faltante
    # lastly, add corrmone if any
    self._finvalue_d2 = self._finvalue_d2 + self.corrmone_n_intrst_if_any
    return True

  def treat_faltante_when_reserve_is_positive(self, faltante):
    """
      if there is missing value (faltante) and 'reserve' is not empty,
         then the missing should first be debted against 'reserve'
    case 1: reserve is greater than or equal to faltante, debt it and return
    case 2: reserve is less than faltante, empty 'reserve' and debt the remaings from 'D2'
    """
    if self.inivalue_res.raw_amount >= abs(faltante.raw_amount):
      # case 1: reserve is greater than or equal to faltante, debt it all from 'reserve' and return
      self._finvalue_res = self.inivalue_res + faltante  # remembering faltante is negative
      # when 'reserve' has some value, 'D2' must be empty, but update D2 anyway (it's expected to be zero)
      self._finvalue_d2 = self.inivalue_d2 + self.corrmone_n_intrst_if_any
      return True
    else:
      # case 2: reserve is less than faltante, empty 'reserve' and debt the remaings from 'D2'
      self._finvalue_res = accdt.dinero_zero  # finvalue's are mutated, inivalue's should not
      faltante = faltante + self.inivalue_res  # credit 'res' to 'faltante', remembering faltante is negative
      self._finvalue_d2 = self.inivalue_d2 + faltante
      # lastly, add corrmone if any
      self._finvalue_d2 = self._finvalue_d2 + self.corrmone_n_intrst_if_any
      return True

  def treat_faltante_p_saldo_reserva_n_d2(self, faltante):
    if faltante > accdt.dinero_zero:
      errmsg = f"Error: faltante (={faltante}) is positive, it should be negative"
      raise ValueError(errmsg)
    if self.inivalue_res < accdt.dinero_zero:  # reserve cannot be negative
      errmsg = f"Error: inivalue_res (={self.inivalue_res}) is negative, it should be positive"
      raise ValueError(errmsg)
    if self.inivalue_res > accdt.dinero_zero:
      # 'reserve' is not empty, debt 'faltante' first to 'reserve'
      return self.treat_faltante_when_reserve_is_positive(faltante)
    # 'reserve' is empty, debt faltante to 'D2'
    return self.treat_faltante_when_reserve_is_empty(faltante)

  @property
  def fmt_finvalue_d1(self):
    flo = self.finvalue_d1.raw_amount
    return f"{flo:0.2f}"

  @property
  def fmt_finvalue_d2(self):
    flo = self.finvalue_d2.raw_amount
    return f"{flo:0.2f}"

  @property
  def fmt_finvalue_res(self):
    flo = self.finvalue_res.raw_amount
    return f"{flo:0.2f}"

  def treat_monthly_zero_balance(self):
    """
    Monthly balance is zero, but fin res and fin D2 must be filled in
      1 ini res value is (simply) copied / transferred to fin res
      2 fin D2 is ini D2 plus corrmone "if any"

    fname = inspect.currentframe().f_code.co_name
    detail = "m-balance is zero"
    self.print_msg_w_finvalues_res_n_d2(fname, detail)
    """
    # 1 ini res value is (simply) copied / transferred to fin res
    self._finvalue_res = self.inivalue_res
    # 2 fin D2 is ini D2 plus corrmone "if any"
    self._finvalue_d2 = self.inivalue_d2 + self.corrmone_n_intrst_if_any
    return True

  def updt_saldo_reserva_n_d2(self):
    """
    Updates accounts 'reserve' and 'D2'.
      This method can only run once.
    """
    self.updt_saldos_has_run = True
    exced_or_faltante = self.exc_or_deficit_to_meta
    if exced_or_faltante == accdt.dinero_zero:
      return self.treat_monthly_zero_balance()
    if exced_or_faltante > accdt.dinero_zero:
      # surplus case: at this point, exced_or_faltante > 0
      excedente = exced_or_faltante
      return self.treat_surplus_for_reserve_n_d2(excedente)
    # faltante case: at this point, exced_or_faltante < 0
    faltante = exced_or_faltante
    return self.treat_faltante_p_saldo_reserva_n_d2(faltante)

  def process(self):
    if not self.updt_saldos_has_run:
      self.updt_saldo_reserva_n_d2()

  def __str__(self):
    ini_d1 = self.inivalue_d1.raw_amount
    s_ini_d1 = f"{ini_d1:.02f}"
    ini_d2 = self.inivalue_d2.raw_amount
    s_ini_d2 = f"{ini_d2:.02f}"
    ini_res = self.inivalue_res.raw_amount
    s_ini_res = f"{ini_res:.02f}"
    cre_in_tasks = self.cre_in_tasks.raw_amount
    s_cre_in_tasks = f"{cre_in_tasks:.02f}"
    cre_in_pay = self.cre_in_pay.raw_amount
    s_cre_in_pay = f"{cre_in_pay:.02f}"
    cre_in_trnsp_n_frut = self.cre_in_trnsp_n_frut.raw_amount
    s_cre_in_trnsp_n_frut = f"{cre_in_trnsp_n_frut:.02f}"
    total_cred = self.total_cred.raw_amount
    s_total_cred = f"{total_cred:.02f}"
    deb_giro = self.deb_giro.raw_amount
    s_deb_giro = f"{deb_giro:.02f}"
    s_balanco_debcre = 'n/a' if self.balanco_deb_cre is None else f"{self.balanco_deb_cre.raw_amount:.02f}"
    s_corrmone = 'n/a' if self.corrmone_n_intrst_if_any is None else f"{self.corrmone_n_intrst_if_any.raw_amount:0.2f}"
    s_ipca_dec = 'n/a' if self._ipca_dec is None else f"{self._ipca_dec:.04f}"
    s_exc_or_def = 'n/a' if self.exc_or_deficit_to_meta is None else f"{self.exc_or_deficit_to_meta.raw_amount:.02f}"
    metmes = self.VALOR_META_MENSAL_BRL
    ostr = f"""{self.__class__.__name__} | {self.seq_refmonth} | {str(self.str_refmonth)}
    Ini:
      saldo_d1= {s_ini_d1} |  saldo_d2= {s_ini_d2} | saldo_res = {s_ini_res} 
    Month cre:
      cre_in_tasks = {s_cre_in_tasks} |  cre_in_pay= {s_cre_in_pay} | trnsp_n_frut = {s_cre_in_trnsp_n_frut} 
    Month cre/deb:
      metamês = {metmes} | totcred = {s_total_cred} | giro= {s_deb_giro}  | bal_deb_cre={s_balanco_debcre}
      corrmone_n_intrst_if_any = {s_corrmone} | ipca = {s_ipca_dec} | exc_or_def = {s_exc_or_def}
    Fim:
      saldo_d1= {self.fmt_finvalue_d1} |  saldo_d2= {self.fmt_finvalue_d2} | saldo_res = {self.fmt_finvalue_res} 
    """
    return ostr


@dataclass
class KeptD2AndRes:
  inivalue_res: Dinero
  inivalue_d2: Dinero

  def __str__(self):
    return f"res={self.inivalue_res} | d2={self.inivalue_d2}"


def process():
  """
      ic_inivalue_d1: int
      ic_inivalue_res: int
      ic_finvalue_d2: int
      ic_cre_in_tasks: int
      ic_cre_in_pay: int
      ic_cre_in_trnsp_n_frut: int
      ic_deb_giro: int
  """
  seq = 0
  kept_d2_res = KeptD2AndRes(
    inivalue_res=accdt.dinero_zero,
    inivalue_d2=accdt.dinero_zero,
  )
  for item in accdt.items:
    seq += 1
    refmonth = item['refmonth']
    refmonth = rmfs.make_refmonth_or_raise(refmonth)
    deb_cred_acc_o = DebCredAccompanier(
      refmonth=refmonth,
      inivalue_d1=item['inivalue_d1'],
      _inivalue_res=kept_d2_res.inivalue_res,
      _inivalue_d2=kept_d2_res.inivalue_d2,
      cre_in_tasks=item['cre_in_tasks'],
      cre_in_pay=item['cre_in_pay'],
      cre_in_trnsp_n_frut=item['cre_in_trnsp_n_frut'],
      deb_giro=item['deb_giro'],
    )
    deb_cred_acc_o.updt_saldo_reserva_n_d2()
    kept_d2_res = KeptD2AndRes(
      inivalue_res=deb_cred_acc_o.finvalue_res,
      inivalue_d2=deb_cred_acc_o.finvalue_d2,
    )
    print(kept_d2_res)
    print(deb_cred_acc_o)


if __name__ == '__main__':
  process()
