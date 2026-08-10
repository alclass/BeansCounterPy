#!/usr/bin/env python3
"""
art/fnc/credeb_accomp/dictdata_fo_monthly_credeb_accomp.py
  This is a data-dictlist module to be inserted in a DB "later on".
  When this time comes, db-field 'is_closed' should be set to True
    and data should only be changed/edited by also rerunning the series,
    because the final values of one month are initial values input to the next one.

To imported:
  art.immeub.inst.cdutra.aliss_dc_accomp.accdata_deb_cre_alssn as accdt.items
"""
from decimal import Decimal
import art.fnc.credeb_accomp as init
dec_monthlymeta_brl_value = Decimal(init.DEFAULT_VALOR_META_MENSAL_IN_BRL)
import lib.fncfs.credeb_pkg.credit_debit_fs as cdfs  # cdfs.debit_or_credit_value_to_accounts
DECIMAL_ZERO = cdfs.DECIMAL_ZERO
makedec = cdfs.make_decimal_w_appcontext


items = []
inivalue_d1 = makedec('-24458.75')
item = {
  'refmonth': '2025-11',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': DECIMAL_ZERO,
  'inivalue_d2': DECIMAL_ZERO,
  'cre_in_tasks': makedec(302.58),
  'cre_in_pay': makedec(600.0),
  'cre_in_trnsp_n_frut': DECIMAL_ZERO,
  'deb_giro': DECIMAL_ZERO,
}
items.append(item)
inivalue_d1 += dec_monthlymeta_brl_value
item = {
  'refmonth': '2025-12',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': DECIMAL_ZERO,
  'cre_in_pay': makedec(600),
  'cre_in_trnsp_n_frut': makedec(-500.0),
  'deb_giro': DECIMAL_ZERO,
}
items.append(item)
inivalue_d1 += dec_monthlymeta_brl_value
item = {
  'refmonth': '2026-01',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': DECIMAL_ZERO,
  'cre_in_pay': makedec(500),
  'cre_in_trnsp_n_frut': DECIMAL_ZERO,
  'deb_giro': DECIMAL_ZERO,
}
items.append(item)
cre_concedido_p_arrend = makedec(58.75)
inivalue_d1 += dec_monthlymeta_brl_value + cre_concedido_p_arrend
item = {
  'refmonth': '2026-02',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': DECIMAL_ZERO,
  'cre_in_pay': DECIMAL_ZERO,
  'cre_in_trnsp_n_frut': DECIMAL_ZERO,
  'deb_giro': DECIMAL_ZERO,
}
items.append(item)
inivalue_d1 += dec_monthlymeta_brl_value
item = {
  'refmonth': '2026-03',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': makedec(114.32),
  'cre_in_pay': DECIMAL_ZERO,
  'cre_in_trnsp_n_frut': makedec(26.77),
  'deb_giro': makedec(-200)
}
items.append(item)
inivalue_d1 += dec_monthlymeta_brl_value
item = {
  'refmonth': '2026-04',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': makedec(210.62),
  'cre_in_pay': DECIMAL_ZERO,
  'cre_in_trnsp_n_frut': makedec(45.68),
  'deb_giro': makedec(-650.0)
}

items.append(item)
inivalue_d1 += dec_monthlymeta_brl_value
item = {
  'refmonth': '2026-05',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': makedec(391.65),
  'cre_in_pay': DECIMAL_ZERO,
  'cre_in_trnsp_n_frut': makedec(163.41),
  'deb_giro': makedec(-50.0),
}
items.append(item)
inivalue_d1 += dec_monthlymeta_brl_value
item = {
  'refmonth': '2026-06',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': makedec(556.15),
  'cre_in_pay': DECIMAL_ZERO,
  'cre_in_trnsp_n_frut': makedec(196.22),
  'deb_giro': makedec(-700),
}
items.append(item)
inivalue_d1 += dec_monthlymeta_brl_value
item = {
  'refmonth': '2026-07',
  'inivalue_d1': inivalue_d1,
  'inivalue_res': None,
  'inivalue_d2': None,
  'cre_in_tasks': makedec(330.73),
  'cre_in_pay': DECIMAL_ZERO,
  'cre_in_trnsp_n_frut': makedec(72.45),
  'deb_giro': makedec(-450),
}
items.append(item)
# for item in items:
#   print(item)
