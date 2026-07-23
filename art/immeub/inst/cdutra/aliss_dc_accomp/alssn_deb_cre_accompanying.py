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
from decimal import Decimal
from dinero import Dinero
from dinero.currencies import BRL
from dataclasses import dataclass, field, asdict
import art.immeub.inst.cdutra.aliss_dc_accomp.accdata_deb_cre_alssn as accdt  # accdt.items
import lib.datesetc.refmonth_fs as rmfs
import lib.finfs.indices.indices_fetch_n_fs as ipfs  # ipfs.ipca_for_refmonth
import lib.finfs.dinerofs.credit_debit_fs as cdfs  # cdfs.debit_or_credit_value_to_accounts
import immeub.inst.cdutra.aliss_dc_accomp.mdb.serialize_dinero_n_decimal as srlz_din_dec
VALOR_META_MENSAL_BRL = accdt.get_brl_dinero(500)
REFMONTH_INI_FOR_META = '2025-10'
DINERO_ZERO = Dinero(str("0"), BRL)


def get_abs_dec_corrmone_n_intrst(inivalue: Dinero, refmonth: datetime.date, fix: float=0.02):
  """
  The abs(inivalue) is taken so that the fraction returns as a positive number
  """
  inivalue = abs(inivalue.raw_amount)
  m_minus_2_rm = rmfs.make_refmonth_it_minus_n(refmonth, 2)
  ipca_dec = ipfs.ipca_for_refmonth(m_minus_2_rm)
  fix = Decimal(fix)
  if not isinstance(ipca_dec, decimal.Decimal):
    ipca_dec = Decimal(ipca_dec)
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
  _ipca_dec: Decimal = None  # is the IPCA month's inflation fraction (another part of this app fetches it)
  updt_saldos_has_run: bool = False  # this Class models a run-once object

  def __post_init__(self):
    """
    Main rule here is that D2 (the debt 2 account) can only have a balance
      if 'res' (the reserve account) is empty (=0)
    But also:
      'res' cannot be negative
      'D1' cannot be positive
      'D2' cannot be positive

    But, important, some accounts may be both positive or negative,
      for example, transport_n_fruit are positive, but can receive an 'estorno' which is negative.
    """
    if self.inivalue_res < DINERO_ZERO:
      errmsg = f"Error: reserve {self.inivalue_res} cannot be negative."
      raise ValueError(errmsg)
    if self.inivalue_d1 > DINERO_ZERO:
      errmsg = f"Error: balance D1 {self.inivalue_d1} cannot be positive."
      raise ValueError(errmsg)
    if self.inivalue_d2 > DINERO_ZERO:
      errmsg = f"Error: balance D2 {self.inivalue_d2} cannot be positive."
      raise ValueError(errmsg)
    # initialize both (accounts) 'reserve' and 'D2'
    # account 'reserve' is only a 'copying' from ini to fin
    self._finvalue_res = self.inivalue_res
    # account 'D2' is 'ini' plus a 'monetary correction'
    self._finvalue_d2 = self.inivalue_d2 + self.corrmone_n_intrst_if_any

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
    """
    It's available, i.e., not None, after __post__init()
    """
    return self._finvalue_res

  @property
  def finvalue_d2(self):
    """
    It's available, i.e., not None, after __post__init()
    """
    return self._finvalue_d2

  @property
  def total_cred(self):
    """
    total_cred is always positive
    """
    _total_cred = self.cre_in_tasks + self.cre_in_pay + self.cre_in_trnsp_n_frut
    if _total_cred < DINERO_ZERO:
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
  def surplus_or_deficit_to_monthlymeta(self):
    """
    This is:
      exc_or_def = self.balanco_deb_cre - VALOR_META_MENSAL_BRL
    where:
      VALOR_META_MENSAL_BRL is 'conventioned' positive
      (so the arithmetic is '-')

    Notice:
      exc_or_def = self.balanco_deb_cre - VALOR_META_MENSAL_BRL
    'balanco' may be positive or negative
     VALOR_META_MENSAL_BRL is positive, and it acts
       as debting 'balanco':

       if exc_or_def > 0, it's a 'surplus' (excedente)
       else (if exc_or_def < 0), it's a 'deficit' (faltante)
    """
    exc_or_def = self.balanco_deb_cre - VALOR_META_MENSAL_BRL
    return exc_or_def

  def get_corrmone_n_intrst_parcel_if_any(self) -> Dinero:
    if self._inivalue_d2 == DINERO_ZERO:
      return DINERO_ZERO
    corrmone_n_intrst, self._ipca_dec = get_as_dinero_dec_corrmone_n_intrst(self.inivalue_d2, self.refmonth)
    # corrmone_n_intrst here is a negative number: check it and turn over sign if needed
    if corrmone_n_intrst > DINERO_ZERO:
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

  def make_reserve_compensate_d2_if_any(self):
    """
    Alright, there is an extra step to:
      updt_saldo_reserva_n_d2()
        called in the 'update' method
      (this completes the 'refmonth' update)

    Let us remind, both 'reserve' and 'D2' cannot have values at the same time.
    'reserve' is a credit account, 'D2' is a debt account.
    Supposing there were a debt, any 'reserve' would compensate it
      and the end result would be either one or the other exists.

    In the logics in here, the presence of both having values
      would probably only occur in an initial state due to the user setting the two
      (which would also be considered somewhat wrong).

    With some tests, this function has shown not necessary if the 'initial state' is correct,
      but in a future version further tests may decide whether it's really needed.

    Anyway, this method calls a 'compensating' function.

    The function called in the 'update' method uses the 'remaining'
      after a cred-against-deb (or viceversa) to carry on the
      cred-against-cred (or viceversa) but does not compensate
      cred_acc-against-deb_acc (or viceversa). This is done here.

    So, in a nutshell, in this app, 'reserve' must 'compensate' D2
      if both have values at the same time.

    Example:
      if 'reserve' has 100 units and 'D2' has -50 units;
      'reserve' must 'pay' (compensate), so to say,'D2'.
      So:
        if input = (reserve=100, D2=-50)
        then output = (reserve=50, D2=0)
        i.e., reserve paid 50 to D2,
    Another example:
        input = (reserve=50, D2=-100)
        output then should be (reserve=0, D2=50)
    A 'full compensation' example:
        input = (reserve=50, D2=-50)
        output then should be (reserve=0, D2=0)
    """
    self._finvalue_res, self._finvalue_d2 = cdfs.compensate_cred_deb_accounts_one_against_the_other(
      self.finvalue_res, self.finvalue_d2
    )

  def updt_saldo_reserva_n_d2(self):
    """
    Updates, for the month, the two accounts 'reserve' (a credit account) and 'D2' (a debit account).
      This method can only run once.
      This method calls cdfs.debit_or_credit_value_to_accounts() lib function.
    """
    self.updt_saldos_has_run = True
    exced_or_faltante = self.surplus_or_deficit_to_monthlymeta
    # the function called below 'distributes' exced_or_faltante into 'reserve' or D2 as it's a credit or a debt
    self._finvalue_res, self._finvalue_d2 = cdfs.debit_or_credit_value_to_accounts(
      exced_or_faltante,
      self.finvalue_res,
      self.finvalue_d2
    )
    # alright, value has been distributed, but there is one extra step
    self.make_reserve_compensate_d2_if_any()
    return

  def process(self):
    if not self.updt_saldos_has_run:
      self.updt_saldo_reserva_n_d2()

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

  def asdict(self):
    pdict = asdict(self, dict_factory=srlz_din_dec.din_dec_dict_fact)
    keys_to_remove = {
      "REFMONTH_INI_FOR_META", "updt_saldos_has_run", "VALOR_META_MENSAL_BRL"
    }
    selected_dict = {
      k: v for k, v in pdict.items()
      if k not in keys_to_remove
    }
    return selected_dict

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
    s_exc_or_def = 'n/a' if self.surplus_or_deficit_to_monthlymeta is None \
        else f"{self.surplus_or_deficit_to_monthlymeta.raw_amount:.02f}"
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


def get_months_closings_w_dictdata():
  seq = 0
  kept_d2_res = KeptD2AndRes(
    inivalue_res=DINERO_ZERO,
    inivalue_d2=DINERO_ZERO,
  )
  debcred_acc_objlist = []
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
    # print(deb_cred_acc_o)
    debcred_acc_objlist.append(deb_cred_acc_o)
  return debcred_acc_objlist


def process():
  """
  """
  get_months_closings_w_dictdata()


if __name__ == '__main__':
  process()
