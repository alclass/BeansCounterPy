#!/usr/bin/env python3
"""
art/immeub/inst/cdutra/aliss_dc_accomp/alssn_deb_cre_accompanying.py
"""
import datetime
from dataclasses import dataclass
import art.immeub.inst.cdutra.aliss_dc_accomp.accdata_deb_cre_alssn as accdt  # accdt.items
import lib.datesetc.refmonth_fs as rmfs
import lib.finfs.indices.indices_fetch_n_fs as ipfs  # ipfs.ipca_for_refmonth

VALOR_META_MENSAL_BRL = 500
REFMONTH_INI_FOR_META = '2025-10'


def get_abs_dec_corrmone_n_intrst(inivalue, refmonth, fix=0.02):
  """
  The abs(inivalue) is taken so that the fraction returns as a positive number
  """
  inivalue = abs(inivalue)
  m_minus_2_rm = rmfs.make_refmonth_it_minus_n(refmonth, 2)
  ipca_dec = ipfs.ipca_for_refmonth(m_minus_2_rm)
  corrmone_n_intrst = inivalue * (fix + ipca_dec)
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
  ic_inivalue_d1: int
  ic_cre_in_tasks: int
  ic_cre_in_pay: int
  ic_cre_in_trnsp_n_frut: int
  ic_deb_giro: int
  ic_inivalue_res: int  # | None = None
  ic_inivalue_d2: int  # | None = None
  _finvalue_res: float | None = None
  _finvalue_d2: float | None  = None
  is_closed_n_in_db: bool = False
  REFMONTH_INI_FOR_META: datetime.date = rmfs.make_refmonth_or_raise('2025-10')
  VALOR_META_MENSAL_BRL: int = VALOR_META_MENSAL_BRL
  _corrmone_n_intrst_if_any: float =  None
  _ipca_dec: float =  None

  @property
  def str_refmonth(self):
    return str(self.refmonth)

  @property
  def seq_refmonth(self):
    n_months_inbetween = rmfs.calc_int_n_months_inbetween(self.REFMONTH_INI_FOR_META, self.refmonth)
    # month 1 is conventioned the 'legacy' 2025-10 which has not a data-record
    # so, add one to 1
    return n_months_inbetween + 1

  @property
  def inivalue_d1(self):
    return self.ic_inivalue_d1 / 100

  @property
  def finvalue_d1(self):
    return self.inivalue_d1 - VALOR_META_MENSAL_BRL

  @property
  def inivalue_res(self):
    return self.ic_inivalue_res / 100

  @property
  def inivalue_d2(self):
    return self.ic_inivalue_d2 / 100

  @property
  def cre_in_tasks(self):
    return self.ic_cre_in_tasks / 100

  @property
  def cre_in_pay(self):
    return self.ic_cre_in_pay / 100

  @property
  def cre_in_trnsp_n_frut(self):
    return self.ic_cre_in_trnsp_n_frut / 100

  @property
  def total_cred(self):
    _total_cred = self.cre_in_tasks + self.cre_in_pay + self.cre_in_trnsp_n_frut
    return _total_cred

  @property
  def deb_giro(self):
    return self.ic_deb_giro / 100

  @property
  def balanco_deb_cre(self):
    balanco = self.total_cred + self.deb_giro  # if there is 'giro' is normally (if not 'estorno') negative
    return balanco

  @property
  def exc_or_deficit_to_meta(self):
    exc_or_def = self.balanco_deb_cre - VALOR_META_MENSAL_BRL
    return exc_or_def

  def get_corrmone_n_intrst_parcel_if_any(self):
    if self.ic_inivalue_d2 == 0:
      return 0.0
    corrmone_n_intrst, self._ipca_dec = get_abs_dec_corrmone_n_intrst(self.inivalue_d2, self.refmonth)
    # corrmone_n_intrst is negative number and it got a positive one
    corrmone_n_intrst = -corrmone_n_intrst
    return corrmone_n_intrst

  @property
  def corrmone_n_intrst_if_any(self):
    if self._corrmone_n_intrst_if_any is None:
      self._corrmone_n_intrst_if_any = self.get_corrmone_n_intrst_parcel_if_any()
    return self._corrmone_n_intrst_if_any

  def treat_excedente_p_saldo_reserva_n_d2(self, excedente):
    if excedente < 0:
      errmsg = f"Error: excedente(={excedente}) is negative in treat_excedente_p_saldo_reserva_n_d2()"
      raise ValueError(errmsg)
    inid2_plus_cm_n_intrst = self.inivalue_d2 + self.corrmone_n_intrst_if_any
    if inid2_plus_cm_n_intrst > 0:
      errmsg = f"Error: inid2_plus_cm_n_intrst(={inid2_plus_cm_n_intrst}) is positive, it cannot be"
      raise ValueError(errmsg)
    if inid2_plus_cm_n_intrst < 0:
      # baixar saldo d2 até a quantidade limite
      if abs(inid2_plus_cm_n_intrst) >= excedente:
        self._finvalue_res = self.inivalue_res
        self._finvalue_d2 = inid2_plus_cm_n_intrst + excedente
        return True
      else:  #  abs(inid2_plus_cm_n_intrst) < excedente:
        ainda_excedendo = excedente + inid2_plus_cm_n_intrst
        self._finvalue_d2 = 0.0
        # remains for the 'reserve'
        self._finvalue_res = self.inivalue_res + ainda_excedendo
        return True
    # at this inid2_plus_cm_n_intrst is zeroed
    # all excedent goes into the 'reserve'
    self._finvalue_d2 = self.inivalue_d2
    self._finvalue_res = self.inivalue_res + excedente
    return True

  def treat_faltante_p_saldo_reserva_n_d2(self, faltante):
    if faltante > 0:
      errmsg = f"Error: faltante(={faltante}) is positive in treat_faltante_p_saldo_reserva_n_d2()"
      raise ValueError(errmsg)
    # first, remove from 'reserve' if any
    ic_inivalue_res = int(round(self.inivalue_res*100, 4))
    if ic_inivalue_res < 0:  # reserve cannot be negative
      errmsg = f"Error: ic_inivalue_res(={ic_inivalue_res}) is negative, it cannot be"
      raise ValueError(errmsg)
    if self.inivalue_res > 0:
      if self.inivalue_res > abs(faltante):
        # reserve is greater than faltante, just debt it and return
        self._finvalue_res = self.inivalue_res + faltante  # faltante is generally negative
        self._finvalue_d2 = self.inivalue_d2 + self.corrmone_n_intrst_if_any
        return True
      else:  # reserve is not enough, debt its part and the remaining to D2
        consumed_positive = self.inivalue_res
        # now zero finvalue_res, reserve was 'consumed'
        self._finvalue_res = 0.0
        # remove consume_positive from 'faltante'
        ainda_faltante = faltante + consumed_positive
        self._finvalue_d2 = self.inivalue_d2 + ainda_faltante
        self._finvalue_d2 = self.inivalue_d2 + ainda_faltante
        self._finvalue_d2 = self._finvalue_d2 + self.corrmone_n_intrst_if_any
        return True
    # at this point self.inivalue_res is 0 i.e., reserve is empty
    self._finvalue_d2 = self.inivalue_d2 + faltante
    self._finvalue_d2 = self._finvalue_d2 + self.corrmone_n_intrst_if_any
    return True

  def upt_saldo_reserva_n_d2(self):
    self._finvalue_res = 0.0
    self._finvalue_d2 = 0.0
    ic_exc_or_def = int(round(self.exc_or_deficit_to_meta*100, 4))
    if ic_exc_or_def == 0:
      self._finvalue_res = self.inivalue_res
      self._finvalue_d2 = self.inivalue_d2
      return True
    if ic_exc_or_def > 0:
      excedente = self.exc_or_deficit_to_meta
      return self.treat_excedente_p_saldo_reserva_n_d2(excedente)
    # at this point, ic_exc_or_def < 0
    faltante = self.exc_or_deficit_to_meta
    return self.treat_faltante_p_saldo_reserva_n_d2(faltante)

  @property
  def finvalue_res(self):
    if self._finvalue_res is None:
      self.upt_saldo_reserva_n_d2()
    return self._finvalue_res

  @property
  def finvalue_d2(self):
    if self._finvalue_d2 is None:
      self.upt_saldo_reserva_n_d2()
    return self._finvalue_d2


  def process(self):
    pass

  def __str__(self):
    metmes = self.VALOR_META_MENSAL_BRL
    ostr = f"""{self.__class__.__name__} | {self.seq_refmonth} | {str(self.refmonth)}
    Ini:
      saldo_d1= {self.inivalue_d1:0.2f} |  saldo_d2= {self.inivalue_d2:0.2f} | saldo_res = {self.inivalue_res:0.2f} 
    Month cre:
      cre_in_tasks = {self.cre_in_tasks:0.2f} |  cre_in_pay= {self.cre_in_pay:0.2f} | trnsp_n_frut = {self.cre_in_trnsp_n_frut:0.2f} 
    Month cre/deb:
      metamensal= {metmes} tcred = {self.total_cred:0.2f} |  deb_giro= {self.deb_giro:0.2f}  | balanco_deb_cre={self.balanco_deb_cre:0.2f}
      corrmone_n_intrst_if_any = {self.corrmone_n_intrst_if_any:0.2f} | ipca = {self._ipca_dec} | exc_or_def = {self.exc_or_deficit_to_meta:0.2f}
    Fim:
      saldo_d1= {self.finvalue_d1:0.2f} |  saldo_d2= {self.finvalue_d2:0.2f} | saldo_res = {self.finvalue_res:0.2f} 
    """
    return ostr


