#!/usr/bin/env python3
"""
commands/books/book_chosen_opener_in_browser.py
  accepts an ISBN or title from the command line and, if related book is in db,
    opens its Packt's webpage on the default browser.
"""
URL_to_interpole = 'https://www.packtpub.com/book/data/{isbn}'

def adhoctest():
  pass


def process():
  ISBNLister()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
