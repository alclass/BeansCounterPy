#!/usr/bin/env python3
"""
commands/download/scrape_bb_rend_diario.py
  scrapes the HTML of BB rendimentos diários

https://scrapeops.io/python-web-scraping-playbook/best-python-html-parsing-libraries/

import requests
from lxml import html
url = 'https://quotes.toscrape.com/'
response = requests.get(url)
tree = html.fromstring(response.content)
quotes = tree.xpath('//div[@class="quote"]')
for quote in quotes:
    text = quote.xpath('.//span[@class="text"]/text()')[0]
    author = quote.xpath('.//small[@class="author"]/text()')[0]
    print(text)
    print(author)

"""
import os.path

# import
import pandas as pd
folderpath = (
  '/home/dados/Sw3/ProdProjSw/BeansCounterPy_PrdPrj/dados/bankdata/'
  '001 BDB bankdata/FI Extratos Mensais Ano a Ano BB OD/'
  'BB FI Rendimentos Diários htmls/'
)

# input_html_filepath = folderpath + '2023-10-26 BB rendimentos diários-conv.html'
input_html_filepath = folderpath + '2023-10-26 BB rendimentos diários.html'
print('Reading input_html_filepath', input_html_filepath)
df_list = pd.read_html(input_html_filepath)
# table RF DI
df_table = df_list[-3]
csv_output_filepath = folderpath + '2023-10-26 RFDI resultados dia.csv'
filename = os.path.split(csv_output_filepath)[-1]
print('Write csv_output', filename)
df_table.to_csv(csv_output_filepath)
# table RF LP
df_table = df_list[-2]
csv_output_filepath = folderpath + '2023-10-26 RFLP resultados dia.csv'
filename = os.path.split(csv_output_filepath)[-1]
print('Write csv_output', filename)
df_table.to_csv(csv_output_filepath)
# table RF Ações
df_table = df_list[-1]
csv_output_filepath = folderpath + '2023-10-26 Ações resultados dia.csv'
filename = os.path.split(csv_output_filepath)[-1]
print('Write csv_output', filename)
df_table.to_csv(csv_output_filepath)


class Scraper:

  def __init__(self, htmlfilepath):
    self.htmlfilepath = htmlfilepath

  def scrape(self):
    self.text = open(self.htmlfilepath).read()



  def __str__(self):
    outstr = """
    """
    return outstr


def adhoctests():
  pass


def process():
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctests()
