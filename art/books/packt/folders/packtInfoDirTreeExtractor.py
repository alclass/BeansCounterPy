#!/usr/bin/env python3
"""
art/books/packt/folders/packtInfoDirTreeExtractor.py
  Explanation
    (...)

"/home/dados/Books/epub Books"

# the namedtuple strategy was changed to a 'dataclass' one
from collections import namedtuple
bookinfo_nt = namedtuple(
  'BookInfoNT',
  ['title', 'year', 'author', 'isbn']
)

======================================================
Method 2: Custom JSON Encoder (For Nested namedtuples)
======================================================
# notice Person and an Address inside it (a nested object)
from collections import namedtuple
import j-s-o-n

class NamedTupleEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, tuple) and hasattr(obj, '_asdict'):
            return obj._asdict()
        return super().default(obj)

# Example with nested namedtuple
Address = namedtuple('Address', ['street', 'city'])
Person = namedtuple('Person', ['name', 'age', 'address'])

address = Address(street='123 Main St', city='Boston')
person = Person(name='Bob', age=25, address=address)

json_str = json.dumps(person, cls=NamedTupleEncoder, indent=2)
print(json_str)

"""
import os
from dataclasses import dataclass, asdict
import re
import sys
from pathlib import Path
from collections.abc import Generator


@dataclass
class BookInfoDC:
  """
  Removing: inSpreadSheet: bool = False
  Because packts_midurl_ka is extracted from Packt's selected SpreadSheet,
    i.e., if packts_midurl_ka is not None, inSpreadSheet is True
  """
  title: str
  year: int
  authors: str
  isbn13: int
  relpath: str | None = None
  packts_midurl_ka: str | None = None

  @property
  def asdict(self):
    return asdict(self)

  @property
  def year_as_a_4_digit_str(self):
    """
    year may be type date though it's defined in the DataClass as int
    """
    year = self.year or 'n/a'
    try:
      year = str(year)
      year = year[:4]
    except (IndexError, TypeError):
      pass
    return year

  def __str__(self):
    isbn13 = "<isbn13>" if self.isbn13 is None else self.isbn13
    outstr = f"{self.title} | {self.year_as_a_4_digit_str} | {self.authors}  | {isbn13}"
    outstr += f" | {self.packts_midurl_ka} | {self.relpath}"
    return outstr


class BookInfo:
  """

  Former regex attempt for title did not consider special character such the dash (e.g. Socket-IO)
    re_s_title_n_year = r ^ ?P<title>[\b\\w+\b\\s*]+)(?P<year>\b\\d{4}\b){1}.+?$
  The one below is more generic/encompassing
  """
  re_s_title_n_year = r"^(?P<title>.+?)(?P<year>\b\d{4}\b){1}.+?$"
  re_c_title_n_year = re.compile(re_s_title_n_year)
  re_s_author_n_isbn = r"^.+?(\b\d{4}\b)\s*(?P<author>[\b\w+\b\s+]+.*?); Packt (?P<isbn>\d{13}).*?.epub$"
  re_c_author_n_isbn = re.compile(re_s_author_n_isbn)

  def __init__(self, booksfilename, relpath=None):
    self.booksfilename = booksfilename
    self.relpath = relpath
    self.title = None
    self.year = None
    self.author = None
    self.isbn13 = None
    self.astr = ''
    self.matched = False
    self.bookinfo_dc = None
    self.process()

  def transpose_to_dataclass_obj(self):
    if self.matched:
      self.bookinfo_dc = BookInfoDC(
        title=self.title,
        year=self.year,
        authors=self.author,
        isbn13=self.isbn13,
        relpath=self.relpath,
        packts_midurl_ka=None,
      )

  def _asdict(self):
    if self.bookinfo_dc:
      try:
        return asdict(self.bookinfo_dc)
      except TypeError:  # for either asdict as None or a non-asdict'able type
        pass
    return {}

  @property
  def asdict(self):
    """
    A property for method self._asdict()
    """
    return self._asdict()

  @property
  def as_bookinfo_dc(self):
    return self.bookinfo_dc

  def extract(self):
    # 1 extract pair title and year
    match_o = self.re_c_title_n_year.match(self.booksfilename)
    self.astr = self.re_c_title_n_year.findall(self.booksfilename)
    if match_o:
      self.matched = True
      self.title = match_o['title'].strip()
      self.year = match_o['year']
      self.author = None
      self.isbn13 = None
    # 2 extract pair author(s) and isbn
    match_o = self.re_c_author_n_isbn.match(self.booksfilename)
    self.astr += self.re_c_author_n_isbn.findall(self.booksfilename)
    if match_o:
      self.matched = True
      self.author = match_o['author'].strip()
      self.isbn13 = match_o['isbn']

  def process(self):
    self.extract()
    self.transpose_to_dataclass_obj()

  def __str__(self):
    outstr = f"""{self.booksfilename}
      title = [{self.title}] 
      year = {self.year}
      author = [{self.author}] 
      isbn = {self.isbn13}
      relpath = {self.relpath}
      matched = {self.matched} | astr = {self.astr}
      {self.bookinfo_dc}
    """
    return outstr


