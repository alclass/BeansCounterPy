#!/usr/bin/env python3
import sys
from commands.download import downloadTabelaBBRendimentosDia

datadir = '/home/grayacer/OurDocs/Banks OD/Banco do Brasil BB OD/Investimentos (Fundos etc) BB OD/Fundos de Investimentos BB OD/FI Extratos Mensais Ano a Ano BB OD/2023 FI Extratos Mensais BB'
datadir = '/home/grayacer/OurDocs/Banks OD/Banco do Brasil BB OD/Investimentos (Fundos etc) BB OD/Fundos de Investimentos BB OD/FI Extratos Mensais Ano a Ano BB OD/2023 FI Extratos Mensais BB'


class Extrator:

  def __int__(self, fundocod, fundonome, dayindex):
    self.fundocod = fundocod
    self.fundonome = fundonome
    self.builtinStr = None
    self.nomesDosFundos = []

  def ajust_utf8(self, builtinStr):
    utf8str = unicode(builtinStr, "utf-8")
    utf8strOut = utf8Str.encode("utf-8")
    return utf8StrOut

  def convert_text_from_iso88591_to_utf8(self):
    iso88591str = unicode(builtinStr, "ISO-8859-1")
    utf8str = iso88591Str.encode("utf-8")
    return utf8str

  def getNomesDosFundosListFirstTime(self, x):
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

  def get_fundonomes_list(self, x):
    global nomesDosFundos
    if len(nomesDosFundos) == 0:
      nomesDosFundos = getNomesDosFundosListFirstTime()
      if len(nomesDosFundos) == 0:
        print('A problem occurred len(nomesDosFundos) is 0.')
        sys.exit(0)
    return nomesDosFundos

  def get_fundonomes_e_valores_zerados(self): # nomesDosFundos
    fundonomes = getNomesDosFundosList()
    fundos_dict = {}
    for nome in fundonomes:
      fundos_dict[nome] = 0
    return fundos_dict

  def extract_column(self):
    '''
    returns a list of 2-D (nome, dayIndex) tuples (datum's)
    '''
    date = downloadTabelaRendimentosBB.getDate()
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

  def process(self):
    datumList = extractColumn()
    for datum in datumList:
      for t in datum:
        print (t,)
      print()



if  __name__ == '__main__':
  extractor = Extrator()
  extractor.process()
