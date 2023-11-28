#!/usr/bin/env python3
"""
commands/download/downloadTabelaBBRendimentosDia.py
  downloads BB's app-fundos daily report
  After downloading, it:
    a) converts comma-sep html into a point-sep one;
    b) converts the 3 point-sep html tables to its csv equivalent.
"""
import datetime
import os
import sys
import requests
import fs.datesetc.argparse_dates as apdt  # apdt.get_args
import models.banks.bb.fi.bbfi_file_find as ffnd  # for ffnd.BBFIFileFinder.Props.commapoint_htmlfilename_to_interpol
import models.banks.bankpathfinder as bkfnd  # .BankOSFolderFileFinder
import models.banks.bb.fi.fibb_daily_results_numbers_comma_to_point_convert as commapoint  # .SingleFileConverter
import models.banks.bb.fi.fibb_daily_results_html_to_csv_via_pandas_transform as transf  # .WithPandasHtmlToCsvConverter

# (old) URL_BB_RENTAB_DIA = 'http://www21.bb.com.br/portalbb/rentabilidade/index.jsp?tipo=01'
URL_BB_RENTAB_DIA = 'https://www37.bb.com.br/portalbb/tabelaRentabilidade/rentabilidade/gfi7,802,9085,9089,1.bbx'
BB_BANK3LETTER = 'bdb'
BB_RENTAB_DIA_MIDDLE_FOLDERNAME = 'BB FI Rendimentos Diários htmls'  # TO-DO move this const to the BANK module or else
htmlfilename_after_date = ' BB rendimentos no dia comma-sep.html'


class BBRendDiaDownloader:

  def __init__(self, targetfilepath=None, download_in_cd=False):
    self.time_start = datetime.datetime.now()
    self.time_end = None
    self.today = datetime.date.today()
    self.download_in_cd = download_in_cd
    self.ok_downloaded = False
    self.bbfinder = ffnd.BBFIFileFinder(self.today)
    self._targetfilepath = targetfilepath
    # access property so that it's init'd | if it's initially None, it gets the default one
    _ = self.targetfilepath
    self._targetfolderpath = None
    # same | folderpath is derived from filepath and, if needed, created
    _ = self.targetfilepath

  @property
  def default_target_filename(self):
    return self.bbfinder.get_conventioned_input_commasep_html_filename()

  def mount_daybased_targetfilepath(self):
    """
    fs.os.dateprefixed_dirtree_finder.DatePrefixedOSFinder

    """
    bank3letter = 'bdb'
    dtprfxd_finder = bkfnd.BankOSFolderFileFinder(bank3letter, bkfnd.BankCat.REND_RESULTS_KEY)
    rentabdia_basefolderpath = dtprfxd_finder.find_l2yyyymm_folderpath_by_year_month_typ(
      self.today.year, self.today.month
    )
    today = datetime.date.today()
    l2folderpath = dtprfxd_finder.find_l2yyyymm_folderpath_by_year_month_typ(today.year, today.month)
    if l2folderpath is None:
      error_msg = (
          'Data or OS Error: from folder [{basefolderpath}] l2 subfolder returned None with'
          ' year {year} and month {month}'.
          format(basefolderpath=rentabdia_basefolderpath, year=today.year, month=today.month)
      )
      raise ValueError(error_msg)
    # use the interpolate constant at
    filepath = os.path.join(l2folderpath, self.default_target_filename)
    return filepath

  @property
  def targetfilepath(self):
    if self._targetfilepath is None:
      self._targetfilepath = self.mount_daybased_targetfilepath()
    return self._targetfilepath

  @property
  def target_folderpath(self):
    if self._targetfolderpath is None:
      try:
        self._targetfolderpath = os.path.split(self.targetfilepath)[0]
      except (IndexError, TypeError):
        return None
    if not os.path.isdir(self._targetfolderpath):
      # if folder does not exist, create it
      # an IOError or an OSError exception may happen here,
      # no need to include a try-block for, if it happens, program should halt anyway
      os.makedirs(self._targetfolderpath)
    return self._targetfolderpath

  @property
  def targetfile_already_exists(self):
    """
    If file already exists, download is avoided and corresponding message is presented
    """
    if os.path.isfile(self.targetfilepath):
      return True
    return False

  def download_in_currentdir(self):
    """
    This option calls os.system() issuing command "wget".
    The other one downloads to a specific folder, it uses lib requests.get()
    """
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
    This option downloads to a specific folder, it uses lib requests.get()
    The other one calls os.system() issuing command "wget".

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
    return True

  def download(self):
    if self.download_in_cd:
      self.download_in_currentdir()
      return
    ret_bool = self.download_to_targetdir()
    self.time_end = datetime.datetime.now()
    duration = self.time_end - self.time_start
    if ret_bool:
      print('Downloaded complete. Elapsed', duration)
    else:
      print('No download. Elapsed', duration)

  def __str__(self):
    outstr = """
    targetfilepath = {targetfilepath}
    downloaded = {ok_downloaded}
    """.format(targetfilepath=self.targetfilepath, ok_downloaded=self.ok_downloaded)
    return outstr


def download_n_gen_csv(pdate=None):
  """

  """
  today = datetime.date.today()
  if pdate is None:
    idate = today
  else:
    idate = pdate
  print("Step 1 is the downloading HTML, it can only happen for paramenter date being 'today'")
  if idate == today:
    print("Step 1 download HTML rendimentos no dia (original has comma decimal-place numbers)")
    downloader = BBRendDiaDownloader()
    downloader.download()
    print(downloader)
  print("Step 2 transform the comma decimal-place HTML above to a point separated one")
  input_filepath, output_filepath = commapoint.get_input_output_filepaths(idate)
  dec_to_point_er = commapoint.SingleFileConverter(input_filepath, output_filepath)
  dec_to_point_er.process()
  print("Step 3 convert the HTML with point decimal-place numbers to 3 csv's (for there are 3 data tables in it)")
  print('transf.WithPandasHtmlToCsvConverter.dispatch', idate)
  converter = transf.WithPandasHtmlToCsvConverter(idate)
  converter.process()


def download_n_gen_csv_thru_dates(datelist=()):
  for pdate in datelist:
    download_n_gen_csv(pdate)


def process_download_convert_transform():
  today = datetime.date.today()
  args = apdt.get_args()
  scrmsg = f"""downloadTabelaBBRendimentosDia.py
  CLI args given are:  {args}
    Obs: 
     1) if no parameter arg is given, 'today' {today} will default for the 3 operations
        (ie download/convert/transform)';
     2) the download operation only works for 'today', because the html data carries daily data;
        (the user can, without confusing, choose 'today', for example, when it's a Saturday or a Sunday,
        that download will refer to Friday);
     3) if another date than today is given, convert & transfom will look for same date html,
        ie, a download that happened before but was not yet processed (ie converted/transformed);
     4) the script does not process if a same date prefixed html or csv file already exists in folder;
        (if the user wants to reprocess it, she must delete the date prefixed files in the results folder); 
  """
  print(scrmsg)
  # 'today' is the last checked option, if nothing else is entered, making it true will dispatch it, like a default,
  # if other options than 'today' are chosen, no problem, program returns before getting to the 'today if'
  args.today = True
  dispatcher = apdt.Dispatcher(args, func=download_n_gen_csv_thru_dates)
  dispatcher.dispatch()


def adhoctest():
  pass


def process():
  """
  """
  process_download_convert_transform()


if __name__ == '__main__':
  """
  adhoctest()
  pass
  """
  process()
