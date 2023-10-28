#!/usr/bin/env python3
"""
commands/download/transform_html_to_csv_w_pandas_for_bbfiresults.py
  scrapes the HTML of BB rendimentos diários

https://scrapeops.io/python-web-scraping-playbook/best-python-html-parsing-libraries/

import requests
from lxml import html

url = 'https://quotes.toscrape.com/'
response = requests.get(url)
tree = html.fromstring(response.content)
quotes = tree.xpath('//div[@class="quote"]'
for quote in quotes:
    text = quote.xpath('.//span[@class="text"]/text()'[0]
    author = quote.xpath('.//small[@class="author"]/text()'[0]
    print(text)
    print(author)

"""
# import argparse
pass
