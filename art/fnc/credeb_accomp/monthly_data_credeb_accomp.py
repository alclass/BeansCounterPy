#!/usr/bin/env python3
"""
art/immeub/inst/cdutra/aliss_dc_accomp/monthly_data_credeb_accomp.py
  This is a data-dictlist module to be inserted in a DB "later on".
  When this time comes, db-field 'is_closed' should be set to True
    and data should only be changed/edited by also rerunning the series,
    because the final values of one month are initial values input to the next one.

To imported:
  art.immeub.inst.cdutra.aliss_dc_accomp.accdata_deb_cre_alssn as accdt.items
"""
import dinero
from dinero import Dinero
from dinero.currencies import BRL


def get_brl_dinero(value):
  if isinstance(value, Dinero):
    return value
  try:
    flo = float(value)
    din = Dinero(flo, BRL)
    return din
  except ValueError:
    pass
  try:
    strvalue = str(value)
    # if strvalue is a representation of Dinero, it may contain ',' for thousands
    # which should be removed or else a dinero.exceptions.InvalidOperationError exception will be raised
    strvalue = strvalue.replace(',', '')
    din = Dinero(strvalue, BRL)
    return din
  except dinero.exceptions.InvalidOperationError as e:
    errmsg = f"Error: The value {value} (type {type(value)}) is not a valid dinero."
    raise ValueError(errmsg + str(e))



items = []
inivalue_d1 = Dinero(-24458.75, BRL)
dinero_zero = Dinero('0', BRL)
item = {
  'refmonth': '2025-11',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': dinero_zero,
  'inivalue_d2': dinero_zero,
  'cre_in_tasks': get_brl_dinero(302.58),
  'cre_in_pay': get_brl_dinero(600.0),
  'cre_in_trnsp_n_frut': dinero_zero,
  'deb_giro': dinero_zero,
}
items.append(item)
monthlymeta = get_brl_dinero(500)
inivalue_d1 += monthlymeta
item = {
  'refmonth': '2025-12',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': dinero_zero,
  'cre_in_pay': get_brl_dinero(600),
  'cre_in_trnsp_n_frut': get_brl_dinero(-500.0),
  'deb_giro': dinero_zero,
}
items.append(item)
inivalue_d1 += monthlymeta
item = {
  'refmonth': '2026-01',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': dinero_zero,
  'cre_in_pay': get_brl_dinero(500),
  'cre_in_trnsp_n_frut': dinero_zero,
  'deb_giro': dinero_zero,
}
items.append(item)
cre_concedido_p_arrend = get_brl_dinero(58.75)
inivalue_d1 += monthlymeta + cre_concedido_p_arrend
item = {
  'refmonth': '2026-02',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': dinero_zero,
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': dinero_zero,
  'deb_giro': dinero_zero,
}
items.append(item)
inivalue_d1 += monthlymeta
item = {
  'refmonth': '2026-03',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': get_brl_dinero(114.32),
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': get_brl_dinero(26.77),
  'deb_giro': get_brl_dinero(-200)
}
items.append(item)
inivalue_d1 += monthlymeta
item = {
  'refmonth': '2026-04',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': get_brl_dinero(210.62),
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': get_brl_dinero(45.68),
  'deb_giro': get_brl_dinero(-650.0)
}

items.append(item)
inivalue_d1 += monthlymeta
item = {
  'refmonth': '2026-05',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': get_brl_dinero(391.65),
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': get_brl_dinero(163.41),
  'deb_giro': get_brl_dinero(-50.0),
}
items.append(item)
inivalue_d1 += monthlymeta
item = {
  'refmonth': '2026-06',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': get_brl_dinero(556.15),
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': get_brl_dinero(196.22),
  'deb_giro': get_brl_dinero(-700),
}
items.append(item)
inivalue_d1 += monthlymeta
item = {
  'refmonth': '2026-07',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': get_brl_dinero(330.73),
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': get_brl_dinero(72.45),
  'deb_giro': get_brl_dinero(-450),
}
items.append(item)
# for item in items:
#   print(item)
