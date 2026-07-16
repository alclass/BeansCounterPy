#!/usr/bin/env python3
"""
lib/osfs/filefolder_retriever_fs.py
  Contains helper functions for finding "qualified" (*) folders and files

(*) "qualified" means having certain characterics as in the example of name prefixes

As an example of a client user:
  module discover_levels_for_datafolders.py, also in the same package, calls functions in-here
"""
from pathlib import Path, PosixPath
import glob
import os
import re
import lib.osfs as init  # init.INTSUFIX_LIMIT_WHEN_DERIV_NONEXIST_FN
DEFAULT_MASK_DOT_EXT = init.DEFAULT_MASK_DOT_EXT
INTSUFIX_LIMIT_WHEN_DERIV_NONEXIST_FN = init.INTSUFIX_LIMIT_WHEN_DERIV_NONEXIST_FN


def derive_a_non_existent_sufixnumbered_filename_from(filepath):
  folderpath, filename = os.path.split(filepath)
  name, dotext = os.path.splitext(filename)
  sufix_number = 0
  while 1:
    sufix_number += 1
    lastfilename = name + '-' + str(sufix_number).zfill(3) + dotext
    lastpath = os.path.join(folderpath, lastfilename)
    if not os.path.isfile(lastpath):
      return lastfilename
    if sufix_number > INTSUFIX_LIMIT_WHEN_DERIV_NONEXIST_FN:
      break
  error_msg = f"""Error: system could not find a sufixnumberer filename.
    Directory: {folderpath}
    Source Filename: {filename}
    Last filename tried: {lastfilename}
    """.format(folderpath=folderpath, filename=filename, lastfilename=lastfilename)
  raise OSError(error_msg)


def save_file_with_text(filepath, text):
  filename = os.path.split(filepath)[-1]
  if os.path.isfile(filepath):
    print('Cannot disk-write', filename, 'for it already exists')
    return False
  print('Saving file', filename)
  fd = open(filepath, 'w', encoding='utf-8')
  fd.write(text)
  fd.close()
  return True


def retrieve_filepaths_in_folder_or_empty(basefolderpath: str | PosixPath, p_dotext: str | None) -> list[Path]:
  """
  This function selects files with glob.glob(criterium). An alternative way is:
    filepaths = [os.path.join(folderpath, fn) for fn in os.listdir(folderpath) if fn.endswith(.html)]

  if not basefolderpath.is_dir():
    error_msg = 'Directory does not exist => [%s]' % str(basefolderpath)
    raise OSError(error_msg)
  """
  if basefolderpath is None:
    return []
  if not isinstance(basefolderpath, Path):
    basefolderpath = Path(os.path.abspath(str(basefolderpath)))
  if not basefolderpath.is_dir():
    return []
  dotext = p_dotext if p_dotext is not None else ''
  if dotext.startswith('.'):
    dotext = f".{dotext}"
  entries =  os.listdir(basefolderpath)
  fentries = map(lambda e: basefolderpath / e, entries)
  filepaths = filter(lambda f: f.is_file(), fentries)
  filepaths = filter(lambda f: f.suffix == dotext, filepaths)
  filepaths = list(filepaths)
  return filepaths


def retrieve_foldernames_from_basefolderpath(basefolderpath: str | Path) -> list[str]:
  if basefolderpath is None:
    return []
  if not isinstance(basefolderpath, Path):
    basefolderpath = Path(os.path.abspath(str(basefolderpath)))
  if not basefolderpath.is_dir():
    return []
  entries = os.listdir(basepath)
  ap_entries = [basefolderpath / e for e in entries]
  folderpaths = filter(lambda e: e.is_dir(), ap_entries)
  foldernames = [e.name for e in folderpaths]
  return foldernames


def retrieve_filenames_in_folder_or_empty(basefolderpath: str | PosixPath, p_dotext: str | None) -> list[str]:
  filepaths = retrieve_filepaths_in_folder_or_empty(basefolderpath, p_dotext)
  filenames = [e.name for e in filepaths]
  filenames.sort()
  return filenames


def find_filenames_from_path_with_ext(basefolderpath: str | PosixPath, p_dotext: str) -> list[str]:
  return retrieve_filenames_in_folder_or_empty(basefolderpath, p_dotext)


def find_foldernames_with_regexp_on_path(str_regexp: str, basepath: str | PosixPath):
  foldernames = retrieve_foldernames_from_basefolderpath(basepath)
  recomp = re.compile(str_regexp)
  qualified_entries = list(filter(lambda e: recomp.match(e), foldernames))
  return qualified_entries


def find_filenames_with_regexp_on_path(str_regexp: str, basefolderpath: str | PosixPath) -> list[str]:
  filenames = retrieve_filenames_in_folder_or_empty(basefolderpath)
  if len(entries) == 0:
    return []
  recomp = re.compile(str_regexp)
  regex_filtered_filenames = list(filter(lambda e: recomp.match(e), filenames))
  return regex_filtered_filenames


def gather_all_files_up_from(rootfolder: Path | str) -> list[Path]:
  if rootfolder is None:
    return []
  if not isinstance(rootfolder, Path):
    rootfolder = Path(os.path.abspath(str(rootfolder)))
  if not rootfolder.exists() or not rootfolder.is_dir():
    return []
  allfiles = []
  for curpath, _, filenames in os.walk(rootfolder):
    files = [Path(curpath) / fn for fn in filenames]
    allfiles.extend(files)
  return allfiles


def adhoctest():
  str_regexp = r'^\d{4}\ '  # \-\d{2}
  basepath = (
      '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/'
      'dados/bankdata/104 CEF bankdata/FI Extratos Mensais Ano a Ano CEF OD'
  )
  qualentries = find_foldernames_with_regexp_on_path(str_regexp, basepath)
  qualentries.sort()
  print('-' * 40)
  print('Finding folders under', basepath)
  print(qualentries)
  str_regexp = r'^\d{4}\-\d{2}\ '  # year dash month blank
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
