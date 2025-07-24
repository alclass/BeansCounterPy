#!/usr/bin/env python3
"""
art/books/search_isbns_from_jsons.py
  => searches ISBN's inside json files using known dict attributes

  Basically, the dict attributes used are the following:
    volinf = item['volumeInfo']
    title = volinf['title']
    identifiers_dictlist = volinf['industryIdentifiers']
    isbn13 = identifiers_dictlist[0]
    isbn10 = identifiers_dictlist[1]
"""
from collections import namedtuple
import os
import json
import pandas as pd
import art.books.packt.functions_packt_books_data_excel_json_pandas as isbnfs
pd.set_option('display.max_rows', 100)
BookNT = namedtuple('BookNT', ['title', 'isbn13list'])


class IBSNSearcher:

  def __init__(self):
    self.df = None  # reserved to receive a pandas's dataframe
    self.n_rolled = 0
    self.n_found = 0
    self.n_jsons_without_info = 0
    self.instanceseq = 0
    self.output_namedtupledict = {}  # dict key is seqfile (or fileseq), its value is tuple (isbn13, title)
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
            # isbn10label = isbn10['type']
            isbn13_strnumber = isbn13['identifier']
            # isbn10_strnumber = isbn10['identifier']
            if isbn13label == 'ISBN_13' and len(isbn13_strnumber) == 13:
              print('\t', isbn13label, isbn13_strnumber)
              if fileseq not in self.output_namedtupledict:
                booknt = BookNT(title=title, isbn13list=[isbn13_strnumber])
                self.output_namedtupledict[fileseq] = booknt
              else:
                booknt = self.output_namedtupledict[fileseq]
                booknt.isbn13list.append(isbn13_strnumber)
            # print('\t', isbn10['type'], isbn10['identifier'])
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

  def transform_tupledict_to_datafram(self):
    print('instanceseq', self.instanceseq)
    print('n_rolled', self.n_rolled)
    print('n_jsons_without_info', self.n_jsons_without_info)
    dictlist = []
    print('transform_tupledict_to_datafram')
    sorted(self.output_namedtupledict)
    for seqfile in self.output_namedtupledict.keys():
      booknt = self.output_namedtupledict[seqfile]
      title = booknt.title
      isbn13liststr = ', '.join(booknt.isbn13list)
      n_isbns = len(booknt.isbn13list)
      pdict = {'n_isbns': n_isbns, 'title': title, 'isbn13liststr': isbn13liststr}
      dictlist.append(pdict)
    self.df = pd.DataFrame(dictlist)

  def save_excel_file(self):
    """
    """
    excelfilepath = isbnfs.form_todayprefixed_output_excelfilepath()
    filename = os.path.split(excelfilepath)[1]
    # remove column 'n_isbns' for it's dynamically created derived from isbn13liststr
    self.df.drop(['n_isbns'], axis=1, inplace=True)
    print('Saving', filename, 'at', excelfilepath)
    self.df.to_excel(excelfilepath)

  def process(self):
    # self.roll_jsonfiles_as_text()
    self.roll_jsonfiles_w_structure()
    self.transform_tupledict_to_datafram()
    self.save_excel_file()
    self.report_processed_dataframe()

  def report_processed_dataframe(self):
    print('Reporting')
    print(self.df.to_string())

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
