#!/usr/bin/env python3
"""
lib/trees/adhoc/anytree_adhoc.py

"""
from anytree import Node, RenderTree
from anytree.resolver import Resolver
from anytree.search import findall  # find,


def create_anytree_adhoc():
  # 1. Model the directory structure
  root = Node("project")
  src = Node("src", parent=root)
  tests = Node("tests", parent=root)
  main_py = Node("main.py", parent=src)
  utils_py = Node("utils.py", parent=src)
  test_main = Node("test_main.py", parent=tests)
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
  create_anytree_adhoc()


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
