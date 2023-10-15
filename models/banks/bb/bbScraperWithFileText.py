#!/usr/bin/env python3
""""
bbScraperWithFileText.py

saldo anterior & cotas
  regexp => dd/dd/yyyy SALDO ANTERIOR
  restr = "(\d{2}/\d{2}/\d{4}).SALDO.ANTERIOR.+"
saldo atual & cotas
  regexp => dd/dd/yyyy SALDO ATUAL

"""
import copy
import datetime
import os.path
import re
import fs.datesetc.datefs as dtfs
from fs.numbers.transform_numbers import transform_european_stringnumber_to_pythonfloat
from fs.texts.texts_scrapehelper import get_name_n_cnpj_from_fundotext
import fs.texts.exampleFundofileNTContent as exMod
import fs.db.dbasfolder.lookup_monthrange_convention_from_basedatafolder_on as lkup
import models.banks.fundoAplic as fAplic
import models.banks.banksgeneral as bkge
SALDOANT_RESTR = r"(\d{2}/\d{2}/\d{4}).(SALDO.ANTERIOR)(.+)"
SALDOATU_RESTR = r"(\d{2}/\d{2}/\d{4}).(SALDO.ATUAL)(.+)"
# SALDOANT_RESTR = "(\d{2}/\d{2}/\d{4}).SALDO.ANTERIOR.+(\d+(?:[\.\,]\d{2})?)"  # ([\d]) \.\,]+)"  # \b+(\d+|\.|\,)"
afterline_for_saldo_n_cota_restr = r"(\b\d{1,3}(?:\.\d{3})*(?:,\d+)?\b)"  # this picks up the valor and qtdcotas
afterline_for_saldo_n_cota_recomp = re.compile(afterline_for_saldo_n_cota_restr)
saldoant_recomp = re.compile(SALDOANT_RESTR)
saldoatu_recomp = re.compile(SALDOATU_RESTR)
DEFAULT_DATADIR = ("/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/FI Extratos Mensais Ano a Ano BB OD/2023 FI "
                   "Extratos Mensais BB")
DEFAULT_FILENAME = 'fundo_report_example.txt'
example_filepath = os.path.join(DEFAULT_DATADIR, DEFAULT_FILENAME)


