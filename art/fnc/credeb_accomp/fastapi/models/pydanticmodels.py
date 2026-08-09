import datetime
import pydantic
from decimal import Decimal
import lib.fncfs.dinerofs.credit_debit_fs as cdfs  # cdfs.debit_or_credit_value_to_accounts
import art.fnc.credeb_accomp as init
from art.immeub.rent.pydantmodels import DEFAULT_3LETTER_CURRENCY
import art.fnc.credeb_accomp.credeb_accompanying_mod as cd_accomp
DEFAULT_DEC_VALOR_META_MENSAL_BRL = Decimal(init.DEFAULT_VALOR_META_MENSAL_IN_BRL)
REFMONTH_BEGINNING_THE_SERIES = init.REFMONTH_BEGINNING_THE_SERIES
DEFAULT_MORA_FIX_DEC = cdfs.make_decimal_w_appcontext(init.DEFAULT_MORA_FIX_FLOAT, n_decimal_places=6)
DECIMAL_ZERO = cdfs.DECIMAL_ZERO


class PydanticCreDebAcc(pydantic.BaseModel):
  refmonth: datetime.date
  inivalue_d1: Decimal
  inivalue_d2: Decimal
  inivalue_res: Decimal
  cre_in_tasks: Decimal
  cre_in_pay: Decimal
  cre_in_trnsp_n_frut: Decimal
  deb_giro: Decimal
  valor_cre_a_d1_no_mes: Decimal = pydantic.Field(default_factory=lambda: DEFAULT_DEC_VALOR_META_MENSAL_BRL)
  corrmone_n_intrst_if_any: Decimal = pydantic.Field(default_factory=lambda: None)
  ipca_dec: Decimal | None = pydantic.Field(default_factory=lambda: None)
  fix_ir_dec: Decimal = pydantic.Field(default_factory=lambda: DEFAULT_MORA_FIX_DEC)
  finvalue_d1: Decimal = pydantic.Field(default_factory=lambda: None)
  finvalue_d2: Decimal = pydantic.Field(default_factory=lambda: None)
  finvalue_res: Decimal = pydantic.Field(default_factory=lambda: None)
  currency3letter: str = DEFAULT_3LETTER_CURRENCY
  bool_updt_saldos_has_run: bool = False
  is_closed: bool = True
  is_data_from_db: bool = False  # so, it's a flag to avoid __post_init__() execution


def trnsf_credeb_dataclass_obj_to_pydantic(credeb_dataclass_obj):
  pdict = credeb_dataclass_obj.asdict_fo_pydantic()
  pydantic_obj = PydanticCreDebAcc(**pdict)
  return pydantic_obj


def trnsf_credeb_dataclass_objs_to_pydantic(credeb_dataclass_objs):
  """
  To import this:
    import art.fnc.credeb_accomp.fastapi.models.pydanticmodels as pydtc  # pydtc.trnsf_credeb_dataclass_objs_to_pydantic

  alist = cd_accomp.get_months_closings_w_dictdata()
  print(alist)
  for db_o in alist:
    _ = PydanticCreDebAcc(**db_o.asdict_fo_pydantic()
  """
  pydantics = [PydanticCreDebAcc(**db_o.asdict_fo_pydantic()) for db_o in credeb_dataclass_objs]
  return pydantics


def adhoctest1():
  pass


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()

