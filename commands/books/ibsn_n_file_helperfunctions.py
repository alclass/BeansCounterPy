#!/usr/bin/env python3
"""
commands/books/ibsn_n_file_helperfunctions.py
  => helper/util functions for the isbn scripts
"""
import datetime
import glob
import os
import re
import settings as sett
import fs.datesetc.datehilofs as hilodt
str_pattern_for_beginning_number = r'^(\d+) '
re_pattern_for_beginning_number = re.compile(r'^(\d+) ')


def extract_seq_n_title_from_seqfilename(filename):
  """
  The pattern filename expected is "{seqnumber} {title}.{ext}"
  Examples:
    "001 Mastering Javascript.json"
    "354 Learn Python - Second Edition.html"
    "1354 Learn Pandas - Third Edition.pdf"
  In the first example: seq = 1, title = "Mastering Javascript"
  For the second example, title will have its
    substring " - Second Edition.json" stripped out, ie:
      seq = 354, title = "Learn Python"
  The third example will extract:
    seq = 1354, title = "Learn Pandas"
  The file extension is not output extracted from here.
  """
  if filename is None:
    return None, None
  seq = None
  derivedtitle = None
  name, _ = os.path.splitext(filename)
  repatternstr_for_beginning_number = r'^(\d+) '
  matchobj = re_pattern_for_beginning_number.match(name)
  if matchobj:
    try:
      seq = int(matchobj.group(1))
    except ValueError:
      pass
  # seq = int(name[:3])
  try:
    pp = name.split(' ')
    derivedtitle = ' '.join(pp[1:])
    # derivedtitle = name[4:]
    pos = derivedtitle.find(' - ')
    if pos > -1:
      derivedtitle = derivedtitle[: pos]
  except (AttributeError, IndexError):
    pass
  return seq, derivedtitle


def form_todayprefixed_output_excelfilepath():
  databookpath = get_bookdata_dirpath()
  today = datetime.date.today()
  filename = f"{today} titles with isbn's.xlsx"
  filepath = os.path.join(databookpath, filename)
  return filepath


def get_bookdata_dirpath():
  rootpath = sett.get_apps_data_rootdir_abspath()
  middlename = 'bookdata'
  bookpath = os.path.join(rootpath, middlename)
  return bookpath


def get_bookdata_filepath():
  bookdirpath = get_bookdata_dirpath()
  files = glob.glob(bookdirpath + '/*.xlsx')
  if len(files) > 0:
    return files[0]
  return None


def get_json_filepaths():
  bookdirpath = get_bookdata_dirpath()
  jsonfilepaths = glob.glob(bookdirpath + '/*.json')
  return sorted(jsonfilepaths)


def search_an_excelfile_dateprefixed():
  bookdatafolderpath = get_bookdata_dirpath()
  xlsx_filepaths = glob.glob(bookdatafolderpath + '/*.xlsx')
  dateprefixed_filepaths = []
  for fpath in xlsx_filepaths:
    if not os.path.isfile(fpath):
      continue
    filename = os.path.split(fpath)[1]
    try:
      pp = filename.split(' ')
      strdate = pp[0]
      pdate = hilodt.make_date_with(strdate)
      if pdate:
        dateprefixed_filepaths.append(fpath)
    except (AttributeError, IndexError):
      pass
    if len(dateprefixed_filepaths) > 0:
      sorted(dateprefixed_filepaths)
      return dateprefixed_filepaths[-1]
  return None


def adhoctest():
  testseq = 0
  filename = "1354 Learn Pandas - Third Edition.pdf"
  seq, title = extract_seq_n_title_from_seqfilename(filename)
  testseq += 1
  print(testseq, 'filename => [', filename, '] extract() => seq [', seq, '] title =>', title)
  filepath = form_todayprefixed_output_excelfilepath()
  testseq += 1
  print(testseq, 'form_todayprefixed_output_excelfilepath() =>', filepath)
  dirpath = get_bookdata_dirpath()
  testseq += 1
  print(testseq, 'get_bookdata_dirpath() =>', dirpath)
  filepath = get_bookdata_filepath()
  testseq += 1
  print(testseq, 'get_bookdata_filepath() =>', filepath)
  filepaths = get_json_filepaths()
  n_files = len(filepaths)
  testseq += 1
  print(testseq, 'n_files', n_files, 'get_json_filepaths() =>')
  for i, fpath in enumerate(filepaths):
    print('\t', fpath)
    if i > 2:
      print('\t', 'etc')
      break
  filepath = search_an_excelfile_dateprefixed()
  testseq += 1
  print(testseq, 'search_an_excelfile_dateprefixed() =>', filepath)


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest()
