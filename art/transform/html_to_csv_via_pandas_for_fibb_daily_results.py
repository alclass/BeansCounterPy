#!/usr/bin/env python3
"""
art/download/fibb_daily_results_html_to_csv_via_pandas_transform.py
  transforms & converts one or more html data files into their csv equivalent ones.
The argparse has the following optional parameters:

args => Namespace(ini=[<initial_date>] fim=[<finish_date'], datelist=[<adatelist>]
  If no parameter is given, default is today's date.

Usage:
$thiscommand -i [<initial_date>] -f <finish_date'] -dl [<adatelist>]

Example:
$thiscommand -i '2023-10-10' -f '2023-10-27'
  The daterange above goes, day to day, from '2023-10-10' up to '2023-10-27' included.
  That is, tranform/convert will look up and process all files prefixed with these dates.
"""
import argparse
import datetime
import lib.datesetc.datehilofs as hilodt
import models.banks.bb.fi.fibb_daily_results_html_to_csv_via_pandas_transform as transf  # .WithPandasHtmlToCsvConverter


class ArgsDispatcher:
  """
  It calls WithPandasHtmlToCsvConverter(date) with all input dates, day-date by day-date each call.
    CLI arguments may be either a range, a list or None, the latter meaning "today".
  """

  def __init__(self, args):
    """
    args => Namespace(ini=None, fim=None, datelist=None)
    Namespace(ini=None, fim=None, datelist=None)
    """
    self.dateini = hilodt.make_date_or_none(args.ini)
    self.datefim = hilodt.make_date_or_none(args.fim)
    self.datelist = hilodt.return_datelist_or_empty_from_strlist(args.datelist)
    self.integrate_datelist_w_ini_fim_range()

  def integrate_datelist_w_ini_fim_range(self):
    outdate = []
    if len(self.datelist) > 0:
      outdate = len(self.datelist)
    if self.dateini:
      for pdate in hilodt.gen_date_range_ini_to_fim(self.dateini, self.datefim):
          outdate.append(pdate)
    self.datelist = sorted(list(set(outdate)))
    if len(self.datelist) == 0:
      # if empty, list defaults to containing (at least) today's date
      self.datelist = [datetime.date.today()]

  def dispatch(self):
    """
    For every day-date, one by one, that is integrated into self.datelist, dispatch calls:
      WithPandasHtmlToCsvConverter(pdate)
    The purpose is to convert all html data files in the conventioned folder into their respective csv's.
      TO-DO: the above class WithPandasHtmlToCsvConverter will, still "to do", better organizes the date folders.
    """
    for pdate in self.datelist:
      print('Dispatching for date', pdate)
      converter = transf.WithPandasHtmlToCsvConverter(pdate)
      converter.process()

  def process(self):
    """
    In the case here, process is a "sinomyn" with "dispatch", both can be called
    """
    self.dispatch()

  def outdict(self):
    _outdict = {
      'dateini': self.dateini,
      'datefim': self.datefim,
      'datelist': str(self.datelist),
    }
    return _outdict

  def __str__(self):
    outstr = ("""ArgsDispatcher: dateini="{dateini}", datefim="{datefim}", datelist = {datelist}"""
              .format(**self.outdict()))
    return outstr


def cli_args_fetcher():
  """
  https://realpython.com/command-line-interfaces-python-argparse/
  One Example:
    parser.add_argument("--veggies", nargs="+")
    parser.add_argument("--fruits", nargs="*")
      $ python cooking.py --veggies pepper tomato --fruits apple banana
    parser.add_argument("--size", choices=["S", "M", "L", "XL"], default="M")
    my_parser.add_argument("--weekday", type=int, choices=range(1, 8))

  parser.add_argument(
    '-cmc', '--calc-monet-corr', metavar='twodates', type=str, nargs=2,
    help="the ending date in date range for finding daily exchange rate quotes",)
  )

  """
  parser = argparse.ArgumentParser(description="Obtain Arguments")
  parser.add_argument(
    '-i', '--ini', metavar='date_ini', type=str, nargs='?',
    help="the beginning date in date range for finding daily exchange rate quotes",
  )
  parser.add_argument(
    '-f', '--fim', metavar='date_fim', type=str, nargs='?',
    help="the ending date in date range for finding daily exchange rate quotes",
  )
  parser.add_argument(
    '-dl', '--datelist', metavar='datelist', type=str, nargs='+',
    help="datelist for finding daily exchange rate quotes one by one",
  )
  args = parser.parse_args()
  print('args =>', args)
  return args


def process():
  """

  """
  args = cli_args_fetcher()
  print(args)
  argdispatcher = ArgsDispatcher(args)
  argdispatcher.process()
  print(argdispatcher)


def adhoctests():
  pass


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
