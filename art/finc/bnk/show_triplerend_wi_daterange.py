#!/usr/bin/env python3
"""
art/finc/bnk/show_triplerend_wi_daterange.py
  Prints to stdout a report with triple rends (no mês, no ano, últimos 12 meses)
    for all models within/through a date range
"""
import sqlite3
import sys
from dateutil.relativedelta import relativedelta
import settings as sett
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
# import scrapers.bbfi.scraper_monthly_rendextracts as scr_bb_extrs


class TripleRend:

  def __init__(self, refmonth_ini, refmonth_fim=None):
    self.refmonth_ini = refmonth_ini
    self.refmonth_fim = refmonth_fim
    self.treat_attrs()
    self.fundo_results_dictlist = []

  def treat_attrs(self):
    self.refmonth_fim = rmfs.make_refmonth_or_current(self.refmonth_fim)
    self.refmonth_ini = rmfs.make_refmonth_or_none(self.refmonth_ini)
    if self.refmonth_ini is None:
      self.refmonth_ini = self.refmonth_fim - relativedelta(months=1)

  def select_wi_refmonth_range(self):
    sql = """
    SELECT prct_rend_mes, prct_rend_desdeano, prct_rend_12meses, mes, nomefundo from dbfi
      WHERE
        refmonthdate >= % and
        refmonthdate <= %
    """
    tuplevalues = (self.refmonth_ini, self.refmonth_fim)
    conn = sqlite3.connect(sett.get_app_sqlite_filepath())
    cursor = conn.cursor()
    retval = cursor.execute(sql, tuplevalues)
    for row in retval:
      prct_rend_mes, prct_rend_desdeano, prct_rend_12meses, refmonth, nomefundo = row[0], row[1], row[2], row[3], row[4]
      triple_result__dict = {
        'prct_rend_mes': prct_rend_mes,
         'prct_rend_desdeano': prct_rend_desdeano,
         'prct_rend_12meses': prct_rend_12meses,
         'refmonth': refmonth,
         'nomefundo': nomefundo,
      }
      self.fundo_results_dictlist.append(triple_result__dict)

  def show_results1(self):
    for fresultdict in self.fundo_results_dictlist:
      print(fresultdict['nomefundo'], '| refmonth', fresultdict['refmonth'])
      print('\t no mês', fresultdict['prct_rend_mes'])
      print('\t no ano', fresultdict['prct_rend_desdeano'])
      print('\t nos últs 12m', fresultdict['prct_rend_12meses'])
      print()

  def process(self):
    """
    fundo_results_dictlist = get_fundo_results_dictlist_within_daterange(monthref_ini, monthref_fim)
    transpose_to_triplerend_dict = transpose_dict(fundo_results_dictlist)
    show_results2(transpose_to_triplerend_dict)
    """
    pass


def get_daterange_args_as_dict():
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
  daterange_dict = get_daterange_args_as_dict()
  monthref_ini = daterange_dict['monthref_ini']
  monthref_fim = daterange_dict['monthref_fim']
  triple = TripleRend(monthref_ini, monthref_fim)
  triple.process()


if __name__ == '__main__':
  process()
  # test_some_yyyydashmm_dates()
