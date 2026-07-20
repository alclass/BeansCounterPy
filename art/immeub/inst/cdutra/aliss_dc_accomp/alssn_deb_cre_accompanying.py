#!/usr/bin/env python3
"""
art/immeub/inst/cdutra/aliss_dc_accomp/alssn_deb_cre_accompanying.py

Strategy to treat 'fractions' (with repeating decimal)
=================

Choices might be: Fraction, decimal.Decimal,
  dinero.Dinero and round()

  Choosing round()
    every_float = round(every_float, 4)  # internal and DB
    then:  {every_float:0.2f}  # display

from dataclasses import dataclass, field
from dinero import Dinero

@dataclass
class Transaction:
    amount: Dinero = field(default_factory=lambda: Dinero("10.50", "USD"))


"""
import datetime
import decimal
import inspect

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
  This class is conceptualized to make its months run sequential,
    i.e., one month feeds info into the subsequent next month.

  Observation on 'putting the run-result into a DB'
  ==============
  But one application of this run is to feed a database and 'close' (or freeze)
    the record setting db-field is_closed to True.
  If an edit is necessary, the whole series should be run again
    because of temporal dependency cited above.

  Observation on one field that was not 'calculate-automatized'
  ==============
  The fields (attributes) was not automatized in the class, they are:
    => the transport value
    => and the 'fruit' quota
  These are dependent on 'task hours' but by design task_hours was left out,
    then the two fields became input instead of autocalculated.
  """
  refmonth: datetime.date
  inivalue_d1: Dinero
  cre_in_tasks: Dinero
  cre_in_pay: Dinero
  cre_in_trnsp_n_frut: Dinero
  deb_giro: Dinero
  _inivalue_res: Dinero
  _inivalue_d2: Dinero
  _finvalue_res: Dinero = field(default_factory=lambda: None)
  _finvalue_d2: Dinero = field(default_factory=lambda: None)  # lambda: accdt.dinero_zero)
  is_closed_n_in_db: bool = False
  REFMONTH_INI_FOR_META: datetime.date = rmfs.make_refmonth_or_raise('2025-10')
  VALOR_META_MENSAL_BRL: Dinero = field(default_factory=lambda: VALOR_META_MENSAL_BRL)
  _corrmone_n_intrst_if_any: Dinero = None
  _ipca_dec: Dinero = None
  updt_saldos_has_run: bool = False

  def __post_init__(self):
    """
    Main rule here is that d2 can only have a balance if res is 0
    """
    if self.inivalue_res < accdt.dinero_zero:
      errmsg = f"Error: reserve {self.inivalue_res} cannot be negative."
      raise ValueError(errmsg)
    if self.inivalue_d2 > accdt.dinero_zero:
      errmsg = f"Error: balance D2 {self.inivalue_res} cannot be positive."
      raise ValueError(errmsg)
    if self.inivalue_res > accdt.dinero_zero < self.inivalue_d2:
      errmsg = f"Error: both reserve {self.inivalue_res} and D2 {self.inivalue_res} have values. Only one can have."
      raise ValueError(errmsg)

  @property
  def str_refmonth(self) -> str:
    str_refmonth = rmfs.trnsf_refmonth_to_yyyydashmm(self.refmonth) or "n/a"
    return str_refmonth

  @property
  def seq_refmonth(self):
    n_months_inbetween = rmfs.calc_int_n_months_inbetween(self.REFMONTH_INI_FOR_META, self.refmonth)
    # month 1 is conventioned the 'legacy' 2025-10 which has not a data-record
    # so, add one to 1
    return n_months_inbetween + 1

  @property
  def finvalue_d1(self):
    """
    This is a characteristic of D1
    It always diminishes by VALOR_META_MENSAL_BRL
    """
    return self.inivalue_d1 - VALOR_META_MENSAL_BRL

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
    _total_cred = self.cre_in_tasks + self.cre_in_pay + self.cre_in_trnsp_n_frut
    return _total_cred

  @property
  def balanco_deb_cre(self):
    balanco = self.total_cred + self.deb_giro  # if there is 'giro' is normally (if not 'estorno') negative
    return balanco

  @property
  def exc_or_deficit_to_meta(self):
    exc_or_def = self.balanco_deb_cre - VALOR_META_MENSAL_BRL
    return exc_or_def

  def get_corrmone_n_intrst_parcel_if_any(self) -> Dinero:
    if self._inivalue_d2 == accdt.dinero_zero:
      return accdt.dinero_zero
    corrmone_n_intrst, self._ipca_dec = get_as_dinero_dec_corrmone_n_intrst(self.inivalue_d2, self.refmonth)
    # corrmone_n_intrst is negative number and it got a positive one
    if corrmone_n_intrst > accdt.dinero_zero:
      corrmone_n_intrst = corrmone_n_intrst * -1
    corrmone_n_intrst = accdt.get_brl_dinero(corrmone_n_intrst)
    return corrmone_n_intrst

  @property
  def corrmone_n_intrst_if_any(self) -> Dinero:
    if self._corrmone_n_intrst_if_any is None:
      self._corrmone_n_intrst_if_any = self.get_corrmone_n_intrst_parcel_if_any()
    if self._corrmone_n_intrst_if_any is None:
      errmsg = f"Error: corrmone_n_intrst_if_any is None"
      raise ValueError(errmsg)
    return self._corrmone_n_intrst_if_any

  def print_msg_w_finvalues_res_n_d2(self, fname, detail="") -> None:
    """
    This is an adhoc-debugging print method
    """
    msg = f"f@{fname}"
    msg += f" | [{detail}]"
    msg += f" | fin_d2 = {self.fmt_finvalue_d2}"
    msg += f" | fin_res = {self.fmt_finvalue_res}"
    msg += f" | refmonth = {self.str_refmonth}"
    print(msg)

  def treat_excedente_p_saldo_reserva_n_d2(self, excedente):
    """

      fname = __name__
      detail = "d2 < excedente"
      self.print_msg_w_finvalues_res_n_d2(fname, detail)
    """
    if excedente < accdt.dinero_zero:
      errmsg = f"Error: excedente(={excedente}) is negative in treat_excedente_p_saldo_reserva_n_d2()"
      raise ValueError(errmsg)
    inid2_plus_cm_n_intrst: Dinero = self.inivalue_d2 + self.corrmone_n_intrst_if_any
    if inid2_plus_cm_n_intrst > accdt.dinero_zero:
      errmsg = f"Error: inid2_plus_cm_n_intrst(={inid2_plus_cm_n_intrst}) is positive, it cannot be"
      raise ValueError(errmsg)
    # baixar saldo d2 até a quantidade limite
    if abs(inid2_plus_cm_n_intrst.raw_amount) >= excedente.raw_amount:
      # excedent can diminish D2 and it remains nothing to reserve
      self._finvalue_d2 = inid2_plus_cm_n_intrst
      self._finvalue_d2 = self._finvalue_d2 + excedente
      self._finvalue_res = self._inivalue_res
      return True
    else:  # inid2_plus_cm_n_intrst < excedente:
      # take care with signs (+/-): excedente is positive
      ainda_excedendo = inid2_plus_cm_n_intrst + excedente
      self._finvalue_d2 = accdt.dinero_zero
      # remains for the 'reserve'
      self._finvalue_res = self.inivalue_res + ainda_excedendo
      return True
    # at this inid2_plus_cm_n_intrst is zeroed
    # all excedent goes into the 'reserve'
    self._finvalue_d2 = self.inivalue_d2
    self._finvalue_res = self.inivalue_res + excedente
    return True

  def treat_faltante_when_reserve_is_empty(self, faltante):
    """
    fname = __name__
    detail = "res is empty"
    self.print_msg_w_finvalues_res_n_d2(fname, detail)
    """
    # at this point self.inivalue_res is 0 i.e., reserve is empty
    self._finvalue_d2 = self.inivalue_d2 + faltante
    # lastly, add corrmone if any
    self._finvalue_d2 = self._finvalue_d2 + self.corrmone_n_intrst_if_any
    return True

  def treat_faltante_when_reserve_is_positive(self, faltante):
    """
      fname = inspect.currentframe().f_code.co_name
      strfaltante = f"{faltante.raw_amount:.02f}"
      detail = f"res >= faltante={strfaltante}"
      self.print_msg_w_finvalues_res_n_d2(fname, detail)
    """
    if self.inivalue_res.raw_amount >= abs(faltante.raw_amount):
      # reserve is greater than faltante, just debt it and return
      self._finvalue_res = self.inivalue_res + faltante  # faltante is generally negative
      self._finvalue_d2 = self.inivalue_d2 + self.corrmone_n_intrst_if_any
      return True
    else:  # reserve is not enough, debt its part and the remaining to D2
      tmp_reserve = self.inivalue_res
      # now zero finvalue_res, reserve was 'consumed'
      self._finvalue_res = accdt.dinero_zero
      # notice faltante is negative and tmp_reserve is positive
      faltante = faltante + tmp_reserve
      self._finvalue_d2 = self.inivalue_d2 + faltante
      # lastly, add corrmone if any
      self._finvalue_d2 = self._finvalue_d2 + self.corrmone_n_intrst_if_any
      return True

  def treat_faltante_p_saldo_reserva_n_d2(self, faltante):
    if faltante > accdt.dinero_zero:
      errmsg = f"Error: faltante(={faltante}) is positive in treat_faltante_p_saldo_reserva_n_d2()"
      raise ValueError(errmsg)
    if self.inivalue_res < accdt.dinero_zero:  # reserve cannot be negative
      errmsg = f"Error: inivalue_res(={self.inivalue_res}) is negative, it cannot be"
      raise ValueError(errmsg)
    # first, remove from 'reserve' if any
    if self.inivalue_res > accdt.dinero_zero:
      return self.treat_faltante_when_reserve_is_positive(faltante)
    return self.treat_faltante_when_reserve_is_empty(faltante)

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
    # almost nothing do to
      # 1 - copy res ini to fin
      # 2 - update D2 "if any" corrmone
    """
    # 1 - the line below guarantes ini-fin res values copied
    _ = self.finvalue_res
    # 2 - run the corrmone function "if any"
    self._finvalue_d2 = self.inivalue_d2 + self.corrmone_n_intrst_if_any
    fname = inspect.currentframe().f_code.co_name
    detail = "m-balance is zero"
    self.print_msg_w_finvalues_res_n_d2(fname, detail)
    return True

  def updt_saldo_reserva_n_d2(self):
    self.updt_saldos_has_run = True
    exced_or_faltante = self.exc_or_deficit_to_meta
    if exced_or_faltante == accdt.dinero_zero:
      return self.treat_monthly_zero_balance()
    # excedente case
    if exced_or_faltante > accdt.dinero_zero:
      excedente = exced_or_faltante
      return self.treat_excedente_p_saldo_reserva_n_d2(excedente)
    # at this point, exced_or_faltante < 0, i.e., the faltante case
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
    s_finvalue_d1 = 'n/a' if self.finvalue_d1 is None else f"{self.finvalue_d1.raw_amount:.02f}"
    s_finvalue_d2 = 'n/a' if self.finvalue_d2 is None else f"{self.finvalue_d2.raw_amount:.02f}"
    s_finvalue_res = 'n/a' if self.finvalue_res is None else  f"{self.finvalue_res.raw_amount:.02f}"
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
      saldo_d1= {s_finvalue_d1} |  saldo_d2= {s_finvalue_d2} | saldo_res = {s_finvalue_res} 
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
