#!/usr/bin/env python3
"""
The context to be solved here is to extract data from xml that has been converted original from pdf

  A refpage for XML parsing in Python
  https://www.geeksforgeeks.org/xml-parsing-python/
"""
# import copy
import fs.datesetc.datefs as dtfs


class FundoAplic:

  def __init__(self):
    self.bank3letter = 'no name'
    self.refmonthdate = None
    self.name = 'no name'
    self.cnpj = 'no name'
    self.data_saldo_ant = None
    self.saldo_anterior = -1
    self.qtd_cotas_ant = -1
    self.valor_cota_ant = -1
    self.data_saldo_atu = None
    self.saldo_atual = -1
    self.qtd_cotas_atu = -1
    self.valor_cota_atu = -1
    self.prct_rend_mes = -1
    self.prct_rend_desdeano = -1
    self.prct_rend_12meses = -1
    self.ir = -1
    self.iof = -1
    self.aplicacoes = -0.001
    self.resgates = -0.001
    self.resg_bru_em_trans = -1  # on CEF
    self.rendimento_bruto = -0.001  # on CEF
    self.rendimento_liq = -0.001
    self.rendimento_base = -0.001  # on CEF
    self._outdict = None

  def sync_refmonthdate_if_needed(self):
    if self.refmonthdate is None:
      if self.data_saldo_atu is None:
        return
      else:
        pdate = dtfs.transform_strdate_to_date(self.data_saldo_atu)
        if pdate is None:
          error_msg = 'Error: data_fim_cota (%s) could not be transform into a formal date type.' % self.data_saldo_atu
          raise ValueError(error_msg)
        self.data_saldo_atu = pdate
        self.refmonthdate = dtfs.make_date_with_day1(pdate)

  @classmethod
  def attrs(cls):
    pdict = vars(__class__())
    _attrs = pdict.keys()
    _attrs = list(filter(lambda attr: not attr.startswith('_'), _attrs))
    return _attrs

  def outdict(self):
    if self._outdict is None:
      self._outdict = {}
      for fieldname in self.attrs():
        value = eval('self.' + fieldname)
        self._outdict[fieldname] = value
    return self._outdict

  @property
  def datadict(self):
    """
    Usage:
      one possible "outside" use of this method is to get data for a db-saving function
    """
    fields = self.attrs()
    outdict = {}
    for fieldname in fields:
      value = eval('self.' + fieldname)
      outdict[fieldname] = value
    return outdict

  @property
  def sql_fieldnames(self):
    """
    Usage:
      one possible "outside" use of this method is to get data for sqlite cursor.execute() second tuple parameter
      (same as tuplevalues below)
    """
    fields = self.attrs()
    _sql_fieldnames = '('
    for fieldname in fields:
      _sql_fieldnames += '"' + fieldname + '",'
    _sql_fieldnames = _sql_fieldnames[:-1] + ')'
    return _sql_fieldnames

  @property
  def tuplevalues(self):
    """
    Usage:
      one possible "outside" use of this method is to get data for sqlite cursor.execute() second tuple parameter
      (same as fieldnames above)
    """
    fields = self.attrs()
    outlist = []
    for fieldname in fields:
      value = eval('self.' + fieldname)
      outlist.append(value)
    return tuple(outlist)

  def __str__(self):
    outstr = """<fundo_result refmonth="{refmonthdate}">
  name              = {name}             
  cnpj              = {cnpj}            
  data_saldo_ant    = {data_saldo_ant}    
  saldo_anterior    = {saldo_anterior}
  qtd_cotas_ant     = {qtd_cotas_ant}    
  valor_cota_ant     = {valor_cota_ant}    
  data_saldo_atu    = {data_saldo_atu}   
  saldo_atual       = {saldo_atual}
  qtd_cotas_atu     = {qtd_cotas_atu}    
  valor_cota_atu     = {valor_cota_atu}    
  prct_rend_mes     = {prct_rend_mes}      
  prct_rend_desdeano = {prct_rend_desdeano}     
  prct_rend_12meses = {prct_rend_12meses}
  resg_bru_em_trans = {resg_bru_em_trans}
  rendimento_bruto  = {rendimento_bruto} 
  rendimento_base   = {rendimento_base}  
  ir                = {ir}
    """.format(**self.outdict())
    return outstr


def adhoctest():
  o = FundoAplic()
  print(o)
  print(o.attrs())
  print(FundoAplic.attrs())


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
