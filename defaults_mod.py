#!/usr/bin/env python3
"""
"""
import os.path


class Default:

  sqlitefilename = '.finance_beans_counter.sqlite'
  bankbasefolder_abspath = \
    '/home/dados/OurDocs/Banks OurDocs/'
  bb_folder_abspath = bankbasefolder_abspath + \
    'Caixa CEF OurDocs/Invests (Fundos etc) CEF OurDocs/' \
    'Fundos de Investimento CEF/Extratos Mensais Ano a Ano FIC CEF OurDocs/' \
    '2021 Extratos Mensais FIC CEF OurDocs'
  cef_folder_abspath = bankbasefolder_abspath + \
    'Caixa CEF OurDocs/Invests (Fundos etc) CEF OurDocs/' \
    'Fundos de Investimento CEF/Extratos Mensais Ano a Ano FIC CEF OurDocs/' \
    '2021 Extratos Mensais FIC CEF OurDocs'
  bb_csvfilename = 'WS 2021 Extratos Mensais BB OurDocs.csv'
  cef_csvfilename = 'WS 2021 Extratos Mensais FIC CEF OurDocs.csv'

  @classmethod
  def get_beans_counter_sqlitefile_abspath(cls):
    return os.path.join(cls.bankbasefolder_abspath, cls.sqlitefilename)

  @classmethod
  def get_bb_csvfile_abspath(cls):
    return os.path.join(cls.bb_folder_abspath, cls.bb_csvfilename)

  @classmethod
  def get_cef_csvfile_abspath(cls):
    return os.path.join(cls.cef_folder_abspath, cls.cef_csvfilename)
