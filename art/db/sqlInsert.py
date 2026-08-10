#!/usr/bin/env python3
# --*-- encoding: utf8 --*--
import os, sys, time
import extraiRendimentoDoDiaBB

sql = '''INSERT INTO `bizIn`.`pdntcmdls` (`codFundo` ,`nome` ,`codBanco`)
  VALUES (NULL , '%s', NULL);'''

def main():
  nomes = extraiRendimentoDoDiaBB.getNomesDosFundosList()
  for nome in nomes:
    print (sql %(nome))

if  __name__ == '__main__':
  main()
