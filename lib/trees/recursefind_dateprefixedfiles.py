#!/usr/bin/env python3
"""
lib/db/trees/recursefind_dateprefixedfiles.py
  Searches the datafolder for ini and fim refmonths
import datetime
import lib.osfs.osfunctions as osfs
import lib.osfs.oshilofunctions as hilo
import lib.datesetc.refmonth_fs as rmfs
"""
from __future__ import annotations
import datetime
import os
from pathlib import PosixPath
from pathlib import Path
import lib.datesetc.datefs as dtfs

import settings as sett
DEFAULT_ROOTPATH = sett.get_apps_data_rootdir_abspath()


class FromRootFolderFinder:

  def __init__(self, nodepath: PosixPath, parent: FromRootFolderFinder | None = None) -> None:
    """
    """
    self.nodepath = Path(nodepath) or DEFAULT_ROOTPATH
    self.parent = parent  # root has parent = None
    self.fonodes = []
    self.finodes = []
    self.foldernames = []
    self.filenames = []
    self.bootstrap()

  def bootstrap(self):
    print('bootstrapping', self.entryname)
    self.discover_dirtree_onwards_if_folder()

  def followup_childfolders(self):
    thisclass = FromRootFolderFinder
    self.fonodes = []
    for foname in self.foldernames:
      aheadpath = self.nodepath / foname
      node = thisclass(aheadpath, self)
      self.fonodes.append(node)
      node.bootstrap()

  def collect_childfiles(self):
    thisclass = FromRootFolderFinder
    self.finodes = []
    for finame in self.filenames:
      aheadpath = self.nodepath / finame
      node = thisclass(aheadpath, self)
      self.finodes.append(node)

  def discover_dirtree_onwards_if_folder(self):
    """


    if self.is_file:
      print('is file', self.entryname)
      return
    """
    if self.nodepath.is_file():
      return
    entries = os.listdir(self.nodepath)
    allpaths = list(map(lambda e: self.nodepath / e, entries))
    folderpaths = filter(lambda e: os.path.isdir(e), allpaths)
    self.foldernames = list(map(lambda e: os.path.split(e)[1], folderpaths))
    filepaths = filter(lambda e: os.path.isfile(e), allpaths)
    self.filenames = list(map(lambda e: os.path.split(e)[1], filepaths))
    self.followup_childfolders()
    self.collect_childfiles()
    pass

  @property
  def entries(self):
    _entries = []
    _entries += self.fonodes
    _entries += self.finodes
    return _entries

  @property
  def is_file(self):
    return self.nodepath.is_file()

  @property
  def entryname(self):
    _, name = os.path.split(self.nodepath)
    return name

  @property
  def entrypath(self):
    ppath, _ = os.path.split(self.nodepath)
    return ppath

  @property
  def dateprefix(self) -> datetime.date | None:
    entryname = self.entryname
    try:
      space = entryname[10]
      if space != ' ':
        return None
      strdate = entryname[0:10]
      pdate = dtfs.make_date_or_none(strdate)
      if pdate is not None:
        return pdate
    except (IndexError, ValueError):
      pass
    return None

  @property
  def yearmonthprefix(self) -> str | None:
    if self.dateprefix is not None:
      year, month = self.dateprefix.year, self.dateprefix.month
      ymprefix = f"{year}-{month:02}"
      return ymprefix
    entryname = self.entryname
    try:
      space = entryname[7]
      if space != ' ':
        return None
      stryear = entryname[0:4]
      year = int(stryear)
      strmonth = entryname[0:4]
      month = int(strmonth)
      ymprefix = f"{year}-{month:02}"
      return ymprefix
    except (IndexError, ValueError):
      pass
    return None

  @property
  def yearprefix(self) -> str | None:
    """
    This should be considered a convention
    """
    if self.dateprefix is not None:
      year = self.dateprefix.year
      return str(year)
    if self.yearmonthprefix is not None:
      return self.yearmonthprefix[:4]
    entryname = self.entryname
    try:
      space = entryname[4]
      if space != ' ':
        return None
      stryear = entryname[0:4]
      _ = int(stryear)
      return stryear
    except (IndexError, ValueError):
      pass
    return None

  @property
  def as_text(self):
    """
    text = "[fonames]"
    for inode in self.fonodes:
      text += "\n\t" + str(inode)
    text += "[finames]"
    if len(self.filenames) == 0:
      text += "\n No files "
    else:
      for inode in self.filenames:
        text += "\n\t" + str(inode)
    return text
    """
    return ""

  def show_finames(self):
    print(self.finames)

  def show_fonames(self):
    print(self.fonames)

  def list_subtree(self):
    for fonode in self.fonodes:
      print(fonode)
      fonode.list_subtree()
    for finode in self.finodes:
      print(finode)
      finode.list_subtree()

  def __str__(self):
    """
    Attention:
      len(self.fonodes) was showing twice as len(self.foldernames)
      => look into it, because they should be the same
    {self.as_text}
    """
    if self.is_file:
      return 'isfile'
    parent = 'ROOT' if self.parent is None else self.parent.entryname
    nentries = len(self.entries)
    ostr = f"""{self.nodepath}
    entry = {self.entryname}
    parent = {parent}
    n_folders = {len(self.foldernames)} | n_files = {len(self.filenames)}
    n_fonodes = {len(self.fonodes)} | n_finodes = {len(self.finodes)}
    {self.yearprefix} | n_entries = {nentries}
    """
    return ostr


def find_by_year(year, node):
  found = []
  for in_node in node.entries:
    if str(year) == in_node.yearprefix:
      found.append(in_node)
    print('to find', year, in_node.yearprefix, found)
    return found + find_by_year(year, in_node)
  return found


def traverse_tree(node):
  print(node)
  for in_node in node.entries:
    return traverse_tree(in_node)
  return None


def adhoctest1():
  p_datafolder_abspath = sett.get_apps_data_rootdir_abspath()
  inipath = p_datafolder_abspath / 'bankdata/001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/BB FI Rendimentos Diários htmls'
  print('inipath', inipath)
  rootnode = FromRootFolderFinder(inipath)
  rootnode.list_subtree()
  traverse_tree(rootnode)
  foundlist = find_by_year('2024', rootnode)
  print('='*40)
  print('found', '='*40)
  print('='*40)
  for found in foundlist:
    print(found)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
