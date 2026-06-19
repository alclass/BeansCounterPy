#!/usr/bin/env python3
"""
art/books/packt/knowledgeArea.py
import re
from xxlimited_35 import Null
from art.books.packt import PACKT_URL_TO_INTERPOL
"""
from dataclasses import dataclass, asdict
import art.books.packt.models.wordTranslateDict as wTD  # wtd.transdict
transdict = wTD.transdict


def cleanup(word):
  if word is None or word == '':
    return ''
  try:
    if word.endswith(' Bks'):
      word = word[:-4]
    # evens = [0 if x % 2 == 0 else -1 for x in numbers]
    if word in transdict.keys():
      word = transdict[word]
    return word
  except (AttributeError, IndexError):
    pass
  return ''


def recompose(pieces):
  words = []
  for pp in pieces:
    pp = cleanup(pp)
    words.append(pp)
  if words[0] == '':
    del words[0]
  ka_name = ' | '.join(words)
  return ka_name


@dataclass
class KnowledgeArea:
  """

  _id: str
  """
  relpath: str | None = None
  packts_midurl_ka: str | None = None

  @classmethod
  def create_root_ka(cls):
    root = cls()
    root.relpath = '/'
    return root

  def is_root(self):
    bool_val = False
    try:
      bool_val = self.relpath == '/'
    except (AttributeError, TypeError):
      pass
    return bool_val

  @property
  def parent(self):
    if self.relpath == '/':
      return None
    try:
      pp = self.relpath.split('/')
      less_one_pp = pp[0:-1]
      parents_relpath = '/'.join(less_one_pp)
      _parent = KnowledgeArea()
      _parent.relpath = parents_relpath
      return _parent
    except (AttributeError, IndexError):
      pass
    return None

  def ka_name(self):
    """
    self.relpath.replace('/', '|')
    """
    if self.relpath is None or self.relpath == '/':
      return 'Todas as Áreas'
    pieces = self.relpath.split('/')
    _relpath = recompose(pieces)
    return _relpath

  def __eq__(self, other):
    try:
      return self.relpath == other.relpath
    except AttributeError:
      pass
    return False

  def __len__(self):
    """

    """
    if self.is_root():
      return 0
    pp = []
    try:
      size = len(self.relpath.split('/'))
      return  size
    except (AttributeError, IndexError):
      pass
    return 0

  def __str__(self):
    outstr = f"""{self.__class__.__name__}
      knowledge area = {self.ka_name()}
      depth = {len(self)} 
    """
    return outstr


def adhoc_test2():
  """
  lista = [i for i in range(10) if i % 2 == 0 else -1]
  print(lista)

  """
  numbers = list(range(10))
  evens = [0 if x % 2 == 0 else -1 for x in numbers ]
  print(evens)


def adhoc_test1():
  """

  ka = KnowledgeArea('/Cmp Sci Bks/Cmp Lng Bks/Y Python Bks')

  """
  ka = KnowledgeArea('/')
  root = ka.create_root_ka()
  print(root)
  ka = KnowledgeArea('/Comp Sci Bks/Cmp Lng Bks/Y Python Bks')
  print(ka)
  parent = ka.parent
  print('parent', parent)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  adhoc_test2()
  """
  adhoc_test1()
