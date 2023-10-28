#!/usr/bin/env python3
"""
commands/download/convert_comma_to_point_as_decimal.py
"""
import os
import glob
import re
point_decimal_place_compiled_re = re.compile(r'(?<=\d)\.(?=\d)')
comma_decimal_place_compiled_re = re.compile(r'(?<=\d),(?=\d)')
folderpath = (
  '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
  '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/'
  'BB FI Rendimentos Diários htmls/'
)


def save_file_with_text(filepath, text):
  filename = os.path.split(filepath)[-1]
  if os.path.isfile(filepath):
    print('Cannot disk-write', filename, 'for it already exists')
    return False
  print('Saving file', filename)
  fd = open(filepath, 'w', encoding='utf-8')
  fd.write(text)
  fd.close()
  return True


def step1_convert_thousands_points_to_empty_in_text_via_regexp(input_text):
  """
  Step 1: remove all thousands points in numbers
          this will avoid their being wrongly seen as decimal points after the comma-decimal conversion next
  """
  output_text = point_decimal_place_compiled_re.sub('', input_text)
  return output_text


def step2_convert_comma_to_point_in_text_via_regexp(input_text):
  """
  Step 2: replace all comma decimal points to point ones in numbers
          notice that in Step 1 thousands points were removed (above)
  """
  output_text = comma_decimal_place_compiled_re.sub('.', input_text)
  return output_text


class SingleFileConverter:
  def __init__(self, input_filepath, output_filepath):
    self.input_filepath = input_filepath
    self.output_filepath = output_filepath
    self.process()

  @property
  def input_filename(self):
    return os.path.split(self.input_filepath)[-1]

  @property
  def output_filename(self):
    return os.path.split(self.output_filepath)[-1]

  def convert_numbers_comma_to_point_n_savefile(self):
    print('SingleFileConverter Converting', self.input_filename, self.output_filename)
    input_text = open(self.input_filepath).read()
    # Step 1
    input_text = step1_convert_thousands_points_to_empty_in_text_via_regexp(input_text)
    # Step 2
    output_text = step2_convert_comma_to_point_in_text_via_regexp(input_text)
    # saves to output_filepath
    _ = save_file_with_text(self.output_filepath, output_text)

  def raise_exception_if_inputfile_is_missing(self):
    if not os.path.isfile(self.input_filepath):
      error_msg = 'Error: input file is missing =>' + self.input_filename
      raise OSError(error_msg)

  def outputfile_already_exists(self):
    if os.path.isfile(self.output_filepath):
      scrmsg = 'Output file [%s] already exists. Continuing.' % self.output_filename
      print(scrmsg)
      return True
    return False

  def process(self):
    self.raise_exception_if_inputfile_is_missing()
    if self.outputfile_already_exists():
      return
    self.convert_numbers_comma_to_point_n_savefile()


class Converter:

  def __init__(self):
    self.seq = 0
    self.inputfilepaths = None
    # self.find_inputfiles()

  def find_inputfiles(self):
    """
    filepaths = [os.path.join(folderpath, fn) for fn in os.listdir(folderpath) if fn.endswith(".html")]
    """
    self.inputfilepaths = []
    self.inputfilepaths = glob.glob(os.path.join(folderpath, '*.html'))

  def convert_comma_to_point_for_numbers_in_file(self, inputfilepath):
    self.seq += 1
    basefolderpath, filename = os.path.split(inputfilepath)
    print(self.seq, 'Converting', filename)
    input_text = open(inputfilepath).read()
    # Step 1
    input_text = step1_convert_thousands_points_to_empty_in_text_via_regexp(input_text)
    # Step 2
    output_text = step2_convert_comma_to_point_in_text_via_regexp(input_text)
    name, dotext = os.path.splitext(filename)
    output_filename = name + ' point-sep' + dotext
    output_filepath = os.path.join(basefolderpath, output_filename)
    _ = save_file_with_text(output_filepath, output_text)
    return output_text

  def process(self):
    if self.inputfilepaths is None:
      self.find_inputfiles()
    self.seq = 0
    for inputfilepath in self.inputfilepaths:
      self.convert_comma_to_point_for_numbers_in_file(inputfilepath)


def adhoctests():
  pass


def process():
  converter = Converter()
  converter.process()


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
