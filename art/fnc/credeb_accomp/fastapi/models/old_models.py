# Pydantic Schemas
class DebCredBase(BaseModel):
  refmonth: date
  inivalue_d1: Decimal
  inivalue_d2: Decimal
  inivalue_res: Decimal
  cre_in_tasks: Decimal
  cre_in_pay: Decimal
  cre_in_trnsp_n_frut: Decimal
  deb_giro: Decimal
  valor_cre_a_d1_no_mes: Decimal = DEFAULT_VALOR_META_MENSAL_IN_BRL
  currency3letter: str = cd_accomp.DEFAULT_3LETTER_CURRENCY


class DebCredCreate(DebCredBase):
  pass


class DebCredUpdate(BaseModel):
  refmonth: Optional[date] = None
  inivalue_d1: Optional[Decimal] = None
  inivalue_d2: Optional[Decimal] = None
  inivalue_res: Optional[Decimal] = None
  cre_in_tasks: Optional[Decimal] = None
  cre_in_pay: Optional[Decimal] = None
  cre_in_trnsp_n_frut: Optional[Decimal] = None
  deb_giro: Optional[Decimal] = None
  fix_ir_dec: Optional[Decimal] = None
  valor_cre_a_d1_no_mes: Optional[Decimal] = None


class DebCredResponse(DebCredBase):
  id: str
  corrmone_n_intrst_if_any: Optional[Decimal] = None
  ipca_dec: Optional[Decimal] = None
  fix_ir_dec: Optional[Decimal] = None
  finvalue_d1: Optional[Decimal] = None
  finvalue_d2: Optional[Decimal] = None
  finvalue_res: Optional[Decimal] = None
  is_closed: bool = False
