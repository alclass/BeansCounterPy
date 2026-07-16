#!/usr/bin/env python3
"""
art/bookroutes/packt/folders/listKnowlegeAreas.py

what is the best way to implement a graph-like data scheme,
  like, for example, knowledge areas, in mongodb?

"/home/dados/Books/epub Books"
"""
import art.bks.packt.models.knowledgeArea as KA
from pathlib import Path
import os
import sys
from art.bks.packt import FALLBACK_LOCAL_BOOKS_ROOTFOLDER


class DirWalker:

    def __init__(self, basefolder_ap=None):
      self.bookcounter = 0
      self.n_gen = 0
      self.current_bookinfo = None
      self.current_passing_dir = None
      self.current_dir_bookinfos = []  # a per-directory buffer for a later yield
      self.basefolder_ap = basefolder_ap or Path(os.path.abspath(os.path.curdir))
      self.treat_basefolder()
      # self.bi_non_isbn = 0

    def treat_basefolder(self):
      self.basefolder_ap = self.basefolder_ap or os.path.abspath(os.path.curdir)
      self.basefolder_ap = Path(self.basefolder_ap)

    @property
    def relpath(self):
      try:
        _relpath = self.current_passing_dir[len(str(self.basefolder_ap)):]
        _relpath = _relpath.lstrip('/')
        return _relpath
      except (IndexError, TypeError):
        pass
      return None

    @property
    def karea(self):
      ka = KA.KnowledgeArea()
      ka.relpath = self.relpath
      return ka

    def gen_bookinfolist_via_dirwalk(self):
      self.n_gen = 0
      for self.current_passing_dir, _, _ in os.walk(self.basefolder_ap):
        self.n_gen += 1
        # print(self.n_gen, 'current', self.current_passing_dir)
        print(self.n_gen, 'relpath', self.relpath)
        print('karea', self.karea)
        yield None


def get_args():
  rootfolder_ap = None
  if len(sys.argv) > 1:
    rootfolder_ap = sys.argv[1]
  return rootfolder_ap


def process():
  """
  grab_bookinfos_thru_dirs(rootfolder_ap)
  """
  rootfolder_ap = get_args() or FALLBACK_LOCAL_BOOKS_ROOTFOLDER
  print(rootfolder_ap)
  walker = DirWalker(rootfolder_ap)
  for i, bi in enumerate(walker.gen_bookinfolist_via_dirwalk()):
    seq = i + 1
    print(seq, bi)


if __name__ == '__main__':
  """
  adhoc_test1()
  process()
  """
  process()
