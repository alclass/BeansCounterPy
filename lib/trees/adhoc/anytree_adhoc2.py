#!/usr/bin/env python3
"""
lib/trees/adhoc/anytree_adhoc2.py

Obs:
   In this adhoc-test, we haven't been able to traverse the whole tree from rootnode.
   We don't know why. Though we received hints from some AI, we stil could not see
   attributes children or descendants being filled in from rootnode on.

   We'll leave it there for time the being. The options ahead are:
     1 ahdoc-test treelib, bigtree and directorytree
     2 try to write a custom local solution (it might even be a Sqlite one instead of a linked-node structure)
"""
from __future__ import annotations  # for allowing a self-reference to the class itself @see Entry class below
import datetime
import os
# from pathlib import PosixPath
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
from anytree import Node, RenderTree
from anytree.resolver import Resolver
from anytree.search import findall
# from anytree.search import find as atfind
from pathlib import Path
from pathlib import PosixPath
from dataclasses import dataclass, field
import lib.trees.adhoc as init
global_i = 0


@dataclass(slots=True)
class Entry(Node):
  """

    Obs:
      the __init__() approach is being avoided with @dataclass
    The observation below is to note the parameter signature for class Entry
       inheriting from Node and annotated as dataclass.
    Pass *args and **kwargs to the anytree.Node parent class
    def __init__(self, name, parent=None, children=None, *args, **kwargs):
        super().__init__(name, parent, children)
        # dataclass fields must be initialized if they don't have defaults
        # However, Python's generated __init__ is overridden here,
        # so we extract or handle dataclass fields if necessary, or use defaults.
  """

  fopath: Path
  name: str
  parent: Entry | None = None
  _dateprefix: datetime.date = None
  _refmonth: datetime.date | None = None
  _refmonthprefix: str = None
  _yearprefix: int = None
  children: list = field(default_factory=list)

  def __post_init__(self):
    # Initialize the underlying anytree Node logic
    Node.__init__(self, name=self.name, parent=self.parent, children=self.children)

  @property
  def entrypath(self) -> Path:
    _path = self.fopath / self.name
    return _path

  @property
  def dateprefix(self) -> datetime.date | None:
    if self._dateprefix is None:
      _ = self.has_dateprefix()
    return self._dateprefix

  @property
  def refmonth(self) -> datetime.date | None:
    if self._refmonth is None:
      _ = self.has_refmonthprefix()
    return self._refmonth

  @property
  def refmonthprefix(self) -> str | None:
    if self._refmonthprefix is None:
      _ = self.has_refmonthprefix()
      if self._refmonthprefix:
        self._refmonth = rmfs.make_refmonth_or_none(self._refmonthprefix)
    return self._refmonthprefix

  @property
  def yearprefix(self) -> int | None:
    if self._yearprefix is None:
      _ = self.has_yearprefix()
    return self._yearprefix

  def isfile(self):
    return self.entrypath.is_file()

  def isdir(self):
    return self.entrypath.is_dir()

  def has_dateprefix(self):
    if self._dateprefix:
      return True
    return self.set_dateprefix_if_any()  # returns True if it's set, otherwise False

  def set_dateprefix_if_any(self):
    try:
      space = self.name[10]
      if space != ' ':
        return False
      strdate = self.name[0: 10]
      pdate = dtfs.make_date_or_none(strdate)
      if pdate is None:
        return False
      self._dateprefix = pdate
      return True
    except (AttributeError, IndexError):
      pass
    return False

  def has_refmonthprefix(self):
    if self._refmonthprefix:
      return True
    return self.set_refmonths_if_any()  # returns True if it's set, otherwise False

  def set_refmonths_if_any(self):
    """
    As a string, refmonth prefix is a 'yyyy-mm' datum
    As a datetime.date, refmonth is a date on day 1
    """
    if self.has_dateprefix():
      return False
    try:
      space = self.name[7]  # because one needs a space after the prefix
      if space != ' ':
        return False
      str_rm = self.name[0: 7]
      year = int(str_rm[0:4])
      month = int(str_rm[5:7])
      self._refmonth = datetime.date(year, month, 1)
      self._refmonthprefix = f"{year}-{month}"
      return True
    except (AttributeError, IndexError):
      pass
    return False

  def has_yearprefix(self):
    if self._yearprefix:
      return True
    return self.set_yearprefix_if_any()  # returns True if it's set, otherwise False

  def set_yearprefix_if_any(self):
    """
    As a string, refmonth prefix is a 'yyyy-mm' datum
    As a datetime.date, refmonth is a date on day 1
    """
    if self.has_dateprefix():
      return False
    if self.has_refmonthprefix():
      return False
    try:
      space = self.name[4]  # because one needs a space after the prefix
      if space != ' ':
        return False
      str_rm = self.name[0: 4]
      self._yearprefix = int(str_rm[0:4])
      return True
    except (AttributeError, IndexError):
      pass
    return False

  def __repr__(self):
    _fopath = str(self.fopath)
    if len(_fopath) > 40:
      _fopath =  '...' + _fopath[-37: ]
    pstr = f"@ {_fopath}/{self.name}"
    parentname = "n/a"
    if self.parent is not None:
      parentname = self.parent.name
    return f"Entry(path={pstr}, parent={parentname})"

  def __str__(self):
    if self.dateprefix is None:
      self.has_dateprefix()
    if self.dateprefix is None and self.refmonth is None:
      self.has_refmonthprefix()
    if self.dateprefix is None and self.refmonth is None and self.yearprefix is None:
      self.has_yearprefix()
    ostr = f"""{self.__class__.__name__}
    {self.__repr__()}
    is file = {self.isfile()} | is dir = {self.isdir()}
    dateprefix = {self.dateprefix} | refmonth = {self.refmonth} | year = {self.yearprefix}
    """
    return ostr


