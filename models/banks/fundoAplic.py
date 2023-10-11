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
    """
    UNIQUE(bank3letter, name, refmonthdate)
    """
    self.bank3letter = None
    self.name = None
    self.refmonthdate = None
    self.cnpj = None
    self.data_saldo_ant = None
    self.saldo_anterior = None
    self.qtd_cotas_ant = None
    self.valor_cota_ant = None
    self.data_saldo_atu = None
    self.saldo_atual = None
    self.qtd_cotas_atu = None
    self.valor_cota_atu = None
    self.prct_rend_mes = None
    self.prct_rend_desdeano = None
    self.prct_rend_12meses = None
    self.ir = None
    self.iof = None
    self.aplicacoes = None
    self.resgates = None
    self.resg_bru_em_trans = None  # on CEF
    self.rendimento_bruto = None  # on CEF
    self.rendimento_liq = None
    self.rendimento_base = None  # on CEF
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

  def load_from_dict(self, pdict):
    for fieldname in self.attrs():
      try:
        _ = pdict  # just for the IDE because pdict is used inside the exec() below
        pyline = 'self.' + fieldname + ' = pdict["' + fieldname + '"]'
        exec(pyline)
      except IndexError:
        pass

  def transpose_from(self, other):
    for fieldname in self.attrs():
      _ = other  # for the IDE to consider use of parameter, which is 'dynamically' used inside the exec() below
      exec('self.' + fieldname + ' = other.' + fieldname)

  def transpose_to(self, other):
    for fieldname in self.attrs():
      _ = other  # for the IDE to consider use of parameter, which is 'dynamically' used inside the exec() below
      exec('other.' + fieldname + ' = self.' + fieldname)

  def outdict(self):
    if self._outdict is None:
      self._outdict = {}
      for fieldname in self.attrs():
        value = eval('self.' + fieldname)
        self._outdict[fieldname] = value
    return self._outdict

  def __str__(self):
    outstr = '<fundo_result refmonth="{refmonthdate}">\n'.format(refmonthdate=self.refmonthdate)
    for fieldname in self.attrs():
      value = eval('self.' + fieldname)
      outstr += f"\t{fieldname} = {value}\n".format(fieldname=fieldname, value=value)
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
