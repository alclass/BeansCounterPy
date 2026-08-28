from typing import Optional
import pydantic
import datetime
from datetime import date, time
from decimal import Decimal
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.PydtcPerson
import lib.datesetc.datefs as dtfs
import lib.fncfs.fncmathfs.fncmath_calc_finalmontants_etal as fm_mnts  # fm_mnts.sigfig()


def split_nonrepeats_n_repeats_fr_payments(p_payments: "list[PydtcPayment]") -> "list[PydtcPayment]":

  payments = p_payments[:]
  nonrepeats, repeats = [], []
  while len(payments) > 0:
    payment = payments.pop(0)
    boolst = [payment == op for op in payments]
    if True in boolst:
      repeats.append(payment)
    else:
      nonrepeats.append(payment)
  return nonrepeats, repeats


class PydtcPayment(pydantic.BaseModel):
  """
  Models the contract's monthly payment.

  """
  datahora: datetime.datetime
  value: Decimal
  payor: Optional[pers.PydtcPerson] = None
  refdoc: Optional[str] = None
  comment: Optional[str] = None

  @pydantic.model_validator(mode='before')
  @classmethod
  def allow_fetching_payor_by_cpf(cls, values: dict) -> dict:
    # if the user passed a raw string/number instead of a person object
    if "payor_cpf" in values and "payor" not in values:
      payor_cpf = values.pop("payor_cpf")
      values["payor"] = pers.fetch_pydtcperson_by_cpf(payor_cpf)
    return values

  @pydantic.computed_field
  @property
  def payor_cpf(self) -> str | None:
    if self.payor is not None:
      return self.payor.cpf
    return None

  @property
  def daytime(self) -> time:
    return self.datahora.time()  # Returns a datetime.time object

  @property
  def date(self) -> date:
    return self.datahora.date()

  def adjust_hora_to_paydt(self, pdaytime) -> None:
    pdate = self.datahora.date()
    self.datahora = datetime.datetime.combine(pdate, pdaytime)
    _ = self.datahora

  @property
  def triple_y_m_d(self) -> tuple[int, int, int]:
    dt = self.datahora
    year, month, day = dt.year, dt.month, dt.day
    return year, month, day

  @property
  def triple_h_m_s(self):
    dt = self.datahora
    hour, minute, second = dt.hour, dt.minute, dt.second
    return hour, minute, second

  def to_json(self, indent=2, is_for_db: bool = False) -> str:
    if is_for_db:
      excludeset = {'payor'}
      json_str = self.model_dump_json(exclude=excludeset, indent=indent)
      return json_str
    json_str = self.model_dump_json(indent=indent)
    return json_str

  @classmethod
  def instantiate_fr_jsonstr(cls, json_str: str) -> "PydtcPayment":
    obj = cls.model_validate_json(json_str)
    return obj

  @classmethod
  def instantiate_fr_jsondict(cls, json_dict: dict) -> "PydtcPayment":
    obj = cls.model_validate(json_dict)
    return obj

  def at_same_moment(self, other: object) -> bool:
    try:
      if self.triple_y_m_d == other.triple_y_m_d:
        if self.triple_h_m_s == other.triple_h_m_s:
          return True
      return False
    except AttributeError:
      pass
    return False

  def __eq__(self, other: object) -> bool:
    if self.at_same_moment(other):
      thisval = fm_mnts.sigfig(self.value, 18)
      thatval = fm_mnts.sigfig(self.other.value, 18)
      return thisval == thatval
    return False

  def __str__(self) -> str:
    dt = self.datahora.strftime("%d/%m/%Y às %H:%M:%S")
    val = f"{self.value:.02f}"
    payorcpf = "n/a"
    if isinstance(self.payor_cpf, str):
      payorcpf = self.payor_cpf
    ostr = f"Payment (dt={dt}, val={val}, cpf={payorcpf})"
    return ostr


def adhoctest1():
  dt1 = dtfs.make_current_datetime_w_horazero()
  payment = PydtcPayment(
    datahora=dt1,
    value=Decimal(2000),
  )
  print(payment)
  json_str = payment.to_json(indent=2, is_for_db=True)
  print(json_str)
  hora = datetime.time(hour=11, minute=11)
  print(hora)
  payment.adjust_hora_to_paydt(hora)
  json_str = payment.to_json(indent=2, is_for_db=True)
  print(json_str)
  print(payment)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
