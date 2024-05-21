#!/usr/bin/env python3
"""
commands/ttc/coursemeta.py

This script attempts to read metadata information
  from TTC stored courses throughout a conventioned directory tree.

"""
COURSE_ID_PREFIX = '_ TTC '
COURSE_URL_INTERPOL = 'www.teachco.com/couse/%s'
MP3_PRODUCTION_PREFICES = [
  'mp3s_converted', 'mp3s_converted', 'mp3s_moved', 'mp3s_not_generated',
]


class CourseMetaInfo:

  def __init__(self):
    self.cid = None
    self.name = None
    self.prof = None
    self.inst = None
    self.year = None
    self.n_lectures = None
    self.min_per_lecture = 30
    self.has_guidebook = False
    self.has_mp3s = False
    self.mp3s_situation = None
    self.has_video = False
    self.karea_path = None  # eg "/Humanities/Social Science/Political Science"
    self.relpath = None  # eg "/_ TTC Humanities/_ TTC Social Science

  @property
  def url_by_cid(self):
    return COURSE_URL_INTERPOL % self.cid

  def introspect_mp3s_situation(self, folders):
    """
    mp3s may happen in four possible options:
      1 mp3s_converted => when they were converted (or extracted) from video
      2 mp3s_copied => when original mp3s were kept in storage and copied to the audio disk
      3 mp3s_moved => when original mp3s were not kept in storage and moved to the audio disk
      4 mp3s_not_generated => when mp3's were not generated due to a reason (mostly when course is too graphic)

    """
    for foldername in folders:
      for prefix in MP3_PRODUCTION_PREFICES:
        if foldername.startswith(prefix):
          self.mp3s_situation = prefix

  def __str__(self):
    outstr = f"""Course Meta Info: cid = {self.cid} | name = {self.name}
    prof = {self.prof} | inst = {self.inst}
    year = {self.year} | n_lectures = {self.n_lectures}
    min_per_lecture = {self.min_per_lecture}
    has_guidebook = {self.has_guidebook} | has_video = {self.has_video}
    url_by_cid = {self.url_by_cid}
    has_mp3s = {self.has_mp3s} | were_mp3s_converted = {self.were_mp3s_converted}
    karea_path = {self.karea_path}
    relpath = {self.relpath}"""
    return outstr


def derive_course_obj(curr_foldername):
  """
  cmi stands for Course Meta Info and its variable is an object
    instantiated from its class
  """
  expression = curr_foldername.lstrip('_ ')
  cmi = CourseMetaInfo()
  pos_ini_title = len(COURSE_ID_PREFIX)
  pos_ini_prof = curr_foldername.find('_i') + 2
  title = expression[pos_ini_title: pos_ini_prof]
  cmi.title = title.strip(' ')
  pos_ini_institut = curr_foldername.find('_f') + 2
  pos_fim_prof = pos_ini_institut - 4
  prof = expression[pos_ini_prof: pos_fim_prof]
  cmi.prof = prof.strip(' ')
  inst = expression[pos_ini_institut:]
  cmi.inst = inst.strip(' ')
  return cmi


def adhoctests():
  pass


def process():
  """

  """
  pass


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
