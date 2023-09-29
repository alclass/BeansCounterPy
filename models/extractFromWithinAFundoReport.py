#!/usr/bin/env python3
""""
extractFromWithinAFundoReport.py

saldo anterior & cotas
  regexp => dd/dd/yyyy SALDO ANTERIOR
  restr = "(\d{2}/\d{2}/\d{4}).SALDO.ANTERIOR.+"
saldo atual & cotas
  regexp => dd/dd/yyyy SALDO ATUAL

"""
import os.path
import re
from fs.numbers.transform_numbers import transform_european_stringnumber_to_pythonfloat
from fs.texts.texts_scrapehelper import get_name_n_cnpj_from_fundotext
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


class WithinFundoExtractScraper:

  def __init__(self, scrapetext=None, refmonthdate=None):
    self.scrapetext = scrapetext
    self.refmonthdate = refmonthdate
    self.lines = []
    self.name = 'no-name'
    self.cnpj = 'no-cnpj'
    self.data_saldo_ant = 'dd/mm/aaaa'
    self.saldo_anterior = -1
    self.qtd_cotas_anterior = -1
    self.data_saldo_atu = 'dd/mm/aaaa'
    self.saldo_atual = -1
    self.qtd_cotas_atual = -1
    self.prct_rend_mes = -1
    self.prct_rend_desdeano = -1
    self.prct_rend_12meses = -1
    self.aplicacoes = -1
    self.resgates = -1
    self.rend_bruto = -1
    self.ir = -1
    self.iof = -1
    self.rend_liq = -1
    self.adjust_scrapetext()

  def adjust_scrapetext(self):
    """

    """
    if self.scrapetext is None:
      self.scrapetext = open(example_filepath, encoding='latin1').read()

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
        self.qtd_cotas_anterior = transform_european_stringnumber_to_pythonfloat(strnumber)

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
        self.qtd_cotas_atual = transform_european_stringnumber_to_pythonfloat(strnumber)

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
        self.rend_bruto = transform_european_stringnumber_to_pythonfloat(strnumber)
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
        self.rend_liq = transform_european_stringnumber_to_pythonfloat(strnumber)

  def process(self):
    self.find_name_n_cnpj()
    self.find_saldo_atu_n_cotas()
    self.find_saldo_atu_n_cotas()
    self.find_mes_ano_ults12meses()
    self.find_apli_resg_brut_ir_iof_n_liq()

  def outdict(self):
    return {
      'name': self.name,
      'cnpj': self.cnpj,
      'data_saldo_ant': self.data_saldo_ant,
      'saldo_anterior': self.saldo_anterior,
      'qtd_cotas_anterior': self.qtd_cotas_anterior,
      'data_saldo_atu': self.data_saldo_atu,
      'saldo_atual': self.saldo_atual,
      'qtd_cotas_atual': self.qtd_cotas_atual,
      'prct_rend_mes': self.prct_rend_mes,
      'prct_rend_desdeano': self.prct_rend_desdeano,
      'prct_rend_12meses': self.prct_rend_12meses,
      'aplicacoes': self.aplicacoes,
      'resgates': self.resgates,
      'rend_bruto': self.rend_bruto,
      'ir': self.ir,
      'iof': self.iof,
      'rend_liq': self.rend_liq,
    }

  def __str__(self):
    outstr = """
      name               = %(name)s
      cnpj               = %(cnpj)s
      saldo_anterior     = %(saldo_anterior)f
      data_saldo_ant     = %(data_saldo_ant)s
      saldo_anterior     = %(saldo_anterior)f
      qtd_cotas_anterior = %(qtd_cotas_anterior)f
      data_saldo_atu     = %(data_saldo_atu)s
      saldo_atual        = %(saldo_atual)f
      qtd_cotas_atual    = %(qtd_cotas_atual)f
      prct_rend_mes      = %(prct_rend_mes)f
      prct_rend_desdeano = %(prct_rend_desdeano)f
      prct_rend_12meses  = %(prct_rend_12meses)f 
      aplicacoes         = %(aplicacoes)f
      resgates           = %(resgates)f
      rend_bruto         = %(rend_bruto)f
      ir                 = %(ir)f
      iof                = %(iof)f
      rend_liq           = %(rend_liq)f
      """ % self.outdict()
    return outstr


if __name__ == '__main__':
  withinfundo_scraper = WithinFundoExtractScraper()
  withinfundo_scraper.process()
  print(withinfundo_scraper)
