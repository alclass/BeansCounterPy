#!/usr/bin/env python3
"""

"""
import os
import fs.os.discover_levels_for_datafolders as disc


class ExampleFundoFile:
  """
  The main class in this module (not this one but NameCnpjScraper)
    does not derive its "scrapetext" from a file,
    but, for adhoc-testing reasons, from an example file was placed in the 2023 bb fi dirtree.
  Also:
    filename is conventioned
    folderpath is "discovered" though it's also a set of conventions
  """
  EXAMPLE_FILENAME = 'fundo_report_example.txt'
  BANK3LETTER = 'bdb'
  YEAR = 2023

  def __init__(self):
    self._folderpath = None
    self._filepath = None
    self.derive_paths()

  @property
  def folderpath(self):
    if self._folderpath is None:
      discoverer = disc.FolderYearMonthLevelDiscovererForBankAndKind(bank3letter=self.BANK3LETTER)
      self._folderpath = discoverer.get_folderpath_by_year(self.YEAR)
    return self._folderpath

  @property
  def filepath(self):
    if self._filepath is None:
      self._filepath = os.path.join(self.folderpath, self.EXAMPLE_FILENAME)
    return self._filepath

  def derive_paths(self):
    _ = self.filepath

  def read_n_return_example_fundofile_text(self):
    return open(self.filepath, encoding='latin1').read()

  def outdict(self):
    _outdict = {
      'examplefilename': self.EXAMPLE_FILENAME,
      'folderpath': self.folderpath,
      'filepath': self.filepath,
      'content': self.read_n_return_example_fundofile_text(),
    }
    return _outdict

  def __str__(self):
    outstr = """
    <obj ExampleFundoFile>
    examplefilename = {examplefilename}
    folderpath      = {folderpath}
    filepath        = {filepath}
    content         = {content}
    """.format(**self.outdict())
    return outstr


def adhoctests():
  ex = ExampleFundoFile()
  print(ex)


if __name__ == '__main__':
  """
  # test_get_name_n_cnpj()
  test_slice_fundos_scrapetexts()
  """
  adhoctests()
