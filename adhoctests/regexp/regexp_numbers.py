"""
Functions for preparing various inputs passed to the DataFrame or Series
constructors before passing them to a BlockManager.
"""
import re
restr = r'^\d+ Pages$'
recomp = re.compile(restr)
text = """
bla bla
foo bar
123 Pages
bla bla
foo bar
"""


def process():
  lines = text.split('\n')
  lines = filter(lambda c: c != '', lines)
  for line in lines:
    if recomp.match(line):
      print(line, 'matched')
    else:
      print(line, 'NOT matched')


def adhoctest():
  """

  """
  pass


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
