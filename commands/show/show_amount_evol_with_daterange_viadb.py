#!/usr/bin/env python3
""""
show_amount_evol_with_daterange_viadatafile.py
  prints to stdout a report with triple rends (no mês, no ano, últimos 12 meses) for all banks with a date range
  (this script searches via extract text files [there's another version that searches via db])
"""
import sys
import fs.datesetc.datefs as dtfs
import fs.numbers.transform_numbers as transfn
import commands.db.scrape_monthly_rendextracts as scr_bb_extrs


def transpose_dict(fundo_results_dictlist):
  """
  The source dist is a field value 1-D one
  The target dict, transposed, has the following schema:
  - fundoname
    - refmonthdate
      - nomes
      - noano
      - ult12m
  """
  transposed_dict = {}
  fundonames = []
  for fundo_results_dict in fundo_results_dictlist:
    for fieldname in fundo_results_dict:
      if fieldname == 'name':
        value = fundo_results_dict[fieldname]
        fundonames.append(value)
  fundonames = list(set(fundonames))
  for name in fundonames:
    transposed_dict[name] = {}
  for fundo_results_dict in fundo_results_dictlist:
    name = fundo_results_dict['name']
    dict_for_name = transposed_dict[name]  # initially it's {}
    refmonthdate = fundo_results_dict['refmonthdate']
    dict_for_name[refmonthdate] = {}
    for fieldname in fundo_results_dict:
      if fieldname in ['prct_rend_mes', 'saldo_atual', 'rend_bruto', 'rend_liq']:
        dict_for_name[refmonthdate][fieldname] = fundo_results_dict[fieldname]
  return transposed_dict


def get_daterange_args():
  monthref_ini = None
  monthref_fim = None
  for arg in sys.argv:
    if arg.startswith('-ini='):
      monthref_ini = arg[len('-ini='):]
    elif arg.startswith('-fim='):
      monthref_fim = arg[len('-fim='):]
  outdict = {'monthref_ini': monthref_ini, 'monthref_fim': monthref_fim}
  return dtfs.transform_yyyydashmm_to_daterange_in_refmonth_dict(outdict)


def get_fundo_results_dictlist_within_daterange(monthref_ini, monthref_fim):
  roller = scr_bb_extrs.MonthlyRoller(yearmonth_ini=monthref_ini, yearmonth_fim=monthref_fim)
  roller.process()
  return roller.fundo_result_records[:]


def show_results(transpose_to_triplerend_dict):
  total_rend_bruto = 0
  total_monthfundos = 0
  for fundoname in transpose_to_triplerend_dict:
    dict_for_name = transpose_to_triplerend_dict[fundoname]
    print(fundoname)
    refmonthdates = dict_for_name.keys()
    sorted(refmonthdates)
    for refmonthdate in refmonthdates:
      total_monthfundos += 1
      tripledict = dict_for_name[refmonthdate]
      print('\t ', refmonthdate)
      rend_bruto = tripledict['rend_bruto']
      print('\t rend_bruto', )
      total_rend_bruto += rend_bruto
      print('\t rend_liq', tripledict['rend_liq'])
      print('\t prct_rend_mes', tripledict['prct_rend_mes'])
      print('\t saldo_atual', tripledict['saldo_atual'])
    strmoney = '${:,.2f}'.format(total_rend_bruto)
    strmoney = transfn.place_thousand_dots_in_number_as_strnumber(strmoney)
    print('total_rend_bruto', strmoney)
    print('total_monthfundos', total_monthfundos)


def process():
  daterange_dict = get_daterange_args()
  monthref_ini = daterange_dict['monthref_ini']
  monthref_fim = daterange_dict['monthref_fim']
  fundo_results_dictlist = get_fundo_results_dictlist_within_daterange(monthref_ini, monthref_fim)
  transpose_to_triplerend_dict = transpose_dict(fundo_results_dictlist)
  show_results(transpose_to_triplerend_dict)


def test_some_yyyydashmm_dates():
  print('test_some_yyyydashmm_dates')
  strdaterange_tuplelist = [('2022-04', '2023-04'), ('2018-10', '2020-01')]
  for strdaterange_tuple in strdaterange_tuplelist:
    monthref_ini = strdaterange_tuple[0]
    monthref_fim = strdaterange_tuple[1]
    strdaterange_dict = {'monthref_ini': monthref_ini, 'monthref_fim': monthref_fim}
    daterange_dict = dtfs.transform_yyyydashmm_to_daterange_in_refmonth_dict(strdaterange_dict)
    print(strdaterange_dict, '=>', daterange_dict)


if __name__ == '__main__':
  process()
  # test_some_yyyydashmm_dates()
