"""
art/fnc/credeb_accomp/fastapi/models/credeb_pydanticmodels.py
  Contains class PydanticCreDebAcc which is copied from an existing @dataclass class.


"""
import datetime
import pydantic
from decimal import Decimal
import lib.fncfs.credeb_pkg.credit_debit_fs as cdfs  # cdfs.debit_or_credit_value_to_accounts
import art.fnc.credeb_accomp.credeb_accompanying_mod as cdaccomp
import art.fnc.credeb_accomp as cdinit
from art.immeub.rent.pydantmodels import DEFAULT_3LETTER_CURRENCY
DEFAULT_DEC_VALOR_META_MENSAL_BRL = Decimal(cdinit.DEFAULT_VALOR_META_MENSAL_IN_BRL)
REFMONTH_BEGINNING_THE_SERIES = cdinit.REFMONTH_BEGINNING_THE_SERIES
DEFAULT_MORA_FIX_DEC = cdfs.make_decimal_w_appcontext(cdinit.DEFAULT_MORA_FIX_FLOAT, n_decimal_places=6)
DECIMAL_ZERO = cdfs.DECIMAL_ZERO


class PydanticCreDebAcc(pydantic.BaseModel):
  """
  Models the CreDed object via Pydantic. As given, it ininherits from pydantic.BaseModel.

  As, at the moment, this class defines only fields, it's very similar to its @dataclass class original.

  A Pydantic object can handle the JSON sending and receiving in the request/response cycle,
    avoiding creating JSON serializers/deserializers. It does other things as well like type-value-validations.

  However, we still have to look into class beanie.Document (which inherits from pydantic.BaseModel)
    for async MongoDB CRUD operations.
  """
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
  # this last 3 attributes may not be necessary for the web-client (to think about it)
  # but still necessary for processing and db-saving
  bool_updt_saldos_has_run: bool = False
  is_closed: bool = True
  is_data_from_db: bool = False


def trnsf_credeb_dataclass_obj_to_pydantic(credeb_dataclass_obj):
  """
  Transforms a @dataclass object to a Pydantic object.

  To import this elsewhere:
    import art.fnc.credeb_accomp.fastapi.models.pydanticmodels as pydtc  # pydtc.trnsf_credeb_dataclass_objs_to_pydantic
    (check also whether path has been changed)
  """
  pdict = credeb_dataclass_obj.asdict_fo_pydantic()
  pydantic_obj = PydanticCreDebAcc(**pdict)
  return pydantic_obj


def trnsf_credeb_dataclass_objs_to_pydantic(credeb_dataclass_objs):
  """
  Transforms a list of @dataclass objects into a list of Pydantic objects.


  To import this elsewhere:
    import art.fnc.credeb_accomp.fastapi.models.pydanticmodels as pydtc  # pydtc.trnsf_credeb_dataclass_objs_to_pydantic
    (check also whether path has been changed)

  """
  pydantics = [PydanticCreDebAcc(**db_o.asdict_fo_pydantic()) for db_o in credeb_dataclass_objs]
  return pydantics


def run_a_transformation_dataclass_to_pydantic_fr_a_datadict():
  dataclass_objs = cdaccomp.get_months_closings_w_dictdata()
  pydantci_objs = trnsf_credeb_dataclass_objs_to_pydantic(dataclass_objs)
  print('dataclass_objs')
  print(dataclass_objs)
  print('pydantci_objs')
  for i, pydantic_obj in enumerate(pydantci_objs):
    seq = i + 1
    print(seq, pydantic_obj)


def adhoctest1():
  run_a_transformation_dataclass_to_pydantic_fr_a_datadict()


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()