def fetch_node_by_entrypath(entrypath, rootnode):
  global global_i
  findresult = findall(rootnode, filter_=lambda nd: str(nd.entrypath) == str(entrypath))
  global_i += 1
  scrmsg = f"global_i {global_i}"
  _ = scrmsg  # just for seeing in the debugger
  if len(findresult) > 0:
    node_on_ep = findresult[0]
    scrmsg = f"{global_i} @fetch_node_by_entrypath() => entry path = {entrypath} | node found => {node_on_ep}"
    print(scrmsg)
    return node_on_ep
  return None


def traverse_subtree(rootnode):
  """
  The way we inherited anytree.Node is problably wrong, though dont' we know yet where that would be.

  Here is what we found out:
    At:
      parentnode = fetch_node_by_entrypath(curpath, rootnode)
    It doesn't fetch 'parentnode' when a new directory level appears, it does only for the first level.
  """
  rootpath = rootnode.entrypath
  for curpath, dirs, files in os.walk(rootpath):
    scurpath = str(curpath)
    pathchunk = scurpath if len(scurpath) < 40 else '...' + scurpath[-37: ]
    scrmsg = f"Traversing {pathchunk}"
    print(scrmsg)
    ppcurpath = Path(str(curpath))
    entries = dirs + files
    parentnode = fetch_node_by_entrypath(curpath, rootnode)
    if parentnode is None:
      errmsg = f"""In traverse_subtree() | parentnode is None = {parentnode}
      rootnode {rootnode}
      failed to get parentnode with path:
        [{curpath}]"""
      raise OSError(errmsg)
    for entryname in entries:
      entryname = str(entryname)
      node = Entry(
        fopath=ppcurpath,
        name=entryname,
        parent=parentnode,
      )
      print(node)


def go_traverse_subtree():
  rootfolder = Path(init.testdir)
  parentpath, rootname = rootfolder.parent, rootfolder.name
  rootnode = Entry(
    fopath=parentpath,
    name=rootname,
    parent=None,
  )
  scrmsg = f"rootnode {rootnode}"
  print(scrmsg)
  traverse_subtree(rootnode)
  print('returned from traversal')
  nodes = findall(rootnode, filter_=lambda nd: nd.isfile())
  print([nd.entryname for nd in nodes])


def create_anytree_adhoc():
  # 1. Model the directory structure
  root = Node("project")
  src = Node("src", parent=root)
  tests = Node("tests", parent=root)
  main_py = Node("main.py", parent=src)
  utils_py = Node("utils.py", parent=src)
  test_main = Node("test_main.py", parent=tests)
  _, _, _ = main_py, utils_py, test_main  # for the IDE
  # 2. Print the tree visually
  for pre, fill, node in RenderTree(root):
    print(f"{pre}{node.name}")
  # Output:
  # project
  # ├── src
  # │   ├── main.py
  # │   └── utils.py
  # └── tests
  #     └── test_main.py
  # 3. Path-based Searching (Resolver)
  r = Resolver('name')
  found_node = r.get(root, "src/utils.py")
  print(found_node)  # Node('/project/src/utils.py')
  # 4. Glob/Filter Searching
  # Find all files ending in '.py'
  py_files = findall(root, filter_=lambda inode: inode.name.endswith('.py'))
  print([f.name for f in py_files])  # ['main.py', 'utils.py', 'test_main.py']


def adhoctest1():
  """
  create_anytree_adhoc()

  """
  entry = Entry(
    fopath=PosixPath("/a/b/c/src"),
    name='test.tst'
  )
  print(entry)
  scrmsg = f"is file? {entry.isfile()}"
  print(scrmsg)
  scrmsg = f"is dir? {entry.isdir()}"
  print(scrmsg)
  scrmsg = f"has dateprefix? {entry.has_dateprefix()}"
  print(scrmsg)
  # ==============================
  entry = Entry(
    fopath=PosixPath("/a/b/c/src"),
    name='2026-07-13 test.tst'
  )
  print(entry)
  scrmsg = f"is file? {entry.isfile()}"
  print(scrmsg)
  scrmsg = f"is dir? {entry.isdir()}"
  print(scrmsg)
  scrmsg = f"has dateprefix? {entry.has_dateprefix()}"
  print(scrmsg)
  scrmsg = f"dateprefix = {entry.dateprefix}"
  print(scrmsg)


def adhoctest2():
  go_traverse_subtree()


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest2()
