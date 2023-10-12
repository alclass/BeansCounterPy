#!/usr/bin/env python3
"""
xmliterposDataDictForCefFundos.py
  This class keeps the line-position-indexing observed when scraping CEF's xml monthly report files.
  For the time being, only two pos-sets are known, ie: 'especial' & 'expertise' (standing for their longer names).

  Levels: LINENUMBERDICT_S1 & LINENUMBERDICT_S2
    LINENUMBERDICT_S1 is observed when scraping node 'LTTextLineHorizontal'
    LINENUMBERDICT_S2 is observed when scraping node 'LTTextBoxHorizontal'
      (@see in source code the xml scraping method findall(param)) where param tells the xml node path

  There's probably a better way or strategy this xml parsing/scraping,
     but for the time being the direct nodepath approach above has been used and
     this (a bit weirdly) brought this scheme with levels and index-positioning.
  It's hoped one day soon to substitute this approach for a better one.
"""
from operator import itemgetter


class CefFIsPosIndexMapper:
  """

  """
  ESPECIAL = 'ESPECIAL'
  EXPERTISE = 'EXPERTISE'
  FUNDOKEYS = ['ESPECIAL', 'EXPERTISE']
  XML_LEVEL_ATTR_NAMES = ['0_LTTextLineHorizontal', '1_LTTextBoxHorizontal']
  FUNDOXMLITERPOSDICT = {
    'ESPECIAL': {
      'name': (4, 0),  # the second element is index for XML_LEVEL_ATTR_NAMES
      'prct_rend_mes': (10, 0),
      'prct_rend_desdeano': (12, 0),
      'prct_rend_12meses': (14, 0),
      'data_saldo_ant': (15, 0),
      'valor_cota_ant': (16, 0),
      'data_saldo_atu': (17, 0),  # 'data_saldo_atu': (11, 1),
      'valor_cota_atu': (18, 0),
      'cnpj': (24, 0),
      'aplicacoes': (39, 0),
      'resgates': (40, 0),
      'ir': (41, 0),
      'iof': (31, 0),
      'saldo_anterior': (28, 1),
      'rendimento_bruto': (29, 1),
      'saldo_bruto': (30, 1),
      'qtd_cotas_ant': (32, 1),
    },
    'EXPERTISE': {
      'name': (8, 0),
      'prct_rend_mes': (10, 0),
      'prct_rend_desdeano': (12, 0),
      'prct_rend_12meses': (14, 0),
      'data_saldo_ant': (15, 0),
      'valor_cota_ant': (16, 0),
      'data_saldo_atu': (17, 0),  # 'data_saldo_atu': (11, 1),
      'valor_cota_atu': (18, 0),
      'cnpj': (24, 0),
      'aplicacoes': (39, 0),
      'resgates': (40, 0),
      'ir': (41, 0),
      'iof': (42, 0),
      'saldo_anterior': (28, 1),
      'rendimento_bruto': (29, 1),
      'saldo_bruto': (30, 1),
      'qtd_cotas_ant': (32, 1),
    },
  }

  @classmethod
  def get_fundodict_with_fundokey(cls, fundokey):
    try:
      return cls.FUNDOXMLITERPOSDICT[fundokey]
    except IndexError:
      pass
    return None

  @classmethod
  def get_fundodict_with_fundokeyidx(cls, fundokeyidx):
    fundokey = cls.FUNDOKEYS[fundokeyidx]
    return cls.get_fundodict_with_fundokey(fundokey)

  @classmethod
  def derive_fundodict_into_triplelist_ordered_by_level_n_pos(cls, fundokey):
    """
    The xml parsing in this system, goes level and pos, that explains the ordering in here
    Eg result
    [('name', 0, 4), ('prct_rend_mes', 0, 10), ('prct_rend_desdeano', 0, 12), ... ]
    """
    specfundodict = cls.get_fundodict_with_fundokey(fundokey)
    if specfundodict is None:
      return None, None
    triplelist = []
    for fieldname in specfundodict:
      pos, ilevel = specfundodict[fieldname]
      triple = (fieldname, ilevel, pos)
      triplelist.append(triple)
    if len(triplelist) == 0:
      return
    triplelist = sorted(triplelist, key=itemgetter(1, 2))
    # triplelist = sorted(triplelist, key=itemgetter(1))
    return triplelist

  @classmethod
  def get_xmliterpos_n_leveln_with_fieldname_n_fundo(cls, fieldname, fundokey):
    """

    """
    specfundodict = cls.get_fundodict_with_fundokey(fundokey)
    if specfundodict is None:
      return None, None
    try:
      pos_level_tuple = specfundodict[fieldname]
      pos, ilevel = pos_level_tuple
      return pos, ilevel
    except IndexError:
      pass
      return None, None

  @classmethod
  def mount_2dlist_ordering_fundotriple_by_level_n_pos(cls, fundokey):
    """
    Eg
    Suppose fundotriple is [('name', 0, 4), ('prct_rend_mes', 0, 10), ('prct_rend_desdeano', 0, 12), ...]
      Reorganizing, one gets:
        poslist for level 0 [4, 10, 12, 14, 15, 16, 17, 18, 24, 31, 39, 40, 41]
        poslist for level 1 [28, 29, 30, 32]
    The return outcome will then be [[4, 10, 12, 14, 15, 16, 17, 18, 24, 31, 39, 40, 41], [28, 29, 30, 32]]
    Notice that fieldname, if needed, must be recuperated back from triple,
      for a level and a pos maps back to a fieldname.
    """
    triple = cls.derive_fundodict_into_triplelist_ordered_by_level_n_pos(fundokey)
    levels = set([elem[1] for elem in triple])  # levels (as of today 2023-10) is [0, 1] meaning spec xmlnodepaths
    levelwithposlist = []
    for elevel in levels:
      tripleforlevel = filter(lambda e: e[1] == elevel, triple)
      poslist = [elem[2] for elem in tripleforlevel]
      print('poslist', poslist)
      levelwithposlist.append(poslist)
    return levelwithposlist

  @classmethod
  def recup_fieldname_name_from_triple_fundo_level_n_pos(cls, fundokey, elevel, pos):
    """
    Eg of derive_fundodict_into...'s return:
    [('name', 0, 4), ('prct_rend_mes', 0, 10), ('prct_rend_desdeano', 0, 12), ... ]
    """
    triple = cls.derive_fundodict_into_triplelist_ordered_by_level_n_pos(fundokey)
    triple_at_elevel = filter(lambda e: e[1] == elevel, triple)
    triple_at_elevel_pos = list(filter(lambda e: e[2] == pos, triple_at_elevel))
    firsttriple = triple_at_elevel_pos[0]
    fieldname = firsttriple[0]
    return fieldname


