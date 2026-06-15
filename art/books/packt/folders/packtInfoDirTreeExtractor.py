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
import sys
from pathlib import Path
from collections.abc import Generator
from art.books.packt.BookModel import BookInfoDC
from art.books.packt.BookModel import BookInfo
from dataclasses import asdict


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
    Each element yielded is not a dictm it's a bookinfo
    Look up below another generator that yields bookinfo as dict

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
    Each element yielded is a dict from bookinfo
    """
    for bookinfo in self.gen_bookinfolist_via_dirwalk():
      # notice that bookinfo contains a bit more fields than bookinfo_dc
      pdict = bookinfo.asdict
      yield pdict

  def gen_bookinfolist_as_bidcdicts_via_dirwalk(self) -> Generator[dict]:
    """
    Each element yielded is a dict from bookinfo_dc
    """
    for bookinfo in self.gen_bookinfolist_via_dirwalk():
      # notice that bookinfo_dc contains a bit less fields than bookinfo_dc
      yield bookinfo.bookinfo_dc.asdict


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