class DirWalkBookInfoExtractor:

  def __init__(self, basefolder_ap=None):
    self.basefolder_ap = basefolder_ap or Path(os.path.abspath(os.path.curdir))
    self.bookcounter = 0
    self.current_bookinfo = None
    self.current_folder_ap = None
    self.current_dir_bookinfos = []  # a per-directory buffer for a later yield
    # self.bi_non_isbn = 0

  @property
  def relpath(self):
    _relpath = self.current_folder_ap[len(str(self.basefolder_ap)):]
    _relpath = _relpath.lstrip('/')
    return _relpath

  def extract_info_from_filename(self, filename):
    """
      if bi.isbn is None:
        self.bi_non_isbn += 1

    :param filename:
    :return:
    """
    self.current_bookinfo = None
    bookinfo = BookInfo(filename, self.relpath)
    if bookinfo and bookinfo.matched:
      self.current_bookinfo = bookinfo
      self.bookcounter += 1
      # bc = self.bookcounter
      # print(bc, 'bookinfo_nt', self.current_bookinfo)

  def extract_books_meta_per_folder(self, files):
    self.current_dir_bookinfos = []
    files = filter(lambda f: f.endswith(('.epub', '.mobi')), files)
    files = filter(lambda f: f.find('Packt') > -1, files)
    for filename in files:
      self.extract_info_from_filename(filename)
      if self.current_bookinfo:
        self.current_dir_bookinfos.append(self.current_bookinfo)

  def gen_bookinfolist_via_dirwalk(self) -> Generator[BookInfo]:
    """
    This generator yields elements of type BookInfo
    (this type cannot be used for the collection-looping JSON write-functions,
      use the next one instead which yields an 'iterable' dict-element, BookInfo is not iterable)
    """
    self.current_dir_bookinfos = []
    for self.current_folder_ap, _, files in os.walk(self.basefolder_ap):
      self.extract_books_meta_per_folder(files)
      for bookinfo in self.current_dir_bookinfos:
        yield bookinfo  # .as_bookinfo_dc

  def gen_bookinfolist_as_dicts_via_dirwalk(self) -> Generator[dict]:
    """
    This generator yields elements of type dict
    """
    for bookinfo in self.gen_bookinfolist_via_dirwalk():
      pdict = bookinfo.asdict
      yield pdict


def adhoc_test2():
  bi_nt = BookInfoDC(
    title="test title",
    year=2026,
    authors="test author",
    isbn13=int("9" * 13),
    relpath="test relpath",
    packts_midurl_ka="test packtsmiddlepath",
  )
  print(bi_nt)
  print('asdict(bi_nt)', asdict(bi_nt))
  print('bi_nt.asdict', bi_nt.asdict)


def adhoc_test1():
  t = "AI Blueprints 2018 Joshua Eckroth +1; Packt 9781788992879.epub"
  bi = BookInfo(t)
  print('bi', bi)


def grab_bookinfos_thru_dirs(rootfolder_ap):
  extractor = DirWalkBookInfoExtractor(rootfolder_ap)
  for i, bookinfo in enumerate(extractor.gen_bookinfolist_via_dirwalk()):
    print(i+1, bookinfo)


def get_args():
  rootfolder_ap = None
  if len(sys.argv) > 1:
    rootfolder_ap = sys.argv[1]
  return rootfolder_ap


def process():
  """
  grab_bookinfos_thru_dirs(rootfolder_ap)
  """
  rootfolder_ap = get_args()
  extractor = DirWalkBookInfoExtractor(rootfolder_ap)
  for i, bi in enumerate(extractor.gen_bookinfolist_via_dirwalk()):
    seq = i + 1
    print(seq, bi)


if __name__ == '__main__':
  """
  adhoc_test1()
  process()
  """
  adhoc_test2()
