#!/usr/bin/env python3
""""
show_triplerend_with_daterange_viadatafile.py
  prints to stdout a report with triple rends (no mês, no ano, últimos 12 meses) for all banks with a date range
"""
import sqlite3
import sys
import settings as sett
import fs.datesetc.datefs as dtfs
# import scrapers.bbfi.scraper_monthly_rendextracts as scr_bb_extrs


class TripleRend:

  def __init__(self, refmonthdate_ini, refmonthdate_fim=None):
    self.refmonthdate_ini = refmonthdate_ini
    self.refmonthdate_fim = refmonthdate_fim

  def do_select_within_refmonthdate_range(self):
    refmonthdate_fim = dtfs.validate_refmonthdate_or_morerecent(self.refmonthdate_fim)
    refmonthdate_ini = dtfs.validate_refmonthdate_or_1monthbefore_the_2ndparam(
        self.refmonthdate_ini,
        self.refmonthdate_fim
    )
    sql = """
    SELECT prct_rend_mes, prct_rend_desdeano, prct_rend_12meses from dbfi
      WHERE
        refmonthdate >= % and
        refmonthdate <= %
    """
    tuplevalues = (refmonthdate_ini, refmonthdate_fim)
    conn = sqlite3.connect(sett.get_app_sqlite_filepath())
    cursor = conn.cursor()
    cursor.execute(sql, tuplevalues)

  def show_results1(self, fundo_results_dictlist):
    for fresultdict in fundo_results_dictlist:
      print(fresultdict['name'], '| refmonth', fresultdict['refmonthdate'])
      print('\t no mês', fresultdict['prct_rend_mes'])
      print('\t no ano', fresultdict['prct_rend_desdeano'])
      print('\t nos últs 12m', fresultdict['prct_rend_12meses'])
      print()

  def show_results2(self, transpose_to_triplerend_dict):
    for fundoname in transpose_to_triplerend_dict:
      dict_for_name = transpose_to_triplerend_dict[fundoname]
      print(fundoname)
      refmonthdates = dict_for_name.keys()
      sorted(refmonthdates)
      for refmonthdate in refmonthdates:
        tripledict = dict_for_name[refmonthdate]
        print('\t ', refmonthdate)
        print('\t prct_rend_mes', tripledict['prct_rend_mes'])
        print('\t prct_rend_desdeano', tripledict['prct_rend_desdeano'])
        print('\t prct_rend_12meses', tripledict['prct_rend_12meses'])
      print()

  def process(self):
    """
    fundo_results_dictlist = get_fundo_results_dictlist_within_daterange(monthref_ini, monthref_fim)
    transpose_to_triplerend_dict = transpose_dict(fundo_results_dictlist)
    show_results2(transpose_to_triplerend_dict)

    """
    pass


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


def process():
  daterange_dict = get_daterange_args()
  monthref_ini = daterange_dict['monthref_ini']
  monthref_fim = daterange_dict['monthref_fim']
  triple = TripleRend(monthref_ini, monthref_fim)
  triple.process()


if __name__ == '__main__':
  process()
  # test_some_yyyydashmm_dates()
