#!/usr/bin/env python3
"""
art/books/packt/folders/packtInfoDirTreeExtractor.py
  Explanation
"""
import re
from dataclasses import dataclass, asdict


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


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
