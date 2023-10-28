#!/usr/bin/env python3
import time
import datetime
import os
import sys
import requests
import models.banks.banksgeneral as bkge
# URL_BB_RENTAB_DIA = 'http://www21.bb.com.br/portalbb/rentabilidade/index.jsp?tipo=01'
URL_BB_RENTAB_DIA = 'https://www37.bb.com.br/portalbb/tabelaRentabilidade/rentabilidade/gfi7,802,9085,9089,1.bbx'
BB_BANK3LETTER = 'bdb'
BB_RENTAB_DIA_MIDDLE_FOLDERNAME = 'BB FI Rendimentos Diários htmls'  # TO-DO move this const to the BANK module or else
htmlfilename_after_date = ' BB rendimentos no dia comma-sep.html'


def mount_daybased_targetfilepath(pdate=None):
  basefolderpath = bkge.BANK.get_bank_fi_folderpath_by_its3letter(BB_BANK3LETTER)
  rentabdia_folderpath = os.path.join(basefolderpath, BB_RENTAB_DIA_MIDDLE_FOLDERNAME)
  if not os.path.isdir(rentabdia_folderpath):
    error_msg = 'Directory [%s] does not exist.' % rentabdia_folderpath
    raise OSError(error_msg)
  if pdate is None:
    pdate = datetime.date.today()
  filename = str(pdate) + ' BB rendimentos no dia comma-sep.html'
  filepath = os.path.join(rentabdia_folderpath, htmlfilename_after_date)
  return filepath


class BBRendDiaDownloader:

  def __init__(self, targetfilepath=None, download_in_cd=False):
    self.today = datetime.date.today()
    self.download_in_cd = download_in_cd
    self.ok_downloaded = False
    self.targetfilepath = targetfilepath
    self.treat_targetfilepath()

  @property
  def targetfile_already_exists(self):
    if os.path.isfile(self.targetfilepath):
      return True
    return False

  def treat_targetfilepath(self):
    if self.targetfilepath is None:
      self.targetfilepath = mount_daybased_targetfilepath()

  def download_in_currentdir(self):
    today = datetime.date.today()
    table_filename = '%s bb rendimento.htm' % today
    if os.path.isfile(table_filename):
      print('Today\'s table (', table_filename, ') has already been downloaded.')
      sys.exit(0)
    url = URL_BB_RENTAB_DIA
    comm = 'wget -c ' + url
    ret_val = os.system(comm)
    # retVal = 0
    if ret_val == 0:
      print('Download OK')
      self.ok_downloaded = True
    else:
      print('A problem occurred. Table could not be downloaded.')
      sys.exit(0)
    print('Renaming table to', table_filename)
    os.rename('index.jsp?tipo=01', table_filename)
    print('retVal', ret_val)
    if os.path.isfile(table_filename):
      print('Rename OK.')
    else:
      print('Could not rename.')

  def download_to_targetdir(self):
    """
    TO-DO include get_args() to make to option available
      This downloads from cli to the current directory whereas the other option downloads to a configured path
      There is not an option for downloading to an arbitrary given path
    """
    print('Trying to download BB daily rends to', self.targetfilepath)
    self.ok_downloaded = False
    if self.targetfile_already_exists:
      scrmsg = 'Targetfile already exists, probably it has already been downloaded.\n'
      scrmsg += '\tLocation: [%s]' % self.targetfilepath
      print(scrmsg)
      return False
    url = URL_BB_RENTAB_DIA
    print(url)
    req = requests.get(url)
    fd = open(self.targetfilepath, 'wb')
    fd.write(req.content)
    # ok unless an exception is raise above
    self.ok_downloaded = True
    print('Downloaded complete.', time.ctime())
    return True

  def download(self):
    if self.download_in_cd:
      self.download_in_currentdir()
      return
    self.download_to_targetdir()

  def __str__(self):
    outstr = """
    targetfilepath = {targetfilepath}
    downloaded = {ok_downloaded}
    """.format(targetfilepath=self.targetfilepath, ok_downloaded=self.ok_downloaded)
    return outstr


def adhoctest():
  pass


def process():
  downloader = BBRendDiaDownloader()
  downloader.download()
  print(downloader)


if __name__ == '__main__':
  """
  adhoctest()
  pass
  """
  process()
