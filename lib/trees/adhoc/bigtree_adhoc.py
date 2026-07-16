#!/usr/bin/env python3
"""
lib/trees/adhoc/bigtree_adhoc.py
  Adhoctests (library) bigtree

"""
from bigtree import dict_to_tree
from bigtree import dataframe_to_tree
import pandas as pd


def make_tree_from_dict(path_dict):
  root = dict_to_tree(path_dict)
  root.show(attr_list=["age"])


def adhoccreate_tree_from_dict():
  """
  a [age=90]
  ├── b [age=65]
  │   ├── d [age=40]
  │   └── e [age=35]
  └── c [age=60]
  """
  path_dict = {
    "a": {"age": 90},
    "a/b": {"age": 65},
    "a/c": {"age": 60},
    "a/b/d": {"age": 40},
    "a/b/e": {"age": 35},
  }
  make_tree_from_dict(path_dict)


def create_tree_from_pddataframe(pddataframe):
  """
  (the same graph one as above)

  a [age=90]
  ├── b [age=65]
  │   ├── d [age=40]
  │   └── e [age=35]
  └── c [age=60]
  """
  root = dataframe_to_tree(pddataframe)
  root.show(attr_list=["age"])


def adhoccreate_w_pddataframe():
  pddataframe = pd.DataFrame(
    [
        ["a", 90],
        ["a/b", 65],
        ["a/c", 60],
        ["a/b/d", 40],
        ["a/b/e", 35],
    ],
    columns=["PATH", "age"],
  )
  create_tree_from_pddataframe(pddataframe)


def adhoctest1():
  adhoccreate_tree_from_dict()
  adhoccreate_w_pddataframe()


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