def adhoctest():
  fundokey = 'ESPECIAL'
  scrmsg = 'CefFIsPosIndexMapper.get_fundodict_with_fundokey(fundokey=%s)' % fundokey
  print(scrmsg)
  r = CefFIsPosIndexMapper.get_fundodict_with_fundokey(fundokey)
  print(r)
  fieldname = 'rendimento_bruto'
  scrmsg = ('CefFIsPosIndexMapper.get_xmliterpos_n_leveln_with_fieldname_n_fundo('
            'fieldname=%s, fundokey=%s)') % (fieldname, fundokey)
  print(scrmsg)
  r = CefFIsPosIndexMapper.get_xmliterpos_n_leveln_with_fieldname_n_fundo(fieldname, fundokey)
  print(r)
  scrmsg = 'CefFIsPosIndexMapper.derive_fundodict_into_triplelist_ordered_by_level_n_pos(fundokey=%s)' % fundokey
  print(scrmsg)
  res = CefFIsPosIndexMapper.derive_fundodict_into_triplelist_ordered_by_level_n_pos(fundokey)
  print(res)
  scrmsg = 'CefFIsPosIndexMapper.mount_2dlist_ordering_fundotriple_by_level_n_pos(fundokey=%s)' % fundokey
  print(scrmsg)
  res = CefFIsPosIndexMapper.mount_2dlist_ordering_fundotriple_by_level_n_pos(fundokey)
  print(res)
  res = CefFIsPosIndexMapper.getback_fieldname_name_from_triple_fundo_level_n_pos(fundokey, 0, 15)
  print(res)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
