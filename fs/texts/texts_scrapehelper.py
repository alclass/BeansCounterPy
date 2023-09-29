#!/usr/bin/env python3
"""
latin1_workaround.py
  Trying to find out a workaround to the "mês" word inside a latin1 text file,
    considering a string in Python is always a UTF-8 one.

Obs:
  # this script depends on the dados folder which is not added to the code's git repo


This simple module helped show that "mÃªs" is the way mês[latin1-in-file] is printed as a UTF-8 Python string
"""
import os
import settings as sett
EXAMPLE_FILENAME = 'fundo_report_example.txt'
datafolder_abspath = sett.get_bb_fi_extracts_datafolder_abspath_by_year(year=2023)
example_filepath = os.path.join(datafolder_abspath, EXAMPLE_FILENAME)


def read_example_fundofile():
  return open(example_filepath, encoding='latin1').read()


class NameCnpjScraper:

  def __init__(self, scrapetext=None):
    self.name = 'no-name'
    self.cnpj = 'no-cnpj'
    self.miolo = None
    self.scrapetext = scrapetext
    self.validate_scrapetext_or_get_example_if_any()

  def validate_scrapetext_or_get_example_if_any(self):
    if self.scrapetext is None:
      self.scrapetext = read_example_fundofile()
    if self.scrapetext is None:
      error_msg = 'Unable to read the example fundofile @ %s' % example_filepath
      raise OSError(error_msg)

  def extract_miolo(self):
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
    '''
    # raise an error due to miolo was not found
    
    error_msg = ('Error when trying to name & cnpj'
                 ' when looking up the miolo (the line inbetween the initial dashed lines)')
    raise ValueError(error_msg)
    '''

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
  wholetext = open(fundofilepath, encoding='latin1').read()
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
  filepath = sett.get_bb_fi_extract_filepath_by_year_month(2023, 4)
  scrapetexts = slice_fundofile_into_fundoscrapetexts(filepath)
  for scrapetext in scrapetexts:
    print('-*-|-*-'*20)
    print(scrapetext)
  print('total slices', len(scrapetexts))


if __name__ == '__main__':
  # test_get_name_n_cnpj()
  test_slice_fundos_scrapetexts()
