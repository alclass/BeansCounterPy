#!/usr/bin/env python3
"""
commands/books/regexp_isbns_from_jsons.py
  => an experiment to find an efficient way to find ISBN's inside json files

URL_to_interpole = 'https://www.packtpub.com/book/data/{isbn}'
"""
import os
import glob
import time
import json
import pandas as pd
import requests

import settings as sett
API_URL_to_interpole = 'https://www.googleapis.com/books/v1/volumes?q=title:{title_with_pluses}'
INTERVAL_INBETWEEN_APICALLS_IN_SEC = 3
pd.set_option('display.max_rows', 100)


def get_bookdata_dirpath():
  rootpath = sett.get_apps_data_rootdir_abspath()
  middlename = 'bookdata'
  bookpath = os.path.join(rootpath, middlename)
  return bookpath


def get_json_filepaths():
  bookdirpath = get_bookdata_dirpath()
  jsonfilepaths = glob.glob(bookdirpath + '/*.json')
  return jsonfilepaths


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
    self.n_rolled = 0
    self.n_found = 0
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

  def roll_jsonfiles_w_structure(self):
    filepaths = get_json_filepaths()
    for jsonpath in filepaths:
      json_fd = open(jsonpath, 'r', encoding='utf-8')
      j_o = json.load(json_fd)
      print(j_o)
      self.n_rolled += 1

  def process(self):
    self.roll_jsonfiles_as_text()
    self.roll_jsonfiles_w_structure()

  def __str__(self):
    return 'ISBNFinder'


def adhoctest():
  pass


def process():
  ISBNFinder()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