class BBExtractScraperWithFileText(fAplic.FundoAplic):

  def __init__(self, scrapetext=None, refmonthdate=None):
    self.refmonthdate = refmonthdate
    self._scrapetext = scrapetext
    super().__init__()  # notice that FunooAplic's constructor instanced an "empty" object
    self.adjust_scrapetext()
    self.process()

  @property
  def scrapetext(self):
    return self._scrapetext

  def adjust_scrapetext(self):
    """

    """
    example = exMod.ExampleFundoFile()
    if self.scrapetext is None:
      self._scrapetext = example.read_n_return_example_fundofile_text()

  def find_name_n_cnpj(self):
    self.name, self.cnpj = get_name_n_cnpj_from_fundotext(self.scrapetext)

  def find_saldo_ant_n_cotas(self):
    findall = saldoant_recomp.findall(self.scrapetext)
    if findall:
      # findall is expected to be a list with one tuple that itself has the sought-for items
      ptuple = findall[0]
      self.data_saldo_ant = ptuple[0]  # date as string
      nextstr_to_extract_for_values = ptuple[-1]  # on this will be applied the next re.findall()
      nextfindall = afterline_for_saldo_n_cota_recomp.findall(nextstr_to_extract_for_values)
      if nextfindall:
        # nextfindall is expected to be a list with two strnumbers (notice its difference from above findall)
        strnumber = nextfindall[0]
        self.saldo_anterior = transform_european_stringnumber_to_pythonfloat(strnumber)
        strnumber = nextfindall[-1]
        self.qtd_cotas_ant = transform_european_stringnumber_to_pythonfloat(strnumber)

  def find_saldo_atu_n_cotas(self):
    """
    At this version, this method find_saldo_atu_n_cotas() is similar to find_saldo_ant_n_cotas()
      ie, no polymorphism was attempted as yet
    """
    findall = saldoatu_recomp.findall(self.scrapetext)
    if findall:
      # findall is expected to be a list with one tuple that itself has the sought-for items
      ptuple = findall[0]
      self.data_saldo_atu = ptuple[0]  # date as string
      nextstr_to_extract_for_values = ptuple[-1]  # on this will be applied the next re.findall()
      nextfindall = afterline_for_saldo_n_cota_recomp.findall(nextstr_to_extract_for_values)
      if nextfindall:
        # nextfindall is expected to be a list with two strnumbers (notice its difference from above findall)
        strnumber = nextfindall[0]
        self.saldo_atual = transform_european_stringnumber_to_pythonfloat(strnumber)
        strnumber = nextfindall[-1]
        self.qtd_cotas_atu = transform_european_stringnumber_to_pythonfloat(strnumber)

  def find_mes_ano_ults12meses(self):
    """
    # repstr = r"DADOS.RENDIMENTOS(.+\n)+[ltimos 12 meses\:]"
    mes = "mês".encode('latin1')
    repstr = r"No." + mes + r"\:.+"
    recomp = re.compile(repstr)

    """
    # self.find_nomes_without_regexp()
    # % no mês
    repstr = r"No mÃªs\:.+"  # notice that mÃªs is the way mês[latin1-in-file] is printed as a UTF-8 Python string
    recomp = re.compile(repstr)
    findall = recomp.findall(self.scrapetext)
    if findall:
      line = findall[0]
      nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
      if nexfindall:
        strnumber = nexfindall[-1]
        self.prct_rend_mes = transform_european_stringnumber_to_pythonfloat(strnumber)
    else:  # "fallback" try UTF-8 instead of latin1
      repstr = r"No mês\:.+"  # notice that mÃªs is the way mês[latin1-in-file] is printed as a UTF-8 Python string
      recomp = re.compile(repstr)
      findall = recomp.findall(self.scrapetext)
      if findall:
        line = findall[0]
        nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
        if nexfindall:
          strnumber = nexfindall[-1]
          self.prct_rend_mes = transform_european_stringnumber_to_pythonfloat(strnumber)
    # % no ano (desdeano)
    repstr = r"No ano\:.+"
    recomp = re.compile(repstr)
    findall = recomp.findall(self.scrapetext)
    if findall:
      line = findall[0]
      nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
      if nexfindall:
        strnumber = nexfindall[-1]
        self.prct_rend_desdeano = transform_european_stringnumber_to_pythonfloat(strnumber)
    # % últimos 12 meses
    repstr = r"ltimos 12 meses\:.+"
    recomp = re.compile(repstr)
    findall = recomp.findall(self.scrapetext)
    if findall is None or len(findall) == 0:
      return
    line = findall[0]
    nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
    if nexfindall:
      strnumber = nexfindall[-1]
      self.prct_rend_12meses = transform_european_stringnumber_to_pythonfloat(strnumber)

  def find_apli_resg_brut_ir_iof_n_liq(self):
    """
    # R$ aplicações
    # R$ resgates
    # R$ rendimento bruto
    # R$ imposto de renda

    """
    # self.find_nomes_without_regexp()
    # R$ aplicações
    repstr = r"APLICAÃÃES.+\(\+\).+"
    recomp = re.compile(repstr)
    findall = recomp.findall(self.scrapetext)
    if findall:
      line = findall[0]
      nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
      if nexfindall:
        strnumber = nexfindall[-1]
        self.aplicacoes = transform_european_stringnumber_to_pythonfloat(strnumber)
    else:  # "fallback" try UTF-8 instead of latin1
      repstr = r"APLICAÇÕES.+\(\+\).+"
      recomp = re.compile(repstr)
      findall = recomp.findall(self.scrapetext)
      if findall:
        line = findall[0]
        nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
        if nexfindall:
          strnumber = nexfindall[-1]
          self.aplicacoes = transform_european_stringnumber_to_pythonfloat(strnumber)
    # R$ resgates
    repstr = r"RESGATES.+\(\-\).+"
    recomp = re.compile(repstr)
    findall = recomp.findall(self.scrapetext)
    if findall:
      line = findall[0]
      nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
      if nexfindall:
        strnumber = nexfindall[-1]
        self.resgates = transform_european_stringnumber_to_pythonfloat(strnumber)
    # R$ rendimento bruto
    repstr = r"RENDIMENTO BRUTO.+\(\+\).+"
    recomp = re.compile(repstr)
    findall = recomp.findall(self.scrapetext)
    if findall:
      line = findall[0]
      nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
      if nexfindall:
        strnumber = nexfindall[-1]
        self.rendimento_bruto = transform_european_stringnumber_to_pythonfloat(strnumber)
    # R$ IR imposto de renda
    repstr = r"IMPOSTO DE RENDA.+\(\-\).+"
    recomp = re.compile(repstr)
    findall = recomp.findall(self.scrapetext)
    if findall:
      line = findall[0]
      nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
      if nexfindall:
        strnumber = nexfindall[-1]
        self.ir = transform_european_stringnumber_to_pythonfloat(strnumber)
    # R$ IOF imposto sobre operações financeiras
    repstr = r"IOF.+\(\-\).+"
    recomp = re.compile(repstr)
    findall = recomp.findall(self.scrapetext)
    if findall:
      line = findall[0]
      nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
      if nexfindall:
        strnumber = nexfindall[-1]
        self.iof = transform_european_stringnumber_to_pythonfloat(strnumber)
    # R$ rendimento líquido
    repstr = r"RENDIMENTO LÃQUIDO.+"
    recomp = re.compile(repstr)
    findall = recomp.findall(self.scrapetext)
    if findall:
      line = findall[0]
      nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
      if nexfindall:
        strnumber = nexfindall[-1]
        self.rendimento_liq = transform_european_stringnumber_to_pythonfloat(strnumber)
    else:  # "fallback" try UTF-8 instead of latin1
      repstr = r"RENDIMENTO LÍQUIDO.+"
      recomp = re.compile(repstr)
      findall = recomp.findall(self.scrapetext)
    if findall:
      line = findall[0]
      nexfindall = afterline_for_saldo_n_cota_recomp.findall(line)
      if nexfindall:
        strnumber = nexfindall[-1]
        self.rendimento_liq = transform_european_stringnumber_to_pythonfloat(strnumber)

  def transform_refmonth_to_date_if_needed(self):
    if type(self.refmonthdate) == datetime.date:
      return
    self.refmonthdate = dtfs.transform_strdate_to_date(self.refmonthdate)  # notice it may be None from here

  def deduce_refmonth_if_not_set(self):
    if self.refmonthdate is not None:
      return self.transform_refmonth_to_date_if_needed()
    # check it once again
    if self.refmonthdate is not None:
      return
    # so refmonthdate is None
    # dateini = self.data_saldo_ant
    refmonthdate = copy.copy(self.data_saldo_atu)
    refmonthdate = dtfs.transform_strdate_to_date(refmonthdate)
    try:
      year = refmonthdate.year
      month = refmonthdate.month
      self.refmonthdate = datetime.date(year=year, month=month, day=1)
    except AttributeError:
      pass

  def do_triple_rends_exist(self):
    if self.prct_rend_mes > 0 and self.prct_rend_mes > 0 and self.prct_rend_12meses > 0:
      return True
    return False

  def treat_the_3_dates(self):
    self.data_saldo_ant = dtfs.transform_strdate_to_date(self.data_saldo_ant)
    self.data_saldo_atu = dtfs.transform_strdate_to_date(self.data_saldo_atu)
    self.deduce_refmonth_if_not_set()

  def process(self):
    self.find_name_n_cnpj()
    self.find_saldo_ant_n_cotas()
    self.find_saldo_atu_n_cotas()
    self.find_mes_ano_ults12meses()
    self.find_apli_resg_brut_ir_iof_n_liq()
    self.treat_the_3_dates()

  def __str__(self):
    outstr = super().__str__()
    outstr = "<WithinFundoExtractScraper refmonthdate= %(refmonthdate)s>\n" + outstr
    return outstr


def adhoctest():
  bank3letter = 'bdb'
  fibasefolderpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(bank3letter)
  finder = lkup.DatePrefixedOSEntriesFinder(fibasefolderpath)
  scrapetext = open(finder.greater_yearmonth_filepath, encoding='latin1').read()
  scraper = BBExtractScraperWithFileText(scrapetext, finder.refmonthdate_fim)
  print('-'*20, 'Fundo')
  print(scraper)


def process():
  """
  withinfundo_scraper = SpecificCEFExtractScraper()
  withinfundo_scraper.process()
  print(withinfundo_scraper)
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
