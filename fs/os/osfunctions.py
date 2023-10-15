#!/usr/bin/env python3
"""
osfunctions.py
  contains helper functions for finding "qualified" (*) folders and files
(*) "qualified" means having certain characterics as in the example of name prefixes

As an example of a client user,
  module discover_levels_for_datafolders.py, also in the same package, calls functions in-here
"""
import os
import re


def find_foldernames_from_path(basepath):
  if basepath is None:
    return None
  entries = os.listdir(basepath)
  abspath_entries = [os.path.join(basepath, e) for e in entries]
  abspath_direntries = filter(lambda e: os.path.isdir(e), abspath_entries)
  foldernames = [os.path.split(e)[-1] for e in abspath_direntries]
  return foldernames


def find_filenames_from_path(basepath):
  if basepath is None or not os.path.isdir(basepath):
    return []
  entries = os.listdir(basepath)
  abspath_entries = [os.path.join(basepath, e) for e in entries]
  abspath_fileentries = filter(lambda e: os.path.isfile(e), abspath_entries)
  filenames = [os.path.split(e)[-1] for e in abspath_fileentries]
  sorted(filenames)
  return filenames


def find_filenames_from_path_with_ext(basepath, dotext):
  filenames = find_filenames_from_path(basepath)
  if dotext is None:
    return filenames
  try:
    dotext = str(dotext)
    # extfilenames = sorted(filter(lambda f: f.endswith(dotext), filenames))
    # filenames come already sorted from find_filenames_from_path(basepath)
    extfilenames = sorted(filter(lambda f: f.endswith(dotext), filenames))
    return extfilenames
  except ValueError:
    pass
  return []


def find_foldernames_with_regexp_on_path(str_regexp, basepath):
  foldernames = find_foldernames_from_path(basepath)
  recomp = re.compile(str_regexp)
  qualified_entries = list(filter(lambda e: recomp.match(e), foldernames))
  return qualified_entries


def find_filenames_with_regexp_on_path(str_regexp, basepath):
  entries = os.listdir(basepath)
  recomp = re.compile(str_regexp)
  qualified_entries = list(filter(lambda e: recomp.match(e), entries))
  return qualified_entries


def adhoctest():
  str_regexp = '^\d{4}\ '  # \-\d{2}
  basepath = ('/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
              'CEF bankdata OD/FI Extratos Mensais Ano a Ano CEF OD')
  qualentries = find_foldernames_with_regexp_on_path(str_regexp, basepath)
  qualentries.sort()
  print('-' * 40)
  print('Finding folders under', basepath)
  print(qualentries)
  str_regexp = '^\d{4}\-\d{2}\ '  # year dash month blank
  foldernames = qualentries
  folderpaths = [os.path.join(basepath, foldername) for foldername in foldernames]
  for folderpath in folderpaths:
    print('-'*40)
    print('Finding files under', folderpath)
    qualentries = find_filenames_with_regexp_on_path(str_regexp, folderpath)
    qualentries.sort()
    print(qualentries)


def process():
  adhoctest()


if __name__ == '__main__':
  """
  """
  process()
