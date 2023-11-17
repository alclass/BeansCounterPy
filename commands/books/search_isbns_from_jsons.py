#!/usr/bin/env python3
"""
commands/books/search_isbns_from_jsons.py
  => searches ISBN's inside json files using known dict attributes

  Basically, the dict attributes used are the following:
    volinf = item['volumeInfo']
    title = volinf['title']
    identifiers_dictlist = volinf['industryIdentifiers']
    isbn13 = identifiers_dictlist[0]
    isbn10 = identifiers_dictlist[1]
"""
import os
import json
import pandas as pd
import commands.books.ibsn_n_file_helperfunctions as isbnfs
pd.set_option('display.max_rows', 100)


class IBSNSearcher:

  def __init__(self):
    self.df = None  # reserved to receive a pandas's dataframe
    self.n_rolled = 0
    self.n_found = 0
    self.n_jsons_without_info = 0
    self.instanceseq = 0
    self.output_tupledict = {}  # dict key is seqfile (or fileseq), its value is tuple (isbn13, title)
    self.process()

  def find_on_text(self, text):
    """
    This method has been used. The search is done by method instropect_json().
      Maybe it should be replanned as a second checker for the present of the publisher's name on record.
    """
    packt_str = 'Packt'
    pos = text.find(packt_str)
    if pos > -1:
      print('Found', packt_str, 'at', pos)
      self.n_found += 1
    else:
      print(packt_str, 'not found')

  def roll_jsonfiles_as_text(self):
    filepaths = isbnfs.get_json_filepaths()
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
    filepaths = isbnfs.get_json_filepaths()
    for n_file, jsonpath in enumerate(filepaths):
      filename = os.path.split(jsonpath)[1]
      json_fd = open(jsonpath, 'r', encoding='utf-8')
      jsondict = json.load(json_fd)
      print(n_file + 1, filename)
      fileseq, derivedtitle = isbnfs.extract_seq_n_title_from_seqfilename(filename)
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
    excelfilepath = isbnfs.form_todayprefixed_output_excelfilepath()
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
  IBSNSearcher()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
