#!/usr/bin/env python3
"""
lookup_monthrange_convention_from_basedatafolder_on.py
  searches the datafolder for ini and fim refmonths
"""
import datetime
import os
import fs.os.osfunctions as osfs
import fs.os.oshilofunctions as hilo
import fs.datesetc.datefs as dtfs


def get_class_attrs(pclass):
  pdict = vars(pclass())
  plist = pdict.keys()
  plist = list(map(lambda attr: attr[1:] if attr.startswith('_') else attr, plist))
  return plist


class DatePrefixedOSEntriesFinder:
  """
  This class depends upon a convention in the way directories and datafiles and prefixed.
     More info on this in the __doc__ for __init__().

  The client caller/user must observe the following. For the time being,
     this class does not solve the many-extensions situation.
  However, a client caller may correct the extension (one for another) on its side
    if all datafiles are available with the two extensions.

  Example: if a datafile has a pdf extension and the caller looks for a version with a xml extension,
    for this to work, all files in this case must have the two formats (ie pdf and xml) in place.
  Then, the client caller just substitute one extension for the other (reenphasizing in the case the two exist!).
  """

  def __init__(self, rootdirpath=None):
    """
    This class is based on a "strong" convention.
    The convention is the following:
      1) starting from a basedir (rootdirpath), there are first level directories that should be prefixed by year+blank
         eg: "2022 FI Extratos Mensais" (notice the year and a blank starting its foldername)
      2) inside the first level directories, there are filenames that are prefixed by year+dash+month+blank
         eg: "2022-09 FI extrato.txt" (notice the year+dash+month+blank as prefix)

    A bit more graphically:

    [rootdirpath]--|
                   +--["2022 FI Extratos Mensais"]+--|
                                                     +--["2022-09 FI extrato.txt"]
                                                     +--["2022-11 FI extrato.txt"]
                   +--["2023 FI Extratos Mensais"]+--|
                                                     +--["2022-01 FI extrato.txt"]
                                                     +--["2022-05 FI extrato.pdf"]
                                                     +--["2022-05 FI extrato.xml"]
                                                     +--["2022-10 FI extrato.txt"]

    IMPORTANT:
      The file structure above is data for this system. If it's not in the convention above,
        this system will not work correctly. It may appoint it either as error or
        that it can't find the data that it needs or show empty results.
    """
    self.rootdirpath = rootdirpath
    self._firstlevel_year_folderpaths = None  # this list is stored right after __init__()
    self._firstlevel_year_foldernames = None  # this list is virtual, ie not stored in the object
    self._lesser_yearprefix_folderpath = None  # same to this
    self._lesser_yearprefix_foldername = None  # virtual, not stored, always retrieved on-the-fly
    self._greater_yearprefix_folderpath = None  # same to this
    self._greater_yearprefix_foldername = None  # same to this
    self._secondlevel_yearmonth_filepaths = None  # this list is stored right after __init__()
    self._secondlevel_yearmonth_filenames = None  # virtual, not stored, always retrieved on-the-fly
    self._lesser_yearmonth_filepath = None  # same to this and also to the following
    self._lesser_yearmonth_filename = None
    self._greater_yearmonth_filepath = None
    self._greater_yearmonth_filename = None
    self._refmonthdate_ini = None
    self._refmonthdate_fim = None
    # some attributes are filled in lazily, ie, upon their first access; others are just "virtual", recomputed each time

  @property
  def firstlevel_year_folderpaths(self):
    if self._firstlevel_year_folderpaths is None:
      self._firstlevel_year_folderpaths = []
      # foldernames = osfs.find_foldernames_from_path(self.rootdirpath)
      # self._firstlevel_year_folderpaths = sorted(map(lambda e: os.path.join(self.rootdirpath, e), foldernames))
      self._firstlevel_year_folderpaths = hilo.\
          find_l1folderpaths_all_years_from_basefolder_opt_substr(
            self.rootdirpath
          )
    return self._firstlevel_year_folderpaths

  @property
  def firstlevel_year_foldernames(self):
    """
    This property (firstlevel_year_foldernames) is recomputed each time, ie, not stored in object
      Its counterpart self._firstlevel_year_foldernames is always None and a marker for get_attrs()
    """
    if self.firstlevel_year_folderpaths is None or len(self.firstlevel_year_folderpaths) == 0:
      return []
    foldernames = sorted(map(lambda e: os.path.split(e)[-1], self.firstlevel_year_folderpaths))
    return foldernames

  def mount_firstlevel_yearprefix_folderpath_from_foldername(self, foldername):
    """
    Logic here: the first-level year-prefix foldernames are folders "above" (or below or inside) the rootdirpath.
    """
    if foldername is None:
      return None
    return os.path.join(self.rootdirpath, foldername)

  @property
  def lesser_yearprefix_folderpath(self):
    """
      property not stored in object, recomputed each time
    """
    return self.mount_firstlevel_yearprefix_folderpath_from_foldername(self.lesser_yearprefix_foldername)

  @property
  def lesser_yearprefix_foldername(self):
    """
      property not stored in object, recomputed each time
    """
    if len(self.firstlevel_year_foldernames) == 0:
      return None
    return self.firstlevel_year_foldernames[0]

  @property
  def greater_yearprefix_folderpath(self):
    """
      property not stored in object, recomputed each time
    """
    return self.mount_firstlevel_yearprefix_folderpath_from_foldername(self.greater_yearprefix_foldername)

  @property
  def greater_yearprefix_foldername(self):
    """
      property not stored in object, recomputed each time
    """
    if len(self.firstlevel_year_foldernames) == 0:
      return None
    return self.firstlevel_year_foldernames[-1]

  @property
  def secondlevel_yearmonth_filepaths(self):
    """
      property is stored in object, it will be filled in "lazily" at its first access
    """
    if self._secondlevel_yearmonth_filepaths is None:
      self._secondlevel_yearmonth_filepaths = []
      for firstlevel_year_folderpath in self.firstlevel_year_folderpaths:
        filenames = osfs.find_filenames_from_path(firstlevel_year_folderpath)
        yeardashmonthfilenames = hilo.find_names_that_start_with_a_yeardashmonth_via_if(filenames)
        for yeardashmonthfilename in yeardashmonthfilenames:
          ppath = os.path.join(firstlevel_year_folderpath, yeardashmonthfilename)
          self._secondlevel_yearmonth_filepaths.append(ppath)
      self._secondlevel_yearmonth_filepaths.sort()
    return self._secondlevel_yearmonth_filepaths

  @property
  def secondlevel_yearmonth_filenames(self):
    """
    This property (secondlevel_yearmonth_filenames) is recomputed each time, ie, not stored in object
      Its counterpart self._secondlevel_yearmonth_filenames is always None and a marker for get_attrs()
    """
    _secondlevel_yearmonth_filenames = []
    for secondlevel_yearmonth_filepath in self.secondlevel_yearmonth_filepaths:
      filename = os.path.split(secondlevel_yearmonth_filepath)[-1]
      _secondlevel_yearmonth_filenames.append(filename)
      _secondlevel_yearmonth_filenames.sort()
    return _secondlevel_yearmonth_filenames

  @property
  def total_files(self, p_dot_ext_or_dotless=None):
    """
    attr filepaths is chosen because this is stored on the object whereas filenames are recomputed at each call
    """
    if self.secondlevel_yearmonth_filepaths is None:
      return 0
    if p_dot_ext_or_dotless is None:
      return len(self.secondlevel_yearmonth_filepaths)
    dot_ext = p_dot_ext_or_dotless
    if not dot_ext.startswith('.'):
      dot_ext = '.' + dot_ext
    return len(list(filter(lambda e: e.endswith(dot_ext), self.secondlevel_yearmonth_filepaths)))

  def retrive_yearmonthfilepaths_in_yearfolder_by_refmonthdate_n_ext(self, refmonthdate, dot_ext=None):
    if refmonthdate is None:
      return []
    yearbasefolderpath = self.find_yearprefix_folderpath_by_year(refmonthdate)
    if yearbasefolderpath is None:
      return []
    filepaths = hilo.find_l2_or_l3_filenames_from_folderpath_w_year_month_opt_ext_substr(
      refmonthdate, yearbasefolderpath, dot_ext
    )
    return filepaths

  def retrive_yearmonthfilenames_in_yearfolder_by_refmonthdate_n_ext(self, refmonthdate, dot_ext=None):
    if refmonthdate is None:
      return []
    if type(refmonthdate) != datetime.date:
      refmonthdate = dtfs.make_date_with_day1_or_none(refmonthdate)
    year = refmonthdate.year
    yearbasefolderpath = self.find_yearprefix_folderpath_by_year(year)
    if yearbasefolderpath is None:
      return []
    filenames = hilo.find_l2_or_l3_filenames_from_folderpath_w_year_month_opt_ext_substr(
      refmonthdate, yearbasefolderpath, dot_ext
    )
    return filenames

  def mount_secondlevel_yearmonthprefix_filepath_from_filename(self, yearmonthprefix_filename):
    """
    Logic here: the second-level year-month-prefix filenames are filepaths "above" (or below or inside)
       a first-level year-prefix foldername.
    """
    pdate = hilo.extract_date_from_yearmonthprefix_str(yearmonthprefix_filename)
    if pdate is None:
      return None
    foldername = hilo.find_a_yearprefixedstr_from_strlist_by_year(pdate.year, self.firstlevel_year_foldernames)
    if foldername is None:
      return None
    yearprefix_folderpath = self.mount_firstlevel_yearprefix_folderpath_from_foldername(foldername)
    if yearprefix_folderpath is None:
      return None
    return os.path.join(yearprefix_folderpath, yearmonthprefix_filename)

  @property
  def lesser_secondlevel_yearmonth_filename(self):
    """
      property not stored in object, recomputed each time
    """
    if self.secondlevel_yearmonth_filenames is None and len(self.secondlevel_yearmonth_filenames) == 0:
      return None
    return self.secondlevel_yearmonth_filenames[0]

  @property
  def lesser_yearmonth_filename(self):
    """
      property not stored in object, recomputed each time
    """
    if self.secondlevel_yearmonth_filenames is None or len(self.secondlevel_yearmonth_filenames) == 0:
      return None
    return self.secondlevel_yearmonth_filenames[0]

  @property
  def lesser_yearmonth_filepath(self):
    """
      property not stored in object, recomputed each time
    """
    ppath = self.mount_secondlevel_yearmonthprefix_filepath_from_filename(self.lesser_secondlevel_yearmonth_filename)
    if ppath is None:
      return None
    return ppath

  @property
  def greater_yearmonth_filename(self):
    """
      property not stored in object, recomputed each time
    """
    if self.secondlevel_yearmonth_filenames is None or len(self.secondlevel_yearmonth_filenames) == 0:
      return None
    return self.secondlevel_yearmonth_filenames[-1]

  @property
  def greater_yearmonth_filepath(self):
    """
      property not stored in object, recomputed each time
    """
    ppath = self.mount_secondlevel_yearmonthprefix_filepath_from_filename(self.greater_yearmonth_filename)
    if ppath is None:
      return None
    return ppath

  @property
  def refmonthdate_ini(self):
    """
      property not stored in object, recomputed each time
    """
    _lesser_refmonthdate = hilo.extract_date_from_yearmonthprefix_str(self.lesser_yearmonth_filename)
    _lesser_refmonthdate = dtfs.make_date_with_day1_or_none(_lesser_refmonthdate)
    return _lesser_refmonthdate

  @property
  def refmonthdate_fim(self):
    """
      property not stored in object, recomputed each time
    """
    _greater_refmonthdate = hilo.extract_date_from_yearmonthprefix_str(self.greater_yearmonth_filename)
    _greater_refmonthdate = dtfs.make_date_with_day1_or_none(_greater_refmonthdate)
    return _greater_refmonthdate

  def find_yearprefix_foldername_by_year(self, year):
    if year is None:
      return year
    foldername = hilo.find_a_yearprefixedstr_from_strlist_by_year(year, self.firstlevel_year_foldernames)
    return foldername

  def find_yearprefix_folderpath_by_year(self, year):
    if year is None:
      return year
    foldername = self.find_yearprefix_foldername_by_year(year)
    if foldername is None:
      return None
    return self.mount_firstlevel_yearprefix_folderpath_from_foldername(foldername)

  def find_all_yearmonthfilepaths_by_year(self, year):
    folderpath = self.find_yearprefix_folderpath_by_year(year)
    if folderpath is None:
      return None
    str_re = r'\d{4}\-\d{2}\ '
    filenames = osfs.find_filenames_with_regexp_on_path(str_re, folderpath)
    filepaths = sorted(map(lambda e: os.path.join(folderpath, e), filenames))
    return filepaths

  def find_all_yearmonthfilenames_by_year(self, year):
    filepaths = self.find_all_yearmonthfilepaths_by_year(year)
    if filepaths is None:
      return None
    filenames = sorted(map(lambda e: os.path.split(e)[-1], filepaths))
    return filenames

  def find_yearmonthfilepath_by_yearmonth(self, refmonthdate):
    filename = self.find_yearmonthfilename_by_yearmonth(refmonthdate)
    if filename is None:
      return None
    folderpath = self.find_yearprefix_folderpath_by_year(refmonthdate.year)
    if folderpath is None:
      return None
    filepath = os.path.join(folderpath, filename)
    return filepath

  def find_yearmonthfilename_by_yearmonth(self, refmonthdate):
    refmonthdate = dtfs.return_date_or_recup_it_from_str(refmonthdate)
    if refmonthdate is None:
      return None
    filenames = self.find_all_yearmonthfilenames_by_year(refmonthdate.year)
    if filenames is None or len(filenames) == 0:
      return None
    for filename in filenames:
      try:
        if refmonthdate.year == int(filename[0:4]) and refmonthdate.month == int(filename[5:7]):
          return filename
      except (IndexError, ValueError):
        pass
    return None

  def gen_refmonths_within_daterange_or_wholeinterval(self, p_refmonthini=None, p_refmonthfim=None):
    refmonthdate_ini = self.refmonthdate_ini
    refmonthdate_fim = self.refmonthdate_fim
    p_refmonthini = dtfs.make_date_with_day1_or_none(p_refmonthini)
    p_refmonthfim = dtfs.make_date_with_day1_or_none(p_refmonthfim)
    if p_refmonthini is None or p_refmonthini < refmonthdate_ini or p_refmonthini > refmonthdate_fim:
       pass
    else:
      refmonthdate_ini = p_refmonthini
    if p_refmonthfim is None or p_refmonthfim > refmonthdate_fim or p_refmonthfim < refmonthdate_ini:
       pass
    else:
      refmonthdate_fim = p_refmonthfim
    if refmonthdate_ini > refmonthdate_fim:
      # probably params are inverted, back to the object's whole interval
      refmonthdate_ini = self.refmonthdate_ini
      refmonthdate_fim = self.refmonthdate_fim
    return dtfs.generate_monthrange(refmonthdate_ini, refmonthdate_fim)

  def gen_filepaths_within_daterange_or_wholeinterval(self, p_refmonthini=None, p_refmonthfim=None, dot_ext=None):
    for filenames in self.gen_filenames_within_daterange_or_wholeinterval(p_refmonthini, p_refmonthfim, dot_ext):
      # this is because there may be various extensions (eg pdf, xml etc) and various 'fundos'
      for filename in filenames:
        filepath = self.mount_secondlevel_yearmonthprefix_filepath_from_filename(filename)
        yield filepath
    return

  def gen_filenames_within_daterange_or_wholeinterval(self, p_refmonthini=None, p_refmonthfim=None, dot_ext=None):
    for refmonthdate in self.gen_refmonths_within_daterange_or_wholeinterval(p_refmonthini, p_refmonthfim):
      # previously self.find_yearmonthfilename_by_yearmonth(refmonthdate)
      filename = self.retrive_yearmonthfilenames_in_yearfolder_by_refmonthdate_n_ext(refmonthdate, dot_ext)
      if filename is None:
        continue
      yield filename
    return

  def gen_folderpaths_within_yearrange_or_wholeinterval(self, p_year_ini=None, p_year_fim=None):
    for foldername in self.gen_foldernames_within_yearrange_or_wholeinterval(p_year_ini, p_year_fim):
      if foldername is None:
        continue
      folderpath = os.path.join(self.rootdirpath, foldername)
      yield folderpath
    return

  def gen_foldernames_within_yearrange_or_wholeinterval(self, p_year_ini=None, p_year_fim=None):
    try:
      year_ini = int(p_year_ini)
      if year_ini < self.refmonthdate_ini.year:
        year_ini = self.refmonthdate_ini.year
    except (TypeError, ValueError):
      year_ini = self.refmonthdate_ini.year
    try:
      year_fim = int(p_year_fim)
      if year_fim > self.refmonthdate_fim.year:
        year_fim = self.refmonthdate_fim.year
      if year_ini > year_fim:
        year_ini = year_fim
    except (TypeError, ValueError):
      year_fim = self.refmonthdate_fim.year
    if year_ini == year_fim:
      foldername = self.find_yearprefix_foldername_by_year(year_ini)
      if foldername is not None:
        yield foldername
      return  # ends generator
    i_year = year_ini  # iterator for the while-loop below
    while i_year <= year_fim:
      foldername = self.find_yearprefix_foldername_by_year(i_year)
      yield foldername
      i_year += 1
    return

  def outdict(self):
    _ = self.rootdirpath  # for the IDE to avoid it not seeing method as 'instance-method', because the eval ofuscate it
    attrs = get_class_attrs(__class__)  # it adjusts the '_' for the properties to find for outdict()/__str__()
    pdict = {}
    for attr in attrs:
      pdict[attr] = eval('self.' + attr)
    return pdict

  def __str__(self):
    outstr = '<' + str(__class__) + '>\n'
    pdict = self.outdict()
    for fieldname in pdict:
      value = pdict[fieldname]
      line = '\t {fieldname} = {value}\n'.format(fieldname=fieldname, value=value)
      outstr += line
    return outstr


