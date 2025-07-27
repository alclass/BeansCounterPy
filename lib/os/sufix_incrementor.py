#!/usr/bin/env python3
"""
fs/os/sufix_incrementor.py
  contains OS-related functions

At the time of this writing, class SufixIncrementor contains functionality
  to increment a numbered sufix in filename until a name is available, ie, until a non-existing path is formed.

Example:
  if filename 'bls_cpi.json' is on folder, an incremented one (as 'bls_cpi-001.json')
  will be checked if available. If so, that one is returned, if not, with another increment,
  'bls_cpi-002.json' will be checked. If so, that one is returned, if not, another increment will be tried.

The example in a nutshell:
  step 1 => 'bls_cpi.json' exists on folder
  step 2 => 'bls_cpi-001.json' also exists on folder
  step 3 => 'bls_cpi-002.json' does not exist, so it's returned as an available name

  However, there are only 1000 (or other 'hardwired' configured) available tries.
    If all tries are attempted and no names available, an OSError will be raised.
    TO-DO: a pre-executed routine, yet to be produced, may stop program run before
      the exception mentioned above to tell the user about the unavailability mentioned.
"""
from collections.abc import Iterable
import os
# import settings as sett


def extract_folderpath_from_filepath_or_none(filepath):
  try:
    return os.path.split(filepath)[0]
  except (AttributeError, TypeError):
    pass
  return None


def print_filenames_from_filepaths(filepaths, folderpath=None):
  if not isinstance(filepaths, Iterable):
    return
  if folderpath:
    print('Folderpath', folderpath)
  for fp in filepaths:
    try:
      filename = os.path.split(fp)[-1]
      print('\t', filename)
    except TypeError:
      continue


class SufixIncrementor:

  MAX_TRIES = 999
  DEFAULT_ZFILL = 3

  def __init__(self, filepath, zfill=None):
    """
    Derivable unmutable attributes: foldername & dotext
    Derivable mutable attributes: filename & name
    """
    self.filepath = filepath
    self.original_filepath = filepath
    self.raise_if_basefolder_does_not_exist()
    self.newfilepath = None
    self.ntries = 0
    self.nsufix = 0
    self.zfill = zfill or self.DEFAULT_ZFILL
    self.is_filepath_available = False

  def raise_if_basefolder_does_not_exist(self):
    folderpath = extract_folderpath_from_filepath_or_none(self.filepath)
    if folderpath is None or not os.path.isdir(folderpath):
      error_msg = f'folderpath [{folderpath}] does not exist in SufixIncrementor.'
      raise OSError(error_msg)

  @property
  def folderpath(self):
    return os.path.split(self.filepath)[0]

  def set_filepath_via_filename(self, newfilename):
    folderpath = self.folderpath
    self.filepath = os.path.join(folderpath, newfilename)

  @property
  def filename(self):
    return os.path.split(self.filepath)[-1]

  def set_filepath_via_name(self, newname):
    _, filename = os.path.split(self.filepath)
    _, dotext = os.path.splitext(filename)
    newfilename = newname + dotext
    self.set_filepath_via_filename(newfilename)

  @property
  def name(self):
    return os.path.splitext(self.filename)[0]

  @property
  def dotext(self):
    return os.path.splitext(self.filename)[-1]

  def does_incremented_sufix_file_exist(self):
    if not os.path.isfile(self.filepath):
      self.newfilepath = self.filepath
      return False
    return True

  def case1_file_has_no_hyphen(self):
    self.nsufix = 1
    newname = self.name + '-' + str(self.nsufix).zfill(self.zfill)
    self.set_filepath_via_name(newname)
    if self.does_incremented_sufix_file_exist():
      return self.add_an_increment_sufix_to_file_w_filepath()
    else:
      return

  def case2_file_has_a_numbered_sufix(self, pp):
    newname = '-'.join(pp[:-1]) + '-' + str(self.nsufix).zfill(self.zfill)
    self.set_filepath_via_name(newname)
    if self.does_incremented_sufix_file_exist():
      return self.add_an_increment_sufix_to_file_w_filepath()
    else:
      return

  def case3_file_needs_a_dashed_numbersufix(self):
    self.nsufix = 1
    sufix = '-' + str(self.nsufix).zfill(self.zfill)
    newname = self.name + sufix
    self.set_filepath_via_name(newname)
    if self.does_incremented_sufix_file_exist():
      return self.add_an_increment_sufix_to_file_w_filepath()
    else:
      return

  def add_an_increment_sufix_to_file_w_filepath(self):
    self.ntries += 1
    if self.ntries > self.MAX_TRIES:
      error_msg = f'Too many tries ({self.ntries}) in attempting to find an availablie numbered sufix filename.'
      error_msg += f'\t Last filename({self.filename}) tried.'
      error_msg += f'\t Base folder is ({self.folderpath}).'
      raise OSError(error_msg)
    if self.name.find('-') < 0:
      return self.case1_file_has_no_hyphen()
    pp = self.name.split('-')
    try:
      isufix = int(pp[-1])
      self.nsufix = isufix + 1
      return self.case2_file_has_a_numbered_sufix(pp)
    except ValueError:
      # sufix is not a number, one a sufix pending '-' which leads to case 3
      pass
    return self.case3_file_needs_a_dashed_numbersufix()

  def find_next_sufix_filepath_or_itself(self):
    if not os.path.isfile(self.filepath):
      # no need for processing, filepath is available not being present in folder
      self.is_filepath_available = True
      return self.filepath
    self.is_filepath_available = False
    self.add_an_increment_sufix_to_file_w_filepath()
    if self.newfilepath is None:
      error_msg = f'System could not find an available sufixed number filename after {self.ntries} tries in folder:'
      error_msg += f'\t {self.folderpath}'
      error_msg += f'\t Original filename {self.filename}'
      raise OSError(error_msg)
    return self.newfilepath

  def process(self):
    return self.find_next_sufix_filepath_or_itself()

  def __str__(self):
    outstr = f"""SufixIncrementor:
    original_filepath = {self.original_filepath}
    filepath = {self.filepath}
    filename = {self.filename}
    nsufix = {self.nsufix}
    ntries = {self.ntries}
    zfill = {self.zfill}
    max tries = {self.MAX_TRIES}
    """
    return outstr


def get_filepath_if_available_or_increment_numbersufix(filepath):
  incrementor = SufixIncrementor(filepath)
  filepath = incrementor.find_next_sufix_filepath_or_itself()
  print(incrementor)
  return filepath


def adhoctest():
  pass


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
