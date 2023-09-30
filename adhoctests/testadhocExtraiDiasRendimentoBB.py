#!/usr/bin/env python3
# --*-- encoding: utf8 --*--
import os, sys, time
import extraiRendimentoDoDiaBB

def printDatums(datumList):
  for datum in datumList:
    for t in datum:
      print (t,)
    print()

if  __name__ == '__main__':
  dates = ['2008-05-05', '2008-05-06', '2008-05-07']
  for date in dates:
    datumList = extraiRendimentoDoDiaBB.extractColumn(date)
    print ('='*40)
    print (date)
    print ('='*40)
    printDatums(datumList)
