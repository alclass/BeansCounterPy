#!/usr/bin/env python3
"""
The context to be solved here is to extract data from xml that has been converted original from pdf.
The current stratety (a change may happen in the future) is to find the field positions via help of
  the following two xml node paths: LTTextLineHorizontal & LTTextBoxHorizontal

  A refpage for XML parsing in Python
  https://www.geeksforgeeks.org/xml-parsing-python/
"""
# import copy
# import fs.os.discover_levels_for_datafolders as fndr
# import fs.datesetc.datefs as dtfs
import os
import xml.etree.ElementTree as eT
import lib.os.oshilofunctions as hilo
import models.banks.banksgeneral as bkge
import models.banks.cef.xmliterposDataDictForCefFundos as itPos  # itpos.CefFIsPosIndexMapper
import models.banks.fundoAplic as fAplic  # fAplic.FundoAplic()


class CefFiXMLDataExtractor:
  """
  A CEF XML data file has only one fundo for one refmonthdate,
    whereas, for example, a BB data text file has one or more fundos in it.

  Notice that for more than one fundo for a refmonth, more than one xml files will be needed.
  """

  def __init__(self, xmlfilepath=None):
    """
    The purpose of this class is to scrape (or parse) the XML file related to a given fundo & refmonthdate,
      these latter two parameters are derived from the filename itself based on a convention.

    Notice __init__() here issues method parsexml() at its end,
      ie the object executes itself upon receiving xmlfilepath at construction time (__init__()).

    For the time being, the parsing strategy is to use xmltree.findall(nodepath)
      and observe nodes and their positions as they occur. This observation is done with the help of:
        => models/banks/cef/parseXmlCefFi.py
    Once these node positionings are taken, they are "hardcoded" in:
        => models/banks/cef/xmliterposDataDictForCefFundos.py

    The scheme is used by CEF which has pdf data files converted into xml.
      BB uses scraping directly from data text files.
    """
    self._outdict = None
    self.bank3letter = bkge.BANK.BANK3LETTER_CEF
    self.xmlpos_mapper = itPos.CefFIsPosIndexMapper
    self._xmlfilepath = xmlfilepath
    self._xmlfilename = None
    self._refmonthdate = None
    self.treat_xmlfilepath()
    self.fundo = None
    self.init_fundo()
    self.parsexml()

  def treat_xmlfilepath(self):
    if self._xmlfilepath is None or not os.path.isfile(self._xmlfilepath):
      error_msg = 'Error: xmlfilepath [%s] does not exist.' % self._xmlfilepath
      raise OSError(error_msg)

  def init_fundo(self):
    """
    should be called after self.treat_xmlfilepath(), because it needs filename for refmonthdate
    """
    self.fundo = fAplic.FundoAplic()  # instantiate an empty FunooAplic obj
    self.fundo.bank3letter = self.bank3letter
    self.fundo.refmonthdate = self.refmonthdate

  @property
  def xmlfilepath(self):
    return self._xmlfilepath

  @property
  def xmlfilename(self):
    if self.xmlfilepath is None:
      return None
    if self._xmlfilename is None:
      self._xmlfilename = os.path.split(self.xmlfilepath)[-1]
    return self._xmlfilename

  @property
  def refmonthdate(self):
    if self._refmonthdate is None:
      self._refmonthdate = hilo.derive_refmonthdate_from_a_yearmonthprefixedstr(self.xmlfilename)
    return self._refmonthdate

  def get_xmlnodelevel_as_idx(self):
    upperfilename = self.xmlfilename.upper()
    for i, fundokey in enumerate(self.xmlpos_mapper.FUNDOKEYS):
      if upperfilename.find(fundokey) > -1:
        elevel = i
        return elevel
    return None

  def get_fundokey_by_xmlfilename(self):
    """
    At this moment, there are two fundokeys, namely, 'ESPECIAL' & 'EXPERTISE',
     they are CONST in list xmlpos_mapper.FUNDOKEYS
    Notice also that, by convention, these 'tokens' should be present in the xml data filenames
    """
    idx = self.get_xmlnodelevel_as_idx()
    if idx is None:
      return None
    return self.xmlpos_mapper.FUNDOKEYS[idx]

  def parse_xmltree(self, xmltree):
    """

    """
    fundokey = self.get_fundokey_by_xmlfilename()
    list2d = self.xmlpos_mapper.mount_2dlist_ordering_fundotriple_by_level_n_pos(fundokey)
    # eg list2d = [[4, 10, 12, 14, 15, 16, 17, 18, 24, 31, 39, 40, 41], [28, 29, 30, 32]]
    xmlroot = xmltree.getroot()
    level0_nodepos = 0
    elevel = 0
    for item in xmlroot.findall('./LTPage/LTTextBoxHorizontal/LTTextLineHorizontal'):
      # area for level 0_LTTextLineHorizontal
      _ = item  # item will used in the exec() below; this line is for the IDE!
      level0_nodepos += 1
      if level0_nodepos in list2d[elevel]:
        print(fundokey, 'nodepos', level0_nodepos, 'level', elevel)
        fieldname = self.xmlpos_mapper.recup_fieldname_name_from_triple_fundo_level_n_pos(
          fundokey, elevel, level0_nodepos
        )
        pyline = 'self.fundo.' + fieldname + ' = item.text'
        exec(pyline)
    level1_nodepos = 0
    elevel = 1
    for item in xmlroot.findall('./LTPage/LTTextLineHorizontal/LTTextBoxHorizontal'):
      # area for level 1_LTTextBoxHorizontal
      _ = item  # item will used in the exec() below; this line is for the IDE!
      level1_nodepos += 1
      if level1_nodepos in list2d[elevel]:
        print(fundokey, 'nodepos', level1_nodepos, 'level', elevel)
        fieldname = self.xmlpos_mapper.recup_fieldname_name_from_triple_fundo_level_n_pos(
          fundokey, elevel, level1_nodepos
        )
        pyline = 'self.fundo.' + fieldname + ' = item.text'
        exec(pyline)

  def parsexml(self):
    xmltree = eT.parse(self.xmlfilepath)
    self.parse_xmltree(xmltree)

  def get_attrs(self):
    """
    Based on
    'https://stackoverflow.com/questions/8137456/'
      'get-class-and-object-attributes-of-class-without-methods-and-builtins'
    """
    outdict = {
      name: attr for name, attr in self.__dict__.items()
      if not name.startswith("__")
      and not callable(attr)
      and not type(attr) is staticmethod}
    return outdict

  def outdict(self):
    if self._outdict is None:
      self._outdict = {}
      for fieldname in self.get_attrs():
        # if fieldname == '_outdict':
        #  continue
        value = eval('self.' + fieldname)
        self._outdict[fieldname] = value
    return self._outdict

  def __str__(self):
    outstr = '<fundo_result refmonth="{refmonthdate}">\n'.format(refmonthdate=self.refmonthdate)
    for fieldname in self.get_attrs():
      value = eval('self.' + fieldname)
      outstr += f"\t{fieldname} = {value}\n".format(fieldname=fieldname, value=value)
    return outstr


def adhoctest():
  pass


def process():
  ppath = "/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/104 CEF bankdata/" \
     "FI Extratos Mensais Ano a Ano CEF OD/2023 FI extratos mensais CEF/" \
     "2023-09 Expertise RF Créd Priv 589048,38 Extrato Mensal CEF.xml"
  o = CefFiXMLDataExtractor(xmlfilepath=ppath)
  # o.parsexml()
  print(o)


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
