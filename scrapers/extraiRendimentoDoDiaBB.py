#!/usr/bin/env python3
# --*-- encoding: utf8 --*--
import os, sys, time
import downloadTabelaRendimentosBB
# print sys.stdout.encoding

def ajustUtf8(builtinStr):
  utf8Str    = unicode(builtinStr, "utf-8")
  utf8StrOut = utf8Str.encode("utf-8")
  return utf8StrOut

def convertTextFromIso88591ToUtf8(builtinStr):
  iso88591Str = unicode(builtinStr, "ISO-8859-1")
  utf8Str     = iso88591Str.encode("utf-8")
  return utf8Str

nomesDosFundos = []
def getNomesDosFundosListFirstTime():
  nomesDosFundosFile = 'Nomes dos Fundos de Ações.txt'
  text = open(nomesDosFundosFile).read()
  # text = ajustUtf8(text)
  nomesDosFundos = text.split('\n')
  # do cleaning if need
  for nome in nomesDosFundos:
    if len(nome)==0:
      nomesDosFundos.remove(nome)
      continue
  return nomesDosFundos

def getNomesDosFundosList():
  global nomesDosFundos
  if len(nomesDosFundos) == 0:
    nomesDosFundos = getNomesDosFundosListFirstTime()
    if len(nomesDosFundos) == 0:
      print('A problem occurred len(nomesDosFundos) is 0.')
      sys.exit(0)
  return nomesDosFundos

def getNomesEValoresZeradosDosFundosDict(nomesDosFundos = getNomesDosFundosList()): # nomesDosFundos
  dictFundos = {}
  for nome in nomesDosFundos:
    dictFundos[nome] = 0
  return dictFundos

def extractColumn(date = downloadTabelaRendimentosBB.getDate()):
  '''
  returns a list of 2-D (nome, dayIndex) tuples (datum's)
  '''
  htmlPage = date + ' bb rendimento.htm'
  text = open(htmlPage).read()
  text = convertTextFromIso88591ToUtf8(text)
  twoColumns = []
  for nome in nomesDosFundos:
    datum = ()
    pos = text.find(nome)
    textChunk = text[pos:]
    pos = textChunk.find('</td>')
    if pos > -1:
      textChunk = textChunk[pos+1:]
      pos = textChunk.find('</td>')
      if pos > -1:
        phraseToClean = textChunk[pos-15:pos]
        pos = phraseToClean.find('>')
        if pos > -1:
          dayIndex = phraseToClean[pos+1:]
          print(' [extractColumn] ', nome, dayIndex)
          datum = nome, dayIndex
          twoColumns.append(datum)
  return twoColumns

if  __name__ == '__main__':
  datumList = extractColumn()
  for datum in datumList:
    for t in datum:
      print (t,)
    print()
