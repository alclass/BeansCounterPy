#!/usr/bin/env python3
"""
commands/download/fibb_daily_results_html_to_csv_via_pandas_transform.py
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
