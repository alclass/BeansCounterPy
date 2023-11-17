#!/usr/bin/env python3
"""
commands/books/regexp_isbns_from_jsons.py
  => an experiment to find an efficient way to find ISBN's inside json files

"""
import datetime
import os
import glob
import json
import pandas as pd
import settings as sett
pd.set_option('display.max_rows', 100)


def extract_seq_n_title_from_seqfilename(filename):
  name, _ = os.path.splitext(filename)
  # there's a 3-digit number plus blank as prefix
  seq = int(name[:3])
  derivedtitle = name[4:]
  pos = derivedtitle.find(' - ')
  if pos > -1:
    derivedtitle = derivedtitle[: pos]
  return seq, derivedtitle


def get_bookdata_dirpath():
  rootpath = sett.get_apps_data_rootdir_abspath()
  middlename = 'bookdata'
  bookpath = os.path.join(rootpath, middlename)
  return bookpath


def form_output_excelfilepath():
  databookpath = get_bookdata_dirpath()
  today = datetime.date.today()
  filename = f"{today} titles with isbn's.xlsx"
  filepath = os.path.join(databookpath, filename)
  return filepath


def get_json_filepaths():
  bookdirpath = get_bookdata_dirpath()
  jsonfilepaths = glob.glob(bookdirpath + '/*.json')
  return sorted(jsonfilepaths)


def get_bookdata_filepath():
  bookdirpath = get_bookdata_dirpath()
  files = glob.glob(bookdirpath + '/*.xlsx')
  if len(files) > 0:
    return files[0]
  return None


def jsonfile_exists(name):
  filename = name + '.json'
  folderpath = get_bookdata_dirpath()
  try:
    filepath = os.path.join(folderpath, filename)
    return os.path.isfile(filepath)  # returns True or False depending on file existence
  except TypeError:
    pass
  return False


class ISBNFinder:

  def __init__(self):
    self.df = None  # reserved to receive a pandas's dataframe
    self.n_rolled = 0
    self.n_found = 0
    self.n_jsons_without_info = 0
    self.instanceseq = 0
    self.output_tupledict = {}  # dict key is seqfile (or fileseq), its value is tuple (isbn13, title)
    self.process()

  def find_on_text(self, text):
    packt_str = 'Packt'
    pos = text.find(packt_str)
    if pos > -1:
      print('Found', packt_str, 'at', pos)
      self.n_found += 1
    else:
      print(packt_str, 'not found')

  def roll_jsonfiles_as_text(self):
    filepaths = get_json_filepaths()
    for jsonpath in filepaths:
      text = open(jsonpath).read()
      self.find_on_text(text)

  def instropect_json(self, jsondict, derivedtitle, fileseq):
    try:
      items = jsondict['items']
      self.instanceseq += 1
      for i, item in enumerate(items):
        volinf = item['volumeInfo']
        title = volinf['title']
        if title.find(derivedtitle) > -1 or derivedtitle.find(title) > -1:
          print(i + 1, title)
          try:
            identifiers_dictlist = volinf['industryIdentifiers']
            isbn13 = identifiers_dictlist[0]
            isbn10 = identifiers_dictlist[1]
            isbn13label = isbn13['type']
            isbn13_strnumber = isbn13['identifier']
            if isbn13label == 'ISBN_13' and len(isbn13_strnumber) == 13:
              print('\t', isbn13label, isbn13_strnumber)
              if fileseq not in self.output_tupledict:
                self.output_tupledict[fileseq] = (isbn13_strnumber, title)
            print('\t', isbn10['type'], isbn10['identifier'])
          except IndexError:
            print('No isbn found.')
    except KeyError:
      self.n_jsons_without_info += 1

  def roll_jsonfiles_w_structure(self):
    filepaths = get_json_filepaths()
    for n_file, jsonpath in enumerate(filepaths):
      filename = os.path.split(jsonpath)[1]
      json_fd = open(jsonpath, 'r', encoding='utf-8')
      jsondict = json.load(json_fd)
      print(n_file + 1, filename)
      fileseq, derivedtitle = extract_seq_n_title_from_seqfilename(filename)
      self.instropect_json(jsondict, derivedtitle, fileseq)
      self.n_rolled += 1

  def process(self):
    # self.roll_jsonfiles_as_text()
    self.roll_jsonfiles_w_structure()
    print('instanceseq', self.instanceseq)
    print('n_rolled', self.n_rolled)
    print('n_jsons_without_info', self.n_jsons_without_info)
    self.transform_tupledict_to_datafram()
    print(self.df.head())
    excelfilepath = form_output_excelfilepath()
    filename = os.path.split(excelfilepath)[1]
    print('Saving', filename, 'at', excelfilepath)
    self.df.to_excel(excelfilepath)
    # self.report_tupledict()

  def transform_tupledict_to_datafram(self):
    dictlist = []
    print('transform_tupledict_to_datafram')
    sorted(self.output_tupledict)
    for seqfile in self.output_tupledict.keys():
      tupl = self.output_tupledict[seqfile]
      isbn13 = tupl[0]
      title = tupl[1]
      pdict = {'seq': seqfile, 'isbn': isbn13, 'title': title}
      dictlist.append(pdict)
    self.df = pd.DataFrame(dictlist)

  def report_tupledict(self):
    print('Reporting')
    sorted(self.output_tupledict)
    for seqfile in self.output_tupledict.keys():
      tupl = self.output_tupledict[seqfile]
      isbn13 = tupl[0]
      title = tupl[1]
      print(seqfile, isbn13, title)

  def __str__(self):
    outstr = f"""
    instanceseq = {self.instanceseq}
    n_rolled = {self.n_rolled}
    n_jsons_without_info {self.n_jsons_without_info}
    """
    return outstr


def adhoctest():
  pass


def process():
  ISBNFinder()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
