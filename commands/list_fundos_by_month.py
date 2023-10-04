#!/usr/bin/env python3
"""
list_fundos_by_month.py

"""
import os
# import fs.db.dbasfolder.discover_bbfi_datadirections as discbbfi
import fs.datesetc.datefs as dtfs

import fs.db.reader_fundoresults_db as dbread
# from prettytable import PrettyTable, ALL, FRAME
# from prettytable import PrettyTable
import pandas as pd
import settings as sett


def printout(pdict):
  print(pdict['name'])
  print(pdict['prct_rend_mes'], '\t', pdict['prct_rend_mes'], '\t', pdict['prct_rend_12meses'], )


def diminish_some_columns_in_dictlist(dictlist):
  """
  columns to exclude from dictlist:
    id | refmonthdate | cnpj | data_saldo_ant | data_saldo_atu
  """
  exclude_cols = ['id', 'refmonthdate', 'cnpj', 'data_saldo_ant', 'data_saldo_atu']
  outdictlist = []
  for pdict in dictlist:
    for col in exclude_cols:
      del pdict[col]
    outdictlist.append(pdict)
  return outdictlist


def gen_report_with_monthrange(refmonthdate_ini, refmonthdate_fim):
  """
    for pdict in reader.fundoresults_dictlist:
    printout(pdict)

  tab.hrules = ALL
  tab.vrules = FRAME
  tab.int_format = '8'
  tab.padding_width = 2
  tab.junction_char = '.'
  # tab.sortby = 'col 2'

  dict0 = dictlist[0]
  fieldnames = list(dict0.keys())
  datalist = [list(d.values()) for d in dictlist]
  print(reader)
  tab = PrettyTable(fieldnames)
  tab.add_rows(datalist)
  print(tab)

  """
  # dbfi_finder = discbbfi.get_dbfi_finder()
  reader = dbread.DBReader()
  reader.read_db_within_refmonthdates(refmonthdate_ini=refmonthdate_ini, refmonthdate_fim=refmonthdate_fim)
  dictlist = reader.fundoresults_dictlist
  dictlist = diminish_some_columns_in_dictlist(dictlist)
  pd_data = pd.DataFrame(dictlist)
  excel_filename = str(refmonthdate_fim)[:7] + '_pandas_excel.xlsx'
  excel_filepath = os.path.join(sett.get_apps_data_abspath(), excel_filename)
  print('writing', excel_filepath)
  pd_data.to_excel(excel_writer=excel_filepath)
  print(pd_data)


def process():
  refmonthdate_ini = '2023-01-01'
  refmonthdate_fim = '2023-06-01'
  for refmonthdate in dtfs.generate_monthrange(refmonthdate_ini, refmonthdate_fim):
    gen_report_with_monthrange(refmonthdate, refmonthdate)  # both are the same so month by month is generated


if __name__ == '__main__':
  process()
