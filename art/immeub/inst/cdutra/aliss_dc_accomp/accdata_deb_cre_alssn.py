#!/usr/bin/env python3
"""
art/immeub/inst/cdutra/aliss_dc_accomp/accdata_deb_cre_alssn.py
  This is a data-dictlist module to be inserted in a DB "later on".
  When this time comes, db-field 'is_closed' should be set to True
    and data should only be changed/edited by also rerunning the series,
    because the final values of one month are initial values input to the next one.

To imported:
  art.immeub.inst.cdutra.aliss_dc_accomp.accdata_deb_cre_alssn as accdt.items
"""
from dinero import Dinero
from dinero.currencies import BRL


def get_brl_dinero(value):
  return Dinero(str(value), BRL)


items = []
inivalue_d1 = Dinero(24458.75, BRL)
dinero_zero = Dinero('0', BRL)
item = {
  'refmonth': '2025-11',
  'inivalue_d1': inivalue_d1,
  '_inivalue_res': dinero_zero,
  '_inivalue_d2': dinero_zero,
  'cre_in_tasks': get_brl_dinero(302.58),
  'cre_in_pay': get_brl_dinero(600.0),
  'cre_in_trnsp_n_frut': dinero_zero,
  'deb_giro': dinero_zero,
}
items.append(item)
monthlymeta = get_brl_dinero(500)
inivalue_d1 -= monthlymeta
item = {
  'refmonth': '2025-12',
  'inivalue_d1': inivalue_d1,
  '_inivalue_res': None,
  '_inivalue_d2': None,
  'cre_in_tasks': dinero_zero,
  'cre_in_pay': get_brl_dinero(600),
  'cre_in_trnsp_n_frut': get_brl_dinero(-500.0),
  'deb_giro': dinero_zero,
}
items.append(item)
inivalue_d1 -= monthlymeta
item = {
  'refmonth': '2026-01',
  'inivalue_d1': inivalue_d1,
  '_inivalue_res': None,
  '_inivalue_d2': None,
  'cre_in_tasks': dinero_zero,
  'cre_in_pay': get_brl_dinero(500),
  'cre_in_trnsp_n_frut': dinero_zero,
  'deb_giro': dinero_zero,
}
items.append(item)
cre_concedido_p_arrend = get_brl_dinero(58.75)
inivalue_d1 -= monthlymeta + cre_concedido_p_arrend
item = {
  'refmonth': '2026-02',
  'inivalue_d1': inivalue_d1,
  '_inivalue_res': None,
  '_inivalue_d2': None,
  'cre_in_tasks': dinero_zero,
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': dinero_zero,
  'deb_giro': dinero_zero,
}
items.append(item)
inivalue_d1 -= monthlymeta
item = {
  'refmonth': '2026-03',
  'inivalue_d1': inivalue_d1,
  '_inivalue_res': None,
  '_inivalue_d2': None,
  'cre_in_tasks': get_brl_dinero(114.32),
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': get_brl_dinero(26.77),
  'deb_giro': get_brl_dinero(-200)
}
items.append(item)
inivalue_d1 -= monthlymeta
item = {
  'refmonth': '2026-04',
  'inivalue_d1': inivalue_d1,
  '_inivalue_res': None,
  '_inivalue_d2': None,
  'cre_in_tasks': get_brl_dinero(210.62),
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': get_brl_dinero(45.68),
  'deb_giro': get_brl_dinero(-650.0)
}

items.append(item)
inivalue_d1 -= monthlymeta
item = {
  'refmonth': '2026-05',
  'inivalue_d1': inivalue_d1,
  '_inivalue_res': None,
  '_inivalue_d2': None,
  'cre_in_tasks': get_brl_dinero(391.65),
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': get_brl_dinero(163.41),
  'deb_giro': get_brl_dinero(-50.0),
}
items.append(item)
inivalue_d1 -= monthlymeta
item = {
  'refmonth': '2026-06',
  'inivalue_d1': inivalue_d1,
  '_inivalue_res': None,
  '_inivalue_d2': None,
  'cre_in_tasks': get_brl_dinero(556.15),
  'cre_in_pay': dinero_zero,
  'cre_in_trnsp_n_frut': get_brl_dinero(196.22),
  'deb_giro': get_brl_dinero(-700),
}
items.append(item)
