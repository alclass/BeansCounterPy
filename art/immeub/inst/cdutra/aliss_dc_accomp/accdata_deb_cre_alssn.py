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
items = []
ic_inivalue_d1 = 24458.75 * 100
item = {
  'refmonth': '2025-11',
  'ic_inivalue_d1': ic_inivalue_d1,
  'ic_inivalue_res': 0,
  'ic_inivalue_d2': 0,
  'ic_cre_in_tasks': 302.58 * 100,
  'ic_cre_in_pay': 600.0 * 100,
  'ic_cre_in_trnsp_n_frut': 0,
  'ic_deb_giro': 0,
}
items.append(item)
ic_monthlymeta = 500 * 100
ic_inivalue_d1 -= ic_monthlymeta
item = {
  'refmonth': '2025-12',
  'ic_inivalue_d1': ic_inivalue_d1,
  'ic_inivalue_res': None,
  'ic_inivalue_d2': None,
  'ic_cre_in_tasks': 0,
  'ic_cre_in_pay': 600.0 * 100,
  'ic_cre_in_trnsp_n_frut': -500.0 * 100,
  'ic_deb_giro': 0,
}
items.append(item)
ic_inivalue_d1 -= ic_monthlymeta
item = {
  'refmonth': '2026-01',
  'ic_inivalue_d1': ic_inivalue_d1,
  'ic_inivalue_res': None,
  'ic_inivalue_d2': None,
  'ic_cre_in_tasks': 0,
  'ic_cre_in_pay': 500.0 * 100,
  'ic_cre_in_trnsp_n_frut': 0,
  'ic_deb_giro': 0.0,
}
items.append(item)
ic_cre_concedido_p_arrend = 58.75 * 100
ic_inivalue_d1 -= ic_monthlymeta - ic_cre_concedido_p_arrend
item = {
  'refmonth': '2026-02',
  'ic_inivalue_d1': ic_inivalue_d1,
  'ic_inivalue_res': None,
  'ic_inivalue_d2': None,
  'ic_cre_in_tasks': 0.0,
  'ic_cre_in_pay': 0.0,
  'ic_cre_in_trnsp_n_frut': 0.0,
  'ic_deb_giro': 0.0,
}
items.append(item)
ic_inivalue_d1 -= ic_monthlymeta
item = {
  'refmonth': '2026-03',
  'ic_inivalue_d1': ic_inivalue_d1,
  'ic_inivalue_res': None,
  'ic_inivalue_d2': None,
  'ic_cre_in_tasks': 114.32 * 100,
  'ic_cre_in_pay': 0,
  'ic_cre_in_trnsp_n_frut': 26.77 * 100,
  'ic_deb_giro': -200.0 * 100,
}
items.append(item)
ic_inivalue_d1 -= ic_monthlymeta
item = {
  'refmonth': '2026-04',
  'ic_inivalue_d1': ic_inivalue_d1,
  'ic_inivalue_res': None,
  'ic_inivalue_d2': None,
  'ic_cre_in_tasks': 210.62 * 100,
  'ic_cre_in_pay': 0,
  'ic_cre_in_trnsp_n_frut': 45.68 * 100,
  'ic_deb_giro': -650.0 * 100,
}

items.append(item)
ic_inivalue_d1 -= ic_monthlymeta
item = {
  'refmonth': '2026-05',
  'ic_inivalue_d1': ic_inivalue_d1,
  'ic_inivalue_res': None,
  'ic_inivalue_d2': None,
  'ic_cre_in_tasks': 391.65 * 100,
  'ic_cre_in_pay': 0,
  'ic_cre_in_trnsp_n_frut': 163.41 * 100,
  'ic_deb_giro': -50.0 * 100,
}
items.append(item)
ic_inivalue_d1 -= ic_monthlymeta
item = {
  'refmonth': '2026-06',
  'ic_inivalue_d1': ic_inivalue_d1,
  'ic_inivalue_res': None,
  'ic_inivalue_d2': None,
  'ic_cre_in_tasks': 556.15 * 100,
  'ic_cre_in_pay': 0,
  'ic_cre_in_trnsp_n_frut': 196.22 * 100,
  'ic_deb_giro': -700.0 * 100,
}
items.append(item)
