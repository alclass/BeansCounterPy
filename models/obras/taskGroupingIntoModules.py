#!/usr/bin/env python3
"""
taskGroupingIntoModules
  This module creates a list of tasks giving weights to them.
  It's a sort of "dictionary" with some additional designed functions.
"""

dicttaskdata = {}
taskcode = 'laje'
taskdesc = "fazer laje acima da caixa d'água"
dayqty = 5
dicttaskdata[taskcode] = (taskdesc, dayqty)


class TaskOrganizer:

  def __init__(self, pdicttaskdata):
    self.totaldays = None
    self.dicttaskdata = pdicttaskdata

  def calc_days(self):
    self.totaldays = 0
    for task in self.dicttaskdata:
      ptuple = self.dicttaskdata[task]
      idayqty = ptuple[1]
      self.totaldays += idayqty
    return self.totaldays

  def __str__(self):
    outstr = ''
    for task in self.dicttaskdata:
      outstr += task + ' | ' + str(self.dicttaskdata[task]) + '\n'
    return outstr


def process():
  to = TaskOrganizer(dicttaskdata)
  print('total days', to.calc_days())
  print(to)


if __name__ == '__main__':
  process()
