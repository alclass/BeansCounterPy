#!/usr/bin/env python3
"""
bankFoldersDiscover.py
  envolopes module lookup_monthrange_convention_from_basedatafolder_on.py giving it BBFI's basefolder
"""
import os
import pdfquery
import fs.db.dbasfolder.lookup_monthrange_convention_from_basedatafolder_on as fndr
import fs.os.osfunctions as osfs
import models.banks.banksgeneral as bkge
CEF_BANK3LETTER = 'cef'


class PdfToXmlTransformer:

  def __init__(self, pdf_filepath=None):
    self.pdf_filepath = pdf_filepath
    self._basefolderpath = None
    self._pdf_filename = None
    self._xml_filename = None
    self._xml_filepath = None
    self.treat_pdf_filepath()
    self.was_tranformed = False
    self.transform_pdf_to_xml()

  def treat_pdf_filepath(self):
    if self.pdf_filepath is None or not os.path.isfile(self.pdf_filepath):
      error_msg = 'Pdf file does not exist [%s] ' % self.pdf_filepath
      raise OSError(error_msg)

  @property
  def basefolderpath(self):
    if self._basefolderpath is not None:
      return self._basefolderpath
    if self.pdf_filepath is None:
      return None
    self._basefolderpath = os.path.split(self.pdf_filepath)[0]
    return self._basefolderpath

  @property
  def pdf_filename(self):
    if self._pdf_filename is not None:
      return self._pdf_filename
    if self.pdf_filepath is None:
      return None
    self._pdf_filename = os.path.split(self.pdf_filepath)[-1]
    return self._pdf_filename

  @property
  def xml_filename(self):
    if self._xml_filename is not None:
      return self._xml_filename
    if self.pdf_filename is None:
      return None
    name = os.path.splitext(self.pdf_filename)[0]
    self._xml_filename = name + '.xml'
    return self._xml_filename

  @property
  def xml_filepath(self):
    if self._xml_filepath is not None:
      return self._xml_filepath
    if self.basefolderpath is None or self.xml_filename is None:
      return None
    self._xml_filepath = os.path.join(self.basefolderpath, self.xml_filename)
    return self._xml_filepath

  def transform_pdf_to_xml(self):
    if os.path.isfile(self.xml_filepath):
      scrmsg = 'File already exists [%s].' % self.xml_filepath
      print(scrmsg)
      self.was_tranformed = False
      return
    pdf = pdfquery.PDFQuery(self.pdf_filepath)
    pdf.load()
    # convert the pdf to XML
    print('Writing xml', self.xml_filename)
    print('\t' + self.xml_filepath)
    pdf.tree.write(self.xml_filepath, pretty_print=True)
    self.was_tranformed = True
    return


class YearBatchPdfToXmlTransformer:
  """
  Though the classname has 'year' in its name,
    it's important to enphasize that all pdf's in basefolder are queued to being transformed to xml,
    the year is just because of organization. (If ten years were there, it should rather be named
    DecadeBatchPdfToXmlTransformer instead of YearBatchPdfToXmlTransformer)
  """

  def __init__(self, folderpath=None):
    self.n_transf = 0
    if folderpath is None or not os.path.isdir(folderpath):
      error_msg = 'Error: folderpath %s does not exist.'
      raise OSError(error_msg)
    self.folderpath = folderpath
    pdfdotext = '.pdf'
    self.pdffilenames = osfs.find_filenames_from_path_with_ext(self.folderpath, pdfdotext)

  @property
  def total_pdffiles(self):
    return len(self.pdffilenames)

  def batch_transform_pdffiles_into_xml(self):
    for i, pdffilename in enumerate(self.pdffilenames):
      seq = i + 1
      print(seq, 'Processing pdf for', pdffilename)
      pdffilepath = os.path.join(self.folderpath, pdffilename)
      try:
        pdf_o = PdfToXmlTransformer(pdffilepath)  # instantiate & execute
        if pdf_o.was_tranformed:
          self.n_transf += 1
          print('n_transf', self.n_transf)
      except OSError as e:
        print('OSError', e)
        pass

  def process(self):
    self.batch_transform_pdffiles_into_xml()

  def outdict(self):
    _outdict = {
      'datadir_abspath': self.folderpath,
      'total_pdffiles': self.total_pdffiles,
    }
    return _outdict

  def __str__(self):
    outstr = """
    datadir_abspath = {datadir_abspath}
    n of pdf files = {total_pdffiles}
    """.format(**self.outdict())
    return outstr


def xmltransform_all_data_years():
  basefolderpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(CEF_BANK3LETTER)
  finder = fndr.DatePrefixedOSEntriesFinder(basefolderpath)
  # roll all available data years
  for yearfolderpath in finder.gen_folderpaths_within_yearrange_or_wholeinterval():
    yearbatch_converter = YearBatchPdfToXmlTransformer(yearfolderpath)
    yearbatch_converter.process()
    print(yearbatch_converter)


def adhoctest():
  basefolderpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(CEF_BANK3LETTER)
  finder = fndr.DatePrefixedOSEntriesFinder(basefolderpath)
  # roll all available data years
  for yearfolderpath in finder.gen_folderpaths_within_yearrange_or_wholeinterval():
    print('yearfolderpath', yearfolderpath)


def process():
  xmltransform_all_data_years()


if __name__ == '__main__':
  """
  adhoctest()
  """
  process()
