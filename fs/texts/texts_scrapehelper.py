#!/usr/bin/env python3
"""
latin1_workaround.py
  Trying to find out a workaround to the "mês" word inside a latin1 text file,
    considering a string in Python is always a UTF-8 one.

Obs:
  # this script depends on the dados folder which is not added to the code's git repo


This simple module helped show that "mÃªs" is the way mês[latin1-in-file] is printed as a UTF-8 Python string
"""
import fs.os.discover_levels_for_datafolders as disc
import fs.texts.exampleFundofileNTContent as exMod


class NameCnpjScraper:

  def __init__(self, scrapetext=None):
    self.name = 'no-name'
    self.cnpj = 'no-cnpj'
    self.miolo = None
    self.scrapetext = scrapetext
    self.validate_scrapetext_or_get_example_if_any()

  def validate_scrapetext_or_get_example_if_any(self):
    if self.scrapetext is None:
      example = exMod.ExampleFundoFile()
      self.scrapetext = example.read_n_return_example_fundofile_text()
      if self.scrapetext is None:
        error_msg = 'Unable to read the example fundofile @ %s' % example.filepath
        raise OSError(error_msg)

  def extract_miolo(self):
    """
      # raise an error due to miolo was not found

      error_msg = ('Error when trying to name & cnpj'
                   ' when looking up the miolo (the line inbetween the initial dashed lines)'
      raise ValueError(error_msg)
    """
    lines = self.scrapetext.split('\n')
    first_dashed_line = False
    for line in lines:
      if line.startswith('=====================') and not first_dashed_line:
        first_dashed_line = True
        continue
      line = line.strip(' \t\r\n')
      if first_dashed_line and len(line) > 0:
        self.miolo = line
        return

  def separate_name_n_cnpj_from_miolo(self):
    """
    example 04.061.224/0001-64
    """
    if self.miolo is None:
      '''
      error_msg = 'Program failed to get the string name & cnpj inbetween the initial dashed lines (scrapetext = %s)'\
          % self.scrapetext
      raise ValueError(error_msg)
      '''
      return
    pp = self.miolo.split(' ')
    self.cnpj = pp[-1]
    del pp[-1]
    pp = list(filter(lambda e: e != '', pp))
    self.name = ' '.join(pp)

  def scrape(self):
    self.extract_miolo()
    self.separate_name_n_cnpj_from_miolo()


def slice_fundofile_into_fundoscrapetexts(fundofilepath):
  # obs: client caller must enclose the call into a try/except caching FileNotFoundError
  wholetext = open(fundofilepath, encoding='latin1').read()
  # if FileNotFoundError is raised, flow will return from here
  # and scrapetexts.append() below will not happen, resulting in a missing month (for the file itself is missing)
  scrapetexts = []
  scrapetext = ''
  lines = wholetext.split('\n')
  found_first_entrance = False
  first_dashed_line = False
  second_dashed_line = False
  for line in lines:
    if not line.startswith('=====================') and not found_first_entrance:
      # the header runs until line hits a doubledashedline =====================
      # this first area should not be appended to scrapetexts
      continue
    if line.startswith('=====================') and not found_first_entrance:
      # it enters here only once
      first_dashed_line = True
      found_first_entrance = True
      scrapetext += line + '\n'  # start new one from beginning
      continue
    if line.startswith('=====================') and first_dashed_line and not second_dashed_line:
      first_dashed_line = False
      second_dashed_line = True
      scrapetext += line + '\n'  # start new one from beginning
      continue
    if line.startswith('=====================') and second_dashed_line and not first_dashed_line:
      first_dashed_line = True
      second_dashed_line = False
      if len(scrapetext) > 0:
        scrapetexts.append(scrapetext)  # append the previous one accumated
      scrapetext = line + '\n'
      continue
    scrapetext += line + '\n'
  if len(scrapetext) > 0:
    scrapetexts.append(scrapetext)  # append the last one accumated
  return scrapetexts


def get_name_n_cnpj_from_fundotext(scrapetext=None):
  scraper = NameCnpjScraper(scrapetext)
  scraper.scrape()
  return scraper.name, scraper.cnpj


def test_get_name_n_cnpj():
  name, cnpj = get_name_n_cnpj_from_fundotext()
  print('name [', name, '] cnpj [', cnpj, ']')


def test_slice_fundos_scrapetexts():
  abank = 'bdb'
  discoverer = disc.FolderYearMonthLevelDiscovererForBankAndKind(abank)
  filepath = discoverer.get_filepath_by_yearmonth(2023, 4)
  scrapetexts = slice_fundofile_into_fundoscrapetexts(filepath)
  for scrapetext in scrapetexts:
    print('-*-|-*-'*20)
    print(scrapetext)
  print('total slices', len(scrapetexts))


def adhoctests():
  ex = exMod.ExampleFundoFile()
  print(ex)


if __name__ == '__main__':
  """
  # test_get_name_n_cnpj()
  test_slice_fundos_scrapetexts()
  """
  adhoctests()
