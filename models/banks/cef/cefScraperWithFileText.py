#!/usr/bin/env python3
""""
cefScraperWithFileText.py

saldo anterior & cotas
  regexp => dd/dd/yyyy SALDO ANTERIOR
  restr = "(\d{2}/\d{2}/\d{4}).SALDO.ANTERIOR.+"
saldo atual & cotas
  regexp => dd/dd/yyyy SALDO ATUAL
"""

class CEFExtractScraperWithXml:

def process():
  withinfundo_scraper = CEFExtractScraperWithXml()
  withinfundo_scraper.process()
  print(withinfundo_scraper)


if __name__ == '__main__':
  process()