class StruIcIniResND2:
  ic_inivalue_res = 0
  ic_inivalue_d2 = 0


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
  StruIcIniResND2.ic_inivalue_res = 0
  StruIcIniResND2.ic_inivalue_d2 = 0
  for item in accdt.items:
    seq +=1
    refmonth = item['refmonth']
    refmonth = rmfs.make_refmonth_or_raise(refmonth)
    deb_cred_acc_o = DebCredAccompanier(
      refmonth = refmonth,
      ic_inivalue_d1 = item['ic_inivalue_d1'],
      ic_inivalue_res = StruIcIniResND2.ic_inivalue_res,
      ic_inivalue_d2 = StruIcIniResND2.ic_inivalue_d2,
      ic_cre_in_tasks = item['ic_cre_in_tasks'],
      ic_cre_in_pay = item['ic_cre_in_pay'],
      ic_cre_in_trnsp_n_frut = item['ic_cre_in_trnsp_n_frut'],
      ic_deb_giro = item['ic_deb_giro'],
    )
    deb_cred_acc_o.upt_saldo_reserva_n_d2()
    StruIcIniResND2.ic_inivalue_res = deb_cred_acc_o.finvalue_res * 100
    StruIcIniResND2.ic_inivalue_d2 = deb_cred_acc_o.finvalue_d2 * 100
    print(deb_cred_acc_o)



if __name__ == '__main__':
  process()
