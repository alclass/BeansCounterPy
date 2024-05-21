#!/usr/bin/env python3
"""
commands/ttc/walk_updir_find_ttc_courses.py

This script attempts to read metadata information
  from TTC stored courses throughout a conventioned directory tree.

"""
# import argparse
# import datetime
# import fs.datesetc.datehilofs as hilodt
import os
import sys
import commands.ttc.coursemeta as cmet
COURSE_ID_PREFIX = cmet.COURSE_ID_PREFIX
COURSE_URL_INTERPOL = cmet.COURSE_URL_INTERPOL


class UpDirGrabber:

  def __init__(self, root_abspath=None):
    self.root_abspath = root_abspath
    self.courses = []
    self.n_courses = 0
    self.treat_root_abspath()

  def treat_root_abspath(self):
    if self.root_abspath is None:
      self.root_abspath = os.getcwd()
      return
    if not os.path.isdir(self.root_abspath):
      errmsg = f"Directory [{self.root_abspath}] doesn't not exist."
      raise OSError(errmsg)

  def grabber_course(self, curr_abspath, dirs, files, course_obj):
    self.n_courses += 1
    print(self.n_courses, course_obj)
    print(curr_abspath)
    print(dirs)
    print(files)

  def introspect_folder(self, curr_abspath, dirs, files):
    curr_foldername = curr_abspath.split(os.sep)[-1]
    if curr_foldername.startswith(COURSE_ID_PREFIX):
      course_obj = cmet.derive_course_obj(curr_foldername)
      self.grabber_course(curr_abspath, dirs, files, course_obj)

  def walk_updir_grabbing_courses(self):
    for curr_abspath, dirs, files in os.walk(self.root_abspath):
      self.introspect_folder(curr_abspath, dirs, files)

  def process(self):
    self.walk_updir_grabbing_courses()


def adhoctests():
  pass


def process():
  """

  """
  start_abspath = sys.argv[1]
  updirgrabber = UpDirGrabber(start_abspath)
  updirgrabber.process()


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