def adhoctest_yeardashmonth_regexp():
  print('='*40)
  print('adhoctest_yeardashmonth_regexp')
  print('='*40)
  s = '2023-09 test'
  result = hilo.yeardashmonthplusblank_re.match(s)
  seq = 1
  print(seq, '[', s, '] result => ', result)
  s = 'bla 2023-09 test'
  result = hilo.yeardashmonthplusblank_re.match(s)
  seq += 1
  print(seq, '[', s, '] result => ', result)
  s = '2023-09a test'
  result = hilo.yeardashmonthplusblank_re.match(s)
  seq += 1
  print(seq, '[', s, '] result => ', result)
  print('end adhoctest')


def adhoctest2():
  print('='*40)
  print('adhoctest2')
  print('='*40)
  v = 'Worksheets 2018 Ext Men FI BB'
  matchobj = hilo.yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)
  v = '2018-01 Ext Men FI BB'
  matchobj = hilo.yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)
  v = ' 2018-01 Ext Men FI BB'
  matchobj = hilo.yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)
  v = 'fundo_report_example.txt'
  matchobj = hilo.yeardashmonthplusblank_re.match(v)
  print('text', v, '=>', matchobj)


def adhoctest3():
  """
  Notice that to avoid "circular imports" this module cannot import models.banks.banksgeneral
    (because that imports this),
    so the adhoctest here will have variable bb_fi_rootfolder_abspath hardcoded
  If this path changes, for running this adhoctest(), variable must be updated too
    bb_fi_rootfolder_abspath = models.banks.banksgeneral.BANK.get_bank_fi_folderpath_by_its3letter('bdb')
  """
  dateprefixfinder = DatePrefixedOSEntriesFinder(bb_fi_rootfolder_abspath)
  print('='*40)
  print('adhoctest')
  print('='*40)
  print(dateprefixfinder)
  print('dateprefixfinder.lesser_yearmonthprefix_folderpath()')


