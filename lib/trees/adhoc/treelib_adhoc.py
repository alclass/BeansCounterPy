#!/usr/bin/env python3
"""
lib/trees/adhoc/treelib_adhoc.py
  Adhoctests (library) treelib

"""
from treelib import Tree


def create_treelib_adhoc():
  tree = Tree()
  # 1. Model the tree (Using paths as unique IDs)
  tree.create_node("project", "project")  # root
  tree.create_node("src", "project/src", parent="project")
  tree.create_node("tests", "project/tests", parent="project")
  tree.create_node("main.py", "project/src/main.py", parent="project/src")
  tree.create_node("utils.py", "project/src/utils.py", parent="project/src")
  # 2. Print the tree
  tree.show()
  # 3. Instant O(1) Search by ID (Path)
  node = tree.get_node("project/src/utils.py")
  print(node.tag)  # utils.py
  # 4. Filter / Subtree Search
  # Get all files under 'src'
  sub_nodes = tree.filter_nodes(lambda n: "project/src" in n.identifier)
  print([n.tag for n in sub_nodes])  # ['src', 'main.py', 'utils.py']


def adhoctest1():
  create_treelib_adhoc()


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