def adhoctest():
  """
  for i, ref in enumerate(o.gen_refmonth_ini_n_fim_range()):
    print(i, ref)
  o = DatePrefixedOSEntriesFinder(rootdirpath=bb_fi_rootfolder_abspath)
  print(o)
  year = 2022
  result = o.find_all_yearmonthfilepaths_by_year(year)
  print('o.find_all_yearmonth_filepaths_by_year()', year, '=>', result
  filenames = o.find_all_yearmonthfilenames_by_year(year)
  print('o.find_all_yearmonthfilenames_by_year(year)', year, '=>', filenames
  print(len(o.secondlevel_yearmonth_filenames))
  filepaths = o.gen_filenames_within_daterange_or_wholeinterval('2022-07', '2023-04')
  for i, fp in enumerate(filepaths):
    print(i+1, fp)
  """
  o = DatePrefixedOSEntriesFinder(rootdirpath=cef_fi_rootfolder_abspath)
  print(o)
  print('='*40, 'foldernames')
  for foldername in o.gen_foldernames_within_yearrange_or_wholeinterval():
    print(foldername)
  print('='*40, 'folderpaths')
  for folderpath in o.gen_folderpaths_within_yearrange_or_wholeinterval():
    print(folderpath)


def process():
  pass


bb_fi_rootfolder_abspath = (
    '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
    '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD'
)
cef_fi_rootfolder_abspath = (
    '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
    '104 CEF bankdata/FI Extratos Mensais Ano a Ano CEF OD'
)

if __name__ == '__main__':
  """
  process()
  adhoctest_yeardashmonth_regexp()
  adhoctest2()
  adhoctest3()
  """
  adhoctest()
